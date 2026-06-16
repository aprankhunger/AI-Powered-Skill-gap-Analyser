from flask import Blueprint, request, jsonify
import logging
import traceback
from app.models import db, Analysis
from app.routes.auth import get_current_user
from app.services.pdf_extractor import structure_resume_data
from app.services.ai_analyzer import analyze_resume_with_ai, get_cache_key, get_cached_result, cache_result

logger = logging.getLogger(__name__)
analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route("/analyses/history", methods=["GET"])
def get_analysis_history():
    """Get user's analysis history"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    # Get pagination params
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Query analyses
    analyses = Analysis.query.filter_by(user_id=user.id)\
        .order_by(Analysis.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        "success": True,
        "analyses": [a.to_dict() for a in analyses.items],
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": analyses.total,
            "pages": analyses.pages,
            "has_next": analyses.has_next,
            "has_prev": analyses.has_prev
        }
    })

@analysis_bp.route("/analyses/<int:analysis_id>", methods=["GET"])
def get_analysis_detail(analysis_id):
    """Get specific analysis details"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404
    
    return jsonify({
        "success": True,
        "analysis": analysis.to_dict()
    })

@analysis_bp.route("/analyses/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):
    """Delete an analysis"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    
    analysis = Analysis.query.filter_by(id=analysis_id, user_id=user.id).first()
    if not analysis:
        return jsonify({"error": "Analysis not found"}), 404
    
    try:
        db.session.delete(analysis)
        db.session.commit()
        return jsonify({"success": True, "message": "Analysis deleted successfully"})
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to delete analysis {analysis_id}: {e}")
        return jsonify({"error": "Failed to delete analysis", "details": str(e)}), 500

@analysis_bp.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    """Analyze resume and return JSON response"""
    
    # Validate request
    if "resume" not in request.files:
        return jsonify({"error": "No resume file provided"}), 400
    
    resume_file = request.files["resume"]
    target_role = request.form.get("target_role", "Software Developer")
    
    if resume_file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    if not resume_file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are supported"}), 400
    
    try:
        file_bytes = resume_file.read()
        resume_file.seek(0)  # Reset file position for re-reading
        
        # Check cache first
        cache_key = get_cache_key(file_bytes, target_role)
        cached_result = get_cached_result(cache_key)
        if cached_result:
            logger.info("Returning cached analysis result.")
            return jsonify({
                "success": True,
                "target_role": target_role,
                "candidate_info": cached_result["candidate_info"],
                "detected_skills": cached_result["detected_skills"],
                "analysis": cached_result["analysis"],
                "cached": True
            })
        
        # Extract and structure resume data
        structured_data = structure_resume_data(resume_file)
        
        # Check if text was extracted
        if len(structured_data["raw_text"].strip()) < 50:
            return jsonify({
                "error": "Could not extract text from PDF. It might be scanned or image-based.",
                "suggestion": "Please upload a text-based PDF"
            }), 400
        
        # Analyze with AI
        analysis = analyze_resume_with_ai(structured_data, target_role)
        
        # Cache the result
        cache_result(cache_key, {
            "candidate_info": structured_data["candidate_info"],
            "detected_skills": structured_data["detected_skills"],
            "analysis": analysis
        })
        
        # Save analysis for logged-in users
        analysis_id = None
        current_user = get_current_user()
        if current_user:
            try:
                new_analysis = Analysis(
                    user_id=current_user.id,
                    target_role=target_role,
                    resume_filename=resume_file.filename,
                    skill_match_percentage=analysis.get("skill_match_percentage", 0),
                    ats_score=analysis.get("ats_score", 0),
                    experience_level=analysis.get("experience_level"),
                    years_of_experience=analysis.get("years_of_experience"),
                    # Now storing directly as JSON, no dumps needed
                    technical_skills=analysis.get("technical_skills", []),
                    soft_skills=analysis.get("soft_skills", []),
                    missing_skills=analysis.get("missing_skills", []),
                    suggestions=analysis.get("suggestions", {}),
                    learning_resources=analysis.get("learning_resources", []),
                    skill_roadmap=analysis.get("skill_roadmap", []),
                    summary=analysis.get("summary"),
                    candidate_name=analysis.get("candidate_name") or structured_data["candidate_info"].get("name"),
                    candidate_email=structured_data["candidate_info"].get("email"),
                    candidate_phone=structured_data["candidate_info"].get("phone")
                )
                db.session.add(new_analysis)
                db.session.commit()
                analysis_id = new_analysis.id
                logger.info(f"Saved analysis {analysis_id} for user {current_user.id}")
            except Exception as save_error:
                logger.error(f"Failed to save analysis: {save_error}")
                db.session.rollback()
        
        # Return complete response
        return jsonify({
            "success": True,
            "target_role": target_role,
            "candidate_info": structured_data["candidate_info"],
            "detected_skills": structured_data["detected_skills"],
            "analysis": analysis,
            "analysis_id": analysis_id,
            "saved": analysis_id is not None
        })
        
    except Exception as e:
        logger.error(f"Error analyzing resume: {str(e)}\n{traceback.format_exc()}")
        return jsonify({
            "error": "Failed to analyze resume",
            "details": str(e)
        }), 500
