from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional, Dict, Tuple

import oss2
from oss2.exceptions import OssError

from .db import get_db_connection
from .logs import logger

import time

import oss2


@dataclass
class OssConfig:
    access_key_id: str
    access_key_secret: str
    bucket_name: str
    endpoint: str
    project_name: str


def load_oss_config() -> OssConfig:
    return OssConfig(
        access_key_id=os.environ["OSS_ACCESS_KEY_ID"],
        access_key_secret=os.environ["OSS_ACCESS_KEY_SECRET"],
        bucket_name=os.environ["OSS_BUCKET_NAME"],
        endpoint=os.environ["OSS_ENDPOINT"],
        project_name=os.environ.get("PROJECT_NAME", "project"),
    )


def _hash8(data: bytes) -> str:
    return hashlib.md5(data).hexdigest()[:8]


def _object_key(project: str, route_key: str, suffix: str) -> str:
    now = datetime.utcnow()
    return f"{project}/logs/{now:%Y%m%d}/{now:%H}/{route_key}_{int(now.timestamp())}_{suffix}.json"


def put_public_json(route_key: str, obj: Any, *, cfg: Optional[OssConfig] = None) -> str:
    cfg = cfg or load_oss_config()
    data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
    key = _object_key(cfg.project_name, route_key, _hash8(data))
    auth = oss2.Auth(cfg.access_key_id, cfg.access_key_secret)
    bucket = oss2.Bucket(auth, cfg.endpoint, cfg.bucket_name)
    bucket.put_object(key, data, headers={"x-oss-object-acl": "public-read"})
    base = os.environ.get("OSS_PUBLIC_BASE_URL")
    if base:
        return f"{base.rstrip('/')}/{key}"
    return f"https://{cfg.bucket_name}.{cfg.endpoint.replace('https://','').replace('http://','')}/{key}"


def get_oss_bucket() -> Optional[oss2.Bucket]:
    cfg = load_oss_config()
    auth = oss2.Auth(cfg.access_key_id, cfg.access_key_secret)
    try:
        bucket = oss2.Bucket(auth, cfg.endpoint, cfg.bucket_name)
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


def upload_file(
    local_file_path: str, object_name: Optional[str] = None
) -> Optional[str]:
    """
    Uploads a local file to OSS and returns its public URL.
    This is a core function of the ai-runner-hjy package.
    """
    if not os.path.exists(local_file_path):
        logger.error(f"Local file not found: {local_file_path}")
        return None

    bucket = get_oss_bucket()
    if not bucket:
        return None

    if not object_name:
        # Create a default object name if not provided
        file_name = os.path.basename(local_file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = os.getenv("PROJECT_NAME", "unknown_project")
        object_name = f"{project_name}/uploads/{timestamp}_{file_name}"

    try:
        # 1. Upload to OSS
        bucket.put_object_from_file(object_name, local_file_path)

        # 2. Get file metadata
        file_size = os.path.getsize(local_file_path)
        original_filename = os.path.basename(local_file_path)
        project_name = os.getenv("PROJECT_NAME")
        file_extension = os.path.splitext(original_filename)[1]
        # A simple way to get MIME type, can be improved
        import mimetypes
        file_type = mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

        # 3. Save record to database
        with get_db_connection(database=os.getenv("OSS_DATABASE")) as conn:
            with conn.cursor() as cursor:
                table_name = os.getenv("OSS_TABLENAME")
                sql = f"""
                    INSERT INTO {table_name}
                    (project_name, original_filename, oss_object_name, file_size, file_type, file_extension, file_acl)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                # Assuming 'public-read' for now, can be parameterized later
                cursor.execute(sql, (project_name, original_filename, object_name, file_size, file_type, file_extension, 'public-read'))
            conn.commit()
        
        logger.info(f"Successfully saved OSS record to database for {object_name}")

        # 4. Return public URL
        public_url_base = os.getenv("OSS_PUBLIC_BASE_URL")
        if public_url_base:
            return f"{public_url_base}/{object_name}"

        # Fallback to creating a signed URL if no public base URL is set
        # Note: This is a fallback and the primary method should be a public URL base
        # for public assets.
        signed_url = bucket.sign_url("GET", object_name, 3600)  # 1 hour expiry
        logger.info(
            f"Successfully uploaded {local_file_path} to {object_name}. "
            f"Generated signed URL (fallback): {signed_url}"
        )
        return signed_url

    except OssError as e:
        logger.error(f"OSS upload failed for {local_file_path}: {e}")
        return None
    except Exception as e:
        logger.error(f"An error occurred during file upload and db logging: {e}")
        # Here you might want to add logic to delete the uploaded file from OSS
        # to maintain consistency, but for now, we just log the error.
        return None

