from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

db = SQLAlchemy()

def init_db(app):
    """Initialize SQLAlchemy DB with Flask app and fallback support."""
    db_uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")

    # Check primary DB connection (e.g. MySQL)
    if "mysql" in db_uri:
        try:
            test_engine = create_engine(db_uri)
            with test_engine.connect() as conn:
                pass
            test_engine.dispose()
            app.logger.info("Successfully verified MySQL database connection.")
        except Exception as e:
            app.logger.warning(
                f"MySQL connection warning: {e}. "
                "Falling back to local SQLite database for development initialization."
            )
            app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dev_fallback.db"

    db.init_app(app)
    
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database initialized successfully.")
        except Exception as e:
            app.logger.error(f"Error during db.create_all(): {e}")
