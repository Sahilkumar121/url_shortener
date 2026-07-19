from datetime import datetime, timezone, timedelta

import jwt
import hashlib
from pwdlib import PasswordHash

from app.config import setting

password_hash = PasswordHash.recommended()


def generate_hash_ip(plain_ip_address: str) -> str:
    return hashlib.sha256(plain_ip_address.encode("utf-8")).hexdigest()


def get_hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)


def verify_hash_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=setting.ACCESS_TOKEN_EXPIRE_TIME
    )

    to_encode.update({"exp": expire})

    return jwt.encode(
        payload=to_encode, key=setting.SECRETE_KEY, algorithm=setting.ALGORITHM
    )


def decode_access_token(token: str, secrete_key: str, algorithm: str):
    return jwt.decode(jwt=token, key=secrete_key, algorithms=algorithm)
