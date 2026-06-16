from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def get_current_user():
    """Get current logged in user from session"""
    user_data = session.get("user")
    if not user_data:
        return None
    return User.query.filter_by(email=user_data.get("email")).first()

@auth_bp.route("/signup", methods=["POST"])
def auth_signup():
    """User registration with database"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    name = data.get("name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"error": "Email already registered"}), 400
    
    # Create new user in database
    new_user = User(
        name=name,
        email=email,
        password_hash=generate_password_hash(password)
    )
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        # Set session
        session["user"] = {"id": new_user.id, "name": name, "email": email}
        
        return jsonify({
            "success": True,
            "message": "Account created successfully",
            "user": new_user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create account", "details": str(e)}), 500


@auth_bp.route("/login", methods=["POST"])
def auth_login():
    """User login with database"""
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    
    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    
    # Find user in database
    user = User.query.filter_by(email=email).first()
    
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401
    
    # Set session
    session["user"] = {"id": user.id, "name": user.name, "email": user.email}
    
    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": user.to_dict()
    })


@auth_bp.route("/logout", methods=["POST"])
def auth_logout():
    """User logout"""
    session.pop("user", None)
    return jsonify({"success": True, "message": "Logged out successfully"})


@auth_bp.route("/me", methods=["GET"])
def auth_me():
    """Get current user with full profile"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"success": True, "user": user.to_dict()})
