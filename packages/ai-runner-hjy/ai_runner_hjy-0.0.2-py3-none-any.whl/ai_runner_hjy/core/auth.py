from __future__ import annotations

import os
import hmac
import hashlib
import time
import json
import secrets
from typing import Dict, Any, Optional, Tuple

from .crypto_utils import decrypt_api_key, encrypt_api_key
from .db import get_db_connection
from .logs import logger


# ------------------ Client/Server shared helpers ------------------

def hmac_headers(access_key_id: str, secret_key: str, payload: Dict[str, Any], *, nonce: Optional[str] = None) -> Dict[str, str]:
    """Return headers for signed request (client side helper).

    Canonical string: f"{timestamp}\n{nonce}\n{compact_json}"
    Signature: sha256.hexdigest()
    """
    ts = str(int(time.time()))
    nz = nonce or (secrets.token_hex(8))
    compact = json.dumps(payload or {}, ensure_ascii=False, separators=(",", ":"))
    sig = hmac.new(secret_key.encode("utf-8"), f"{ts}\n{nz}\n{compact}".encode("utf-8"), hashlib.sha256).hexdigest()
    return {
        "X-AK": access_key_id,
        "X-Nonce": nz,
        "X-Timestamp": ts,
        "X-Signature": sig,
    }


def generate_project_credential(project_name: str) -> Dict[str, str]:
    """Create or rotate an AK/SK for a project; returns plain AK/SK once.

    - Ensures project exists in ai_project_v2
    - Inserts/updates ai_project_credential_v2(project_id, access_key_id, secret_encrypted)
    - Secret is AES-GCM encrypted at rest; plain SK is returned once for display
    """
    if not project_name:
        raise ValueError("project_name is required")

    ak = f"ak_{secrets.token_urlsafe(10)}"
    sk_plain = f"sk_{secrets.token_urlsafe(24)}"
    enc_blob = encrypt_api_key(sk_plain, os.environ.get("AI_PEPPER", ""))

    with get_db_connection() as conn:
        cur = conn.cursor()
        # ensure project row exists
        cur.execute(
            "INSERT INTO ai_project_v2(name,status) VALUES(%s,'active') ON DUPLICATE KEY UPDATE status='active'",
            (project_name,)
        )
        cur.execute("SELECT id FROM ai_project_v2 WHERE name=%s LIMIT 1", (project_name,))
        pid = int(cur.fetchone()[0])

        # upsert credential for this ak
        cur.execute(
            """
            INSERT INTO ai_project_credential_v2(project_id, access_key_id, secret_encrypted, status)
            VALUES(%s, %s, %s, 'active')
            ON DUPLICATE KEY UPDATE secret_encrypted=VALUES(secret_encrypted), status='active'
            """,
            (pid, ak, json.dumps(enc_blob, ensure_ascii=False))
        )
        conn.commit()

    return {"access_key_id": ak, "secret_key": sk_plain}


# ------------------ Existing low-level helpers ------------------

def hmac_sign(secret: str, method: str, path: str, timestamp: str, body_bytes: bytes) -> str:
    payload = method.upper() + "\n" + path + "\n" + timestamp + "\n" + hashlib.sha256(body_bytes).hexdigest()
    sig = hmac.new(secret.encode("utf-8"), payload.encode("utf-8"), hashlib.sha256).digest()
    import base64
    return base64.b64encode(sig).decode("utf-8")


def verify_hmac(signature: str, secret: str, method: str, path: str, timestamp: str, body_bytes: bytes, *, skew_sec: int = 300) -> Optional[str]:
    try:
        ts = int(timestamp)
    except Exception:
        return "INVALID_TIMESTAMP"

    now = int(time.time())
    if abs(now - ts) > skew_sec:
        return "TIMESTAMP_SKEW"

    expect = hmac_sign(secret, method, path, timestamp, body_bytes)
    try:
        import base64
        given = base64.b64decode(signature.encode("utf-8"))
        exp = base64.b64decode(expect.encode("utf-8"))
    except Exception:
        return "INVALID_SIGNATURE_FORMAT"

    if hmac.compare_digest(given, exp):
        return None

    try:
        _obj = json.loads(body_bytes.decode("utf-8")) if body_bytes else None
        if _obj is not None:
            compact = json.dumps(_obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            expect2 = hmac_sign(secret, method, path, timestamp, compact)
            import base64
            exp2 = base64.b64decode(expect2.encode("utf-8"))
            if hmac.compare_digest(given, exp2):
                return None
            default_dump = json.dumps(_obj, ensure_ascii=False).encode("utf-8")
            expect3 = hmac_sign(secret, method, path, timestamp, default_dump)
            exp3 = base64.b64decode(expect3.encode("utf-8"))
            if hmac.compare_digest(given, exp3):
                return None
    except Exception:
        pass

    return "SIGNATURE_MISMATCH"


# ------------------ Dev mode and internal testing support ------------------

def is_dev_mode() -> bool:
    """检查是否启用内测模式"""
    return os.environ.get("DEV_MODE", "false").lower() == "true"

def get_dev_key() -> Optional[str]:
    """获取dev key"""
    return os.environ.get("DEV_KEY")

def is_internal_ip(client_ip: str) -> bool:
    """检查是否为内网IP"""
    if not client_ip:
        return False
    
    # 内网IP段
    internal_ranges = [
        "127.0.0.0/8",      # localhost
        "10.0.0.0/8",       # 10.0.0.0 - 10.255.255.255
        "172.16.0.0/12",    # 172.16.0.0 - 172.31.255.255
        "192.168.0.0/16",   # 192.168.0.0 - 192.168.255.255
    ]
    
    try:
        import ipaddress
        client_addr = ipaddress.ip_address(client_ip)
        for range_str in internal_ranges:
            if client_addr in ipaddress.ip_network(range_str):
                return True
        return False
    except Exception:
        # 如果IP解析失败，默认不允许
        return False

def verify_dev_key(access_key: str, client_ip: str) -> bool:
    """验证dev key"""
    if not is_dev_mode():
        return False
    
    dev_key = get_dev_key()
    if not dev_key:
        logger.warning("Dev mode enabled but DEV_KEY not set")
        return False
    
    # 检查IP限制
    if os.environ.get("DEV_IP_RESTRICT", "true").lower() == "true":
        if not is_internal_ip(client_ip):
            logger.warning(f"Dev key access denied from external IP: {client_ip}")
            return False
    
    # 验证dev key
    return access_key == dev_key

def verify_user_key_signature(
    access_key: str,
    nonce: str,
    timestamp: str,
    signature: str,
    request_body: Dict[str, Any]
) -> bool:
    """验证用户Key的HMAC签名"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    """
                    SELECT k.secret_encrypted, k.allow_ips_json, u.name as user_name
                    FROM ai_user_key k
                    JOIN ai_user u ON k.user_id = u.id
                    WHERE k.access_key_id = %s AND k.status = 'active'
                    LIMIT 1
                    """,
                    (access_key,)
                )
                row = cursor.fetchone()
    except Exception as e:
        logger.error(f"Database error during user key lookup: {e}")
        return False

    if not row:
        logger.warning(f"User key verification failed: access key '{access_key}' not found or not active.")
        return False

    # 解密密钥
    enc = row["secret_encrypted"]
    if isinstance(enc, str):
        enc = json.loads(enc)

    pepper = os.getenv("AI_PEPPER")
    if not pepper:
        logger.error("User key verification failed: AI_PEPPER is not set.")
        return False

    try:
        secret_key = decrypt_api_key(enc, pepper)
    except Exception as e:
        logger.error(f"Failed to decrypt user secret key for AK {access_key}: {e}")
        return False

    # 构建规范字符串
    compact_json = json.dumps(request_body, ensure_ascii=False, separators=(",", ":"))
    canonical = f"{timestamp}\n{nonce}\n{compact_json}"
    expected = hmac.new(secret_key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()
    
    return hmac.compare_digest(expected, signature)

async def verify_hmac_signature_enhanced(
    access_key: Optional[str],
    nonce: Optional[str],
    timestamp: Optional[str],
    signature_from_header: Optional[str],
    request_body: Dict[str, Any],
    client_ip: str = "127.0.0.1"
) -> Tuple[bool, str, Optional[str]]:
    """
    增强的HMAC签名验证，支持dev key和用户key
    
    Returns:
        (verified, auth_type, user_info)
        - verified: 是否验证通过
        - auth_type: 认证类型 ('dev', 'user', 'project', 'none')
        - user_info: 用户信息 (仅用户key时返回)
    """
    if not all([access_key, nonce, timestamp, signature_from_header]):
        logger.warning("HMAC verification failed: missing required headers.")
        return False, "none", None

    # 1. 检查dev key
    if verify_dev_key(access_key, client_ip):
        logger.info(f"Dev key authentication successful from {client_ip}")
        return True, "dev", None

    # 2. 检查用户key
    if verify_user_key_signature(access_key, nonce, timestamp, signature_from_header, request_body):
        try:
            with get_db_connection() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT u.name, u.email, k.id as key_id
                        FROM ai_user_key k
                        JOIN ai_user u ON k.user_id = u.id
                        WHERE k.access_key_id = %s AND k.status = 'active'
                        LIMIT 1
                        """,
                        (access_key,)
                    )
                    row = cursor.fetchone()
                    if row:
                        user_info = {
                            "user_name": row["name"],
                            "user_email": row["email"],
                            "key_id": row["key_id"]
                        }
                        logger.info(f"User key authentication successful: {row['name']}")
                        return True, "user", user_info
        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
        
        return True, "user", None

    # 3. 检查项目凭证（原有逻辑）
    try:
        with get_db_connection() as conn:
            with conn.cursor(dictionary=True) as cursor:
                cursor.execute(
                    "SELECT pc.secret_encrypted FROM ai_project_credential_v2 pc JOIN ai_project_v2 p ON p.id=pc.project_id WHERE pc.access_key_id=%s AND pc.status='active' LIMIT 1",
                    (access_key,)
                )
                row = cursor.fetchone()
    except Exception as e:
        logger.error(f"Database error during project credential lookup: {e}")
        return False, "none", None

    if not row:
        logger.warning(f"Project credential verification failed: access key '{access_key}' not found or not active.")
        return False, "none", None

    enc = row["secret_encrypted"] if isinstance(row, dict) else row[0]
    if isinstance(enc, str):
        enc = json.loads(enc)

    pepper = os.getenv("AI_PEPPER")
    if not pepper:
        logger.error("Project credential verification failed: AI_PEPPER is not set.")
        return False, "none", None

    try:
        secret_key = decrypt_api_key(enc, pepper)
    except Exception as e:
        logger.error(f"Failed to decrypt project secret key for AK {access_key}: {e}")
        return False, "none", None

    # build canonical string safely
    compact_json = json.dumps(request_body, ensure_ascii=False, separators=(",", ":"))
    canonical = f"{timestamp}\n{nonce}\n{compact_json}"
    expected = hmac.new(secret_key.encode("utf-8"), canonical.encode("utf-8"), hashlib.sha256).hexdigest()
    
    if hmac.compare_digest(expected, signature_from_header):
        logger.info(f"Project credential authentication successful: {access_key}")
        return True, "project", None
    
    return False, "none", None


# 向后兼容的原有函数
async def verify_hmac_signature(
    access_key: Optional[str],
    nonce: Optional[str],
    timestamp: Optional[str],
    signature_from_header: Optional[str],
    request_body: Dict[str, Any]
) -> bool:
    """向后兼容的HMAC签名验证函数"""
    verified, auth_type, _ = await verify_hmac_signature_enhanced(
        access_key, nonce, timestamp, signature_from_header, request_body
    )
    return verified

