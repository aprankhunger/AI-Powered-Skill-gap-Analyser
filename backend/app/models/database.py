"""
Database Models for AI Skill Gap Analyser
Using SQLAlchemy with SQLite
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class User(db.Model):
    """User model for authentication and profile"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    profile_picture = db.Column(db.String(500), default=None)
    current_role = db.Column(db.String(100), default=None)
    target_role = db.Column(db.String(100), default=None)
    years_experience = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text, default=None)
    linkedin_url = db.Column(db.String(300), default=None)
    github_url = db.Column(db.String(300), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert user to dictionary (excluding password)"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'profile_picture': self.profile_picture,
            'current_role': self.current_role,
            'target_role': self.target_role,
            'years_experience': self.years_experience,
            'bio': self.bio,
            'linkedin_url': self.linkedin_url,
            'github_url': self.github_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'total_analyses': len(self.analyses)
        }


class Analysis(db.Model):
    """Model to store resume analysis history"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_role = db.Column(db.String(100), nullable=False)
    resume_filename = db.Column(db.String(200), default=None)
    
    # Scores
    skill_match_percentage = db.Column(db.Integer, default=0)
    ats_score = db.Column(db.Integer, default=0)
    experience_level = db.Column(db.String(50), default=None)
    years_of_experience = db.Column(db.String(50), default=None)
    
    # Skills data (stored as JSON strings)
    technical_skills = db.Column(db.Text, default='[]')  # JSON array
    soft_skills = db.Column(db.Text, default='[]')  # JSON array
    missing_skills = db.Column(db.Text, default='[]')  # JSON array
    
    # Additional data
    suggestions = db.Column(db.Text, default='{}')  # JSON object
    learning_resources = db.Column(db.Text, default='[]')  # JSON array
    summary = db.Column(db.Text, default=None)
    
    # Candidate info from resume
    candidate_name = db.Column(db.String(100), default=None)
    candidate_email = db.Column(db.String(120), default=None)
    candidate_phone = db.Column(db.String(30), default=None)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            'id': self.id,
            'target_role': self.target_role,
            'resume_filename': self.resume_filename,
            'skill_match_percentage': self.skill_match_percentage,
            'ats_score': self.ats_score,
            'experience_level': self.experience_level,
            'years_of_experience': self.years_of_experience,
            'technical_skills': json.loads(self.technical_skills) if self.technical_skills else [],
            'soft_skills': json.loads(self.soft_skills) if self.soft_skills else [],
            'missing_skills': json.loads(self.missing_skills) if self.missing_skills else [],
            'suggestions': json.loads(self.suggestions) if self.suggestions else {},
            'learning_resources': json.loads(self.learning_resources) if self.learning_resources else [],
            'summary': self.summary,
            'candidate_name': self.candidate_name,
            'candidate_email': self.candidate_email,
            'candidate_phone': self.candidate_phone,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class LearningProgress(db.Model):
    """Model to track skill learning progress"""
    __tablename__ = 'learning_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed
    notes = db.Column(db.Text, default=None)
    resource_url = db.Column(db.String(500), default=None)
    target_role = db.Column(db.String(100), default=None)  # Which role this skill is for
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one skill per user
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_name', name='unique_user_skill'),)
    
    def to_dict(self):
        """Convert learning progress to dictionary"""
        return {
            'id': self.id,
            'skill_name': self.skill_name,
            'status': self.status,
            'notes': self.notes,
            'resource_url': self.resource_url,
            'target_role': self.target_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


def init_db(app):
    """Initialize the database with the Flask app"""
    db.init_app(app)
    with app.app_context():
        db.create_all()
        print("Database initialized successfully!")
