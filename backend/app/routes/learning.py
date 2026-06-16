from flask import Blueprint, request, jsonify
import logging
from app.models import db, LearningProgress
from app.routes.auth import get_current_user

logger = logging.getLogger(__name__)
learning_bp = Blueprint('learning', __name__, url_prefix='/learning')

@learning_bp.route("/progress", methods=["GET"])
def get_learning_progress():
    """Get user's learning progress"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    progress = LearningProgress.query.filter_by(user_id=user.id)\
        .order_by(LearningProgress.updated_at.desc()).all()
    
    # Group by status
    grouped = {
        "not_started": [],
        "in_progress": [],
        "completed": []
    }
    
    for item in progress:
        grouped[item.status].append(item.to_dict())
    
    return jsonify({
        "success": True,
        "progress": [p.to_dict() for p in progress],
        "grouped": grouped,
        "stats": {
            "total": len(progress),
            "not_started": len(grouped["not_started"]),
            "in_progress": len(grouped["in_progress"]),
            "completed": len(grouped["completed"])
        }
    })

@learning_bp.route("/progress", methods=["POST"])
def add_learning_skill():
    """Add a skill to learning progress"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    data = request.get_json()
    if not data or not data.get("skill_name"):
        return jsonify({"error": "Skill name is required"}), 400
    
    skill_name = data.get("skill_name").strip()
    
    # Check if skill already exists for user
    existing = LearningProgress.query.filter_by(user_id=user.id, skill_name=skill_name).first()
    if existing:
        return jsonify({"error": "Skill already in your learning list", "progress": existing.to_dict()}), 400
    
    new_progress = LearningProgress(
        user_id=user.id,
        skill_name=skill_name,
        status=data.get("status", "not_started"),
        notes=data.get("notes"),
        resource_url=data.get("resource_url"),
        target_role=data.get("target_role")
    )
    
    try:
        db.session.add(new_progress)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Skill added to learning progress",
            "progress": new_progress.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to add skill: {e}")
        return jsonify({"error": "Failed to add skill", "details": str(e)}), 500

@learning_bp.route("/progress/<int:progress_id>", methods=["PUT"])
def update_learning_progress(progress_id):
    """Update learning progress for a skill"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    progress = LearningProgress.query.filter_by(id=progress_id, user_id=user.id).first()
    if not progress:
        return jsonify({"error": "Progress item not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Update allowed fields
    if "status" in data:
        if data["status"] not in ["not_started", "in_progress", "completed"]:
            return jsonify({"error": "Invalid status"}), 400
        progress.status = data["status"]
    
    if "notes" in data:
        progress.notes = data["notes"]
    
    if "resource_url" in data:
        progress.resource_url = data["resource_url"]
    
    try:
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Progress updated successfully",
            "progress": progress.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to update progress {progress_id}: {e}")
        return jsonify({"error": "Failed to update progress", "details": str(e)}), 500

@learning_bp.route("/progress/<int:progress_id>", methods=["DELETE"])
def delete_learning_progress(progress_id):
    """Delete a skill from learning progress"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    progress = LearningProgress.query.filter_by(id=progress_id, user_id=user.id).first()
    if not progress:
        return jsonify({"error": "Progress item not found"}), 404
    
    try:
        db.session.delete(progress)
        db.session.commit()
        return jsonify({"success": True, "message": "Skill removed from learning progress"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete progress {progress_id}: {e}")
        return jsonify({"error": "Failed to delete progress", "details": str(e)}), 500
