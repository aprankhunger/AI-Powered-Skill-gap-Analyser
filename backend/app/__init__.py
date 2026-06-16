import os
import logging
from flask import Flask, request
from flask_cors import CORS
from app.models import db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    
    # Check for critical env vars in production
    if not app.debug and not app.testing:
        if not os.getenv("SECRET_KEY"):
            logger.warning("SECRET_KEY is not set. Using insecure default for development only.")
        if not os.getenv("OPENROUTER_API_KEY"):
            logger.error("OPENROUTER_API_KEY is not set! AI features will fail.")
            
    app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

    # Session cookie configuration for cross-origin requests
    app.config['SESSION_COOKIE_SECURE'] = True  # Only send cookie over HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent JavaScript access
    app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site cookies
    app.config['SESSION_COOKIE_NAME'] = 'skillgap_session'

    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///skillgap.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    # Initialize extensions
    db.init_app(app)

    # CORS configuration - allow production and development origins
    ALLOWED_ORIGINS = [
        "http://localhost:5173", 
        "http://localhost:5174", 
        "http://localhost:3000", 
        "http://127.0.0.1:5173", 
        "http://127.0.0.1:5174"
    ]

    # Add production frontend URL from environment variable
    FRONTEND_URL = os.getenv("FRONTEND_URL")
    if FRONTEND_URL:
        # Clean up the URL - remove trailing slashes
        FRONTEND_URL = FRONTEND_URL.rstrip('/')
        ALLOWED_ORIGINS.append(FRONTEND_URL)
        if FRONTEND_URL.startswith("http://"):
            ALLOWED_ORIGINS.append(FRONTEND_URL.replace("http://", "https://"))
        elif FRONTEND_URL.startswith("https://"):
            ALLOWED_ORIGINS.append(FRONTEND_URL.replace("https://", "http://"))

    logger.info(f"CORS Allowed Origins: {ALLOWED_ORIGINS}")

    CORS(app, 
         supports_credentials=True, 
         origins=ALLOWED_ORIGINS,
         allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
         expose_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"])

    # Add explicit CORS headers to all responses
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin in ALLOWED_ORIGINS:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Accept, Origin'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS, PATCH'
        return response

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp
    from app.routes.analysis import analysis_bp
    from app.routes.learning import learning_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(learning_bp)
    
    # Root health check endpoint
    @app.route("/", methods=["GET"])
    def home():
        """API health check"""
        return {"status": "running", "message": "AI Resume Analyzer API (Modular)"}

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint"""
        return {"status": "healthy"}

    return app
