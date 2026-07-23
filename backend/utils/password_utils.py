from werkzeug.security import generate_password_hash, check_password_hash

def hash_password(password: str) -> str:
    """Hash password using Werkzeug's default secure algorithm."""
    if not password:
        raise ValueError("Password cannot be empty")
    return generate_password_hash(password)

def verify_password(password_hash: str, password: str) -> bool:
    """Verify raw password against hashed password."""
    if not password_hash or not password:
        return False
    return check_password_hash(password_hash, password)
