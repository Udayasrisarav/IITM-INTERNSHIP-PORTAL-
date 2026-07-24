import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from database import init_db
from routes import health_bp


def create_app(config_class=Config):
    """Flask Application Factory."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure upload directory exists
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Initialize extensions
    CORS(app)
    JWTManager(app)

    # Initialize database
    init_db(app)

    # Register blueprints
    app.register_blueprint(health_bp)

    from routes.auth import auth_bp
    from routes.profile import profile_bp
    from routes.application_routes import application_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(application_bp)

    @app.route("/")
    def index():
        return jsonify({
            "message": "Welcome to Internship Management Portal API Foundation",
            "health_check": "/health",
            "api_health_check": "/api/v1/health"
        }), 200

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() in ["true", "1", "t"]

    print(
        f"Starting Internship Management Portal Backend Server on port {port}..."
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=debug,
        use_reloader=False
    )