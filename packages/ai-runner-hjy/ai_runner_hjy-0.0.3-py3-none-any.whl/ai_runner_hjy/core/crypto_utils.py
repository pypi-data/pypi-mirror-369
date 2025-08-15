import base64
from typing import Any, Dict
import os
import json

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

DEFAULT_KDF_ITERATIONS = 200_000
ALG = "AES-256-GCM"
VERSION = 1
FIXED_PASSWORD = b"fixed-input"


def _derive_key(pepper: str, random_salt: bytes, iterations: int = DEFAULT_KDF_ITERATIONS) -> bytes:
    if not pepper:
        raise ValueError("pepper is required to derive key")
    combined_salt = pepper.encode("utf-8") + random_salt
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=combined_salt,
        iterations=iterations,
        backend=default_backend(),
    )
    return kdf.derive(FIXED_PASSWORD)


def decrypt_api_key(blob: Dict[str, Any], pepper: str) -> str:
    if not pepper:
        raise ValueError("pepper is required")

    salt = base64.b64decode(blob["salt"])  # type: ignore[index]
    nonce = base64.b64decode(blob["nonce"])  # type: ignore[index]
    ct_raw = base64.b64decode(blob["ct"])  # type: ignore[index]
    tag_b64 = blob.get("tag")
    if tag_b64:
        tag = base64.b64decode(tag_b64)
        ct = ct_raw + tag
    else:
        ct = ct_raw
    iterations = int(blob.get("iter", DEFAULT_KDF_ITERATIONS))

    key = _derive_key(pepper, salt, iterations)
    aesgcm = AESGCM(key)
    pt = aesgcm.decrypt(nonce, ct, None)
    return pt.decode("utf-8")


def encrypt_api_key(plain: str, pepper: str, iterations: int = DEFAULT_KDF_ITERATIONS) -> Dict[str, Any]:
    if not pepper:
        raise ValueError("pepper is required")
    if not isinstance(plain, str) or not plain:
        raise ValueError("plain api key required")

    import os, base64
    salt = os.urandom(16)
    nonce = os.urandom(12)
    key = _derive_key(pepper, salt, iterations)
    aesgcm = AESGCM(key)
    ct = aesgcm.encrypt(nonce, plain.encode("utf-8"), None)
    return {
        "v": VERSION,
        "alg": ALG,
        "iter": iterations,
        "salt": base64.b64encode(salt).decode(),
        "nonce": base64.b64encode(nonce).decode(),
        "ct": base64.b64encode(ct).decode(),
    }

