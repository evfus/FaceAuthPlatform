import secrets
from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

def generate_client_id() -> str:
    return secrets.token_hex(16)

def generate_client_secret() -> str:
    return secrets.token_urlsafe(32)

def hash_secret(raw_secret: str) -> str:
    return pwd_context.hash(raw_secret)

def verify_secret(raw_secret: str, hash_secret: str) -> bool:
    return pwd_context.verify(raw_secret, hash_secret)

def generate_auth_code() -> str:
    return secrets.token_urlsafe(32)

def generate_token() ->str:
    return secrets.token_urlsafe(32)
