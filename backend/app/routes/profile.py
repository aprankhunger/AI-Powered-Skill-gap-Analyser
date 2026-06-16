from flask import Blueprint, request, jsonify
from app.models import db, Analysis, LearningProgress
from app.routes.auth import get_current_user

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

@profile_bp.route("/", methods=["GET"])
def get_profile():
    """Get user profile with statistics"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get analysis statistics
    analyses = Analysis.query.filter_by(user_id=user.id).order_by(Analysis.created_at.desc()).all()
    
    # Calculate stats
    total_analyses = len(analyses)
    avg_skill_match = sum(a.skill_match_percentage for a in analyses) / total_analyses if total_analyses > 0 else 0
    avg_ats_score = sum(a.ats_score for a in analyses) / total_analyses if total_analyses > 0 else 0
    
    # Get learning progress stats
    learning_items = LearningProgress.query.filter_by(user_id=user.id).all()
    skills_completed = len([l for l in learning_items if l.status == 'completed'])
    skills_in_progress = len([l for l in learning_items if l.status == 'in_progress'])
    
    # Get latest analysis
    latest_analysis = analyses[0].to_dict() if analyses else None
    
    return jsonify({
        "success": True,
        "profile": user.to_dict(),
        "stats": {
            "total_analyses": total_analyses,
            "avg_skill_match": round(avg_skill_match, 1),
            "avg_ats_score": round(avg_ats_score, 1),
            "skills_completed": skills_completed,
            "skills_in_progress": skills_in_progress,
            "total_skills_tracked": len(learning_items)
        },
        "latest_analysis": latest_analysis
    })


@profile_bp.route("/", methods=["PUT"])
def update_profile():
    """Update user profile"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update allowed fields
    allowed_fields = ['name', 'current_role', 'target_role', 'years_experience', 'bio', 'linkedin_url', 'github_url', 'profile_picture']
    
    for field in allowed_fields:
        if field in data:
            setattr(user, field, data[field])
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Profile updated successfully",
            "profile": user.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update profile", "details": str(e)}), 500
