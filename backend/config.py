import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration settings."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default-dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "default-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 hours in seconds
    
    # Primary Database connection string (MySQL PyMySQL format)
    DATABASE_URL = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:password@localhost:3306/internship_portal_db"
    )
    
    # SQLAlchemy configuration
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Uploads folder configuration
    UPLOAD_FOLDER = os.path.abspath(os.getenv("UPLOAD_FOLDER", "uploads"))
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max limit
