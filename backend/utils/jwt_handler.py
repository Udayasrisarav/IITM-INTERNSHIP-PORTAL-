import jwt
from datetime import datetime, timedelta
from flask import current_app

DEFAULT_EXPIRES_SECONDS = 86400  # 24 hours

def generate_token(user_id: int, email: str, role_name: str, expires_in: int = DEFAULT_EXPIRES_SECONDS) -> str:
    """Generate JWT access token valid for 24 hours."""
    secret_key = current_app.config.get("JWT_SECRET_KEY", current_app.config.get("SECRET_KEY", "dev-secret"))
    now = datetime.utcnow()
    payload = {
        "user_id": user_id,
        "email": email,
        "sub": email,
        "role": role_name,
        "iat": now,
        "exp": now + timedelta(seconds=expires_in)
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

def decode_token(token: str) -> dict:
    """Decode and validate JWT access token. Raises jwt exceptions on failure."""
    secret_key = current_app.config.get("JWT_SECRET_KEY", current_app.config.get("SECRET_KEY", "dev-secret"))
    payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    return payload
