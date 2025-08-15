from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime
from typing import Any, Optional, Dict, Tuple

import oss2
from oss2.exceptions import OssError

from .config import AppConfig, get_config, logger
from .db import get_db_connection

import time
import mimetypes
from io import BytesIO

import oss2


def _hash8(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:8]


def _object_key(project: str, route_key: str, suffix: str) -> str:
    now = datetime.utcnow()
    return f"{project}/logs/{now:%Y%m%d}/{now:%H}/{route_key}_{int(now.timestamp())}_{suffix}.json"


def _generate_upload_object_name(project_name: str, original_filename: str) -> str:
    """Generates a unique object name for file uploads."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    # Sanitize filename slightly, though OSS can handle most chars
    safe_filename = "".join(c for c in original_filename if c.isalnum() or c in '._-')
    return f"{project_name}/uploads/{timestamp}_{safe_filename}"


def get_signed_url(object_name: str, ttl_seconds: int = 3600, config: Optional[AppConfig] = None) -> Optional[str]:
    """Generates a signed URL for a private OSS object."""
    bucket = get_oss_bucket(config=config)
    if not bucket:
        return None
    try:
        signed_url = bucket.sign_url("GET", object_name, ttl_seconds)
        logger.info(f"Generated signed URL for {object_name} with TTL {ttl_seconds}s.")
        return signed_url
    except OssError as e:
        logger.error(f"Failed to sign URL for {object_name}: {e}")
        return None


def put_public_json(route_key: str, obj: Any, *, config: Optional[AppConfig] = None) -> str:
    config = config or get_config()
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    key = _object_key(config.project_name, route_key, _hash8(data))
    auth = oss2.Auth(config.oss_access_key_id, config.oss_access_key_secret)
    bucket = oss2.Bucket(auth, config.oss_endpoint, config.oss_bucket_name)
    bucket.put_object(key, data, headers={"x-oss-object-acl": "public-read"})
    base = os.environ.get("OSS_PUBLIC_BASE_URL")
    if base:
        return f"{base.rstrip('/')}/{key}"
    if config.oss_endpoint:
        return f"https://{config.oss_bucket_name}.{config.oss_endpoint.replace('https://','').replace('http://','')}/{key}"
    return f"https://{config.oss_bucket_name}.aliyuncs.com/{key}"


def get_oss_bucket(config: Optional[AppConfig] = None) -> Optional[oss2.Bucket]:
    config = config or get_config()
    auth = oss2.Auth(config.oss_access_key_id, config.oss_access_key_secret)
    try:
        bucket = oss2.Bucket(auth, config.oss_endpoint, config.oss_bucket_name)
        return bucket
    except OssError as e:
        logger.error(f"Failed to get OSS bucket: {e}")
        return None


def put_public_json_with_bucket(
    bucket: oss2.Bucket, object_name: str, data: Dict
) -> Optional[str]:
    try:
        bucket.put_object(object_name, json.dumps(data, ensure_ascii=False), headers={"x-oss-object-acl": "public-read"})
        return f"https://{bucket.bucket_name}.{bucket.endpoint.replace('https://','').replace('http://','')}/{object_name}"
    except OssError as e:
        logger.error(f"OSS put_object failed for {object_name}: {e}")
        return None


def _upload_and_log(
    bucket: oss2.Bucket,
    object_name: str,
    file_bytes: bytes,
    original_filename: str,
    acl: str,
    config: AppConfig,
) -> Optional[Dict[str, Any]]:
    conn = None
    try:
        # Wrap bytes in BytesIO to make it a file-like object
        file_like_object = BytesIO(file_bytes)
        
        # Upload the object from the file-like object
        result = bucket.put_object(object_name, file_like_object)

        if result.status != 200:
            logger.error(f"OSS upload failed for {object_name} with status {result.status}")
            return None

        file_size = len(file_bytes)
        file_type = mimetypes.guess_type(original_filename)[0] or "application/octet-stream"
        
        db_name = config.oss_database
        table_name = config.oss_tablename

        if not db_name or not table_name:
            logger.error("OSS_DATABASE and OSS_TABLENAME must be set in config.")
            raise ValueError("OSS database configuration is missing.")

        conn = get_db_connection(config=config, db_name=db_name)
        if not conn:
            logger.error("Failed to get DB connection for logging OSS upload.")
            return {"object_name": object_name, "size": file_size, "db_log_status": "failed"}

        cursor = conn.cursor()
        
        insert_sql = f"""
        INSERT INTO {table_name}
        (project_name, original_filename, oss_object_name, file_size, file_type, file_acl)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        project_name = config.project_name
        cursor.execute(
            insert_sql,
            (project_name, original_filename, object_name, file_size, file_type, acl),
        )
        conn.commit()
        logger.info(f"Successfully uploaded and logged {object_name} to DB.")
        
        return {"object_name": object_name, "size": file_size, "db_log_status": "success"}

    except Exception as e:
        logger.error(f"Error during OSS upload or DB logging for {original_filename}: {e}", exc_info=True)
        # Rollback in case of failure during commit
        if conn:
            conn.rollback()
        return None
    finally:
        # Ensure the connection is closed
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


def upload_file_from_bytes(
    file_bytes: bytes, original_filename: str, object_name: Optional[str] = None, acl: str = 'private', config: Optional[AppConfig] = None
) -> Optional[Dict[str, Any]]:
    """
    Uploads file bytes to OSS and returns a dictionary with upload details.
    """
    config = config or get_config()
    bucket = get_oss_bucket(config=config)
    if not bucket:
        return None

    project_name = config.project_name
    obj_name = object_name or _generate_upload_object_name(project_name, original_filename)

    return _upload_and_log(bucket, obj_name, file_bytes, original_filename, acl=acl, config=config)


def upload_file(
    local_file_path: str, object_name: Optional[str] = None, config: Optional[AppConfig] = None
) -> Optional[Dict[str, Any]]:
    """
    Uploads a local file to OSS and returns a dictionary with upload details.
    This function is refactored to use the bytes-based upload logic.
    """
    if not os.path.exists(local_file_path):
        logger.error(f"Local file not found: {local_file_path}")
        return None

    try:
        with open(local_file_path, "rb") as f:
            file_bytes = f.read()

        original_filename = os.path.basename(local_file_path)
        # Assuming private ACL for general file uploads unless specified otherwise.
        return upload_file_from_bytes(file_bytes, original_filename, object_name, acl='private', config=config)

    except IOError as e:
        logger.error(f"Failed to read local file {local_file_path}: {e}")
        return None

