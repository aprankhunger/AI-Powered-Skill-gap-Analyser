from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from openai import OpenAI
import pdfplumber
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
from io import BytesIO
import json
import re
import os
from dotenv import load_dotenv
import redis
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Load environment variables first
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///skillgap.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# ============ DATABASE MODELS ============
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
    
    analyses = db.relationship('Analysis', backref='user', lazy=True, cascade='all, delete-orphan')
    learning_progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
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
    skill_match_percentage = db.Column(db.Integer, default=0)
    ats_score = db.Column(db.Integer, default=0)
    experience_level = db.Column(db.String(50), default=None)
    years_of_experience = db.Column(db.String(50), default=None)
    technical_skills = db.Column(db.Text, default='[]')
    soft_skills = db.Column(db.Text, default='[]')
    missing_skills = db.Column(db.Text, default='[]')
    suggestions = db.Column(db.Text, default='{}')
    learning_resources = db.Column(db.Text, default='[]')
    skill_roadmap = db.Column(db.Text, default='[]')
    summary = db.Column(db.Text, default=None)
    candidate_name = db.Column(db.String(100), default=None)
    candidate_email = db.Column(db.String(120), default=None)
    candidate_phone = db.Column(db.String(30), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
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
            'skill_roadmap': json.loads(self.skill_roadmap) if self.skill_roadmap else [],
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
    status = db.Column(db.String(20), default='not_started')
    notes = db.Column(db.Text, default=None)
    resource_url = db.Column(db.String(500), default=None)
    target_role = db.Column(db.String(100), default=None)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('user_id', 'skill_name', name='unique_user_skill'),)
    
    def to_dict(self):
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


# Create database tables
with app.app_context():
    db.create_all()
    print("Database initialized successfully!")

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
    ALLOWED_ORIGINS.append(FRONTEND_URL)
    # Also add without trailing slash and with https
    if not FRONTEND_URL.startswith("https://"):
        ALLOWED_ORIGINS.append(FRONTEND_URL.replace("http://", "https://"))

CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS, supports_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Configure OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),  # Never hardcode API keys!
)

# Redis connection (optional - caching will be disabled if Redis is not available)
try:
    redis_client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'), port=int(os.getenv('REDIS_PORT', 6379)), db=0)
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
except:
    redis_client = None
    REDIS_AVAILABLE = False
    print("Warning: Redis not available. Caching disabled.")

CACHE_TTL = 3600  # 1 hour

SYSTEM_PROMPT = """
You are an AI Resume & Skill Gap Analyzer.

Your tasks:
1. Analyze the resume text provided.
2. Extract technical skills mentioned.
3. Infer the candidate's experience level.
4. Compare resume skills with the target role.
5. Identify missing skills.
6. Suggest improvements for:
   - ATS optimization
   - Skill section
   - Project section

Rules:
- Do NOT hallucinate skills.
- Output ONLY valid JSON with this exact structure:
{
    "candidate_name": "Name from resume or Unknown",
    "experience_level": "Entry/Mid/Senior/Expert",
    "years_of_experience": "X years (estimated)",
    "technical_skills": ["skill1", "skill2"],
    "soft_skills": ["skill1", "skill2"],
    "missing_skills": ["skill1", "skill2"],
    "skill_match_percentage": 75,
    "ats_score": 70,
    "suggestions": {
        "ats_optimization": ["suggestion1", "suggestion2"],
        "skill_section": ["suggestion1", "suggestion2"],
        "project_section": ["suggestion1", "suggestion2"],
        "general": ["suggestion1", "suggestion2"]
    },
    "skill_roadmap": [
        {
            "skill": "skill name",
            "priority": 1,
            "importance": "critical/high/medium/low",
            "improvement_percent": 15,
            "reason": "Why this skill is needed for the target role",
            "time_to_learn": "2-4 weeks",
            "prerequisites": ["skill1", "skill2"]
        }
    ],
    "learning_resources": [
        {
            "skill": "missing skill name",
            "youtube_search_query": "best tutorial playlist for [skill] beginners",
            "description": "Brief description of what to learn"
        }
    ],
    "summary": "Brief overall assessment"
}

For skill_roadmap:
- Order skills by priority (1 = most important to learn first)
- improvement_percent should estimate how much the skill_match_percentage would increase if this skill is learned (total should roughly add up to 100 - current_match)
- Include prerequisite skills if any (skills they should learn before this one)
- time_to_learn should be realistic estimate for someone at candidate's level
- importance: "critical" for must-have skills, "high" for strongly recommended, "medium" for good to have, "low" for nice to have

For learning_resources:
- Include a resource for each missing skill (up to 5 most important ones)
- Create a YouTube search query that would find good tutorial playlists for that skill
- Make queries specific and include words like 'tutorial', 'course', 'playlist', 'full course', 'beginners' or 'advanced' based on context
"""


# ============ PDF TEXT EXTRACTION ============
def extract_text_from_pdf(file):
    """Extract text with multiple fallbacks"""
    file_bytes = file.read()
    file.seek(0)
    
    extraction_results = []
    
    # Method 1: pdfplumber (best for most PDFs)
    try:
        file.seek(0)
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
            if text.strip():
                extraction_results.append({"method": "pdfplumber", "text": text})
    except Exception as e:
        pass
    
    # Method 2: PyPDF2 (fallback)
    try:
        file.seek(0)
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        if text.strip():
            extraction_results.append({"method": "PyPDF2", "text": text})
    except Exception as e:
        pass
    
    # Method 3: OCR (for scanned PDFs)
    if not extraction_results or all(len(r["text"]) < 100 for r in extraction_results):
        try:
            images = convert_from_bytes(file_bytes)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            if text.strip():
                extraction_results.append({"method": "OCR", "text": text})
        except Exception as e:
            pass
    
    # Return best result (longest text)
    if extraction_results:
        best = max(extraction_results, key=lambda x: len(x["text"]))
        return {
            "text": best["text"],
            "method": best["method"],
            "confidence": "high" if len(best["text"]) > 500 else "medium" if len(best["text"]) > 100 else "low"
        }
    
    return {"text": "", "method": None, "confidence": "failed"}


# ============ CONTACT EXTRACTION ============
def extract_email(text):
    """Extract email from text"""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(pattern, text)
    return match.group(0) if match else None


def extract_phone(text):
    """Extract phone number from text"""
    patterns = [
        r'\+?1?[-.\s]?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}',
        r'\b[0-9]{10,12}\b',
        r'\b[0-9]{3}[-.\s][0-9]{3}[-.\s][0-9]{4}\b'
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_links(text):
    """Extract URLs from text"""
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    
    links = {
        "linkedin": None,
        "github": None,
        "portfolio": None,
        "other": []
    }
    
    for url in urls:
        url_lower = url.lower()
        if "linkedin" in url_lower:
            links["linkedin"] = url
        elif "github" in url_lower:
            links["github"] = url
        elif links["portfolio"] is None:
            links["portfolio"] = url
        else:
            links["other"].append(url)
    
    return links


def extract_name(text):
    """Extract candidate name from resume"""
    lines = text.split('\n')[:5]
    
    for line in lines:
        line = line.strip()
        if '@' in line or 'http' in line:
            continue
        if len(line) < 2:
            continue
        if any(keyword in line.lower() for keyword in ['resume', 'cv', 'phone', 'email', 'address']):
            continue
        
        words = line.split()
        if 1 <= len(words) <= 4:
            if all(word.replace('.', '').replace('-', '').isalpha() for word in words):
                return line
    
    return None


# ============ SECTION PARSING ============
def identify_section(line):
    """Identify resume section from line"""
    line_lower = line.lower().strip()
    
    sections = {
        "education": ["education", "academic", "qualification", "degree"],
        "experience": ["experience", "employment", "work history", "professional experience"],
        "skills": ["skills", "technical skills", "competencies", "technologies"],
        "projects": ["projects", "personal projects", "academic projects"],
        "certifications": ["certification", "certificates", "licensed"],
        "summary": ["summary", "objective", "profile", "about me"],
        "achievements": ["achievements", "accomplishments", "awards"],
        "languages": ["languages", "language proficiency"],
        "interests": ["interests", "hobbies"]
    }
    
    for section, keywords in sections.items():
        if any(keyword in line_lower for keyword in keywords):
            return section
    
    return None


def parse_resume_sections(text):
    """Parse resume into sections"""
    lines = text.split('\n')
    sections = {
        "contact": [],
        "summary": [],
        "education": [],
        "experience": [],
        "skills": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
        "languages": [],
        "interests": [],
        "other": []
    }
    
    current_section = "contact"
    contact_lines_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        identified = identify_section(line)
        if identified:
            current_section = identified
            continue
        
        if current_section == "contact" and contact_lines_count < 6:
            sections["contact"].append(line)
            contact_lines_count += 1
        else:
            if current_section == "contact":
                current_section = "other"
            sections[current_section].append(line)
    
    return sections


# ============ SKILL DETECTION ============
def extract_skills_from_text(text):
    """Auto-detect technical skills from text"""
    skill_patterns = [
        # Programming Languages
        r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|Scala|R|MATLAB|Perl|SQL)\b',
        # Frameworks
        r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|\.NET|Rails|Laravel|FastAPI|Next\.js)\b',
        # Databases
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQLite|DynamoDB|Cassandra|Firebase|Elasticsearch)\b',
        # Cloud & DevOps
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD|Terraform|Ansible)\b',
        # Data Science & ML
        r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Spark|Hadoop|Tableau|Power BI)\b',
        # Tools
        r'\b(Linux|Unix|Jira|Confluence|VS Code|IntelliJ|Eclipse)\b',
        # Web Technologies
        r'\b(HTML|CSS|SASS|REST|GraphQL|API|JSON|XML|OAuth|JWT)\b',
        # Methodologies
        r'\b(Agile|Scrum|Kanban|DevOps|TDD|BDD|OOP|Microservices)\b'
    ]
    
    skills = set()
    search_text = text.upper() + " " + text
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        skills.update(matches)
    
    return list(skills)


# ============ DATA STRUCTURING ============
def structure_resume_data(file):
    """Structure resume data from PDF"""
    raw_result = extract_text_from_pdf(file)
    raw_text = raw_result["text"]  # Extract the text string from the result dict
    
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    links = extract_links(raw_text)
    name = extract_name(raw_text)
    
    sections = parse_resume_sections(raw_text)
    detected_skills = extract_skills_from_text(raw_text)
    
    return {
        "candidate_info": {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": links["linkedin"],
            "github": links["github"],
            "portfolio": links["portfolio"]
        },
        "sections": {
            "summary": " ".join(sections["summary"]) if sections["summary"] else None,
            "education": sections["education"],
            "experience": sections["experience"],
            "skills_section": sections["skills"],
            "projects": sections["projects"],
            "certifications": sections["certifications"],
            "achievements": sections["achievements"],
            "other": sections["other"]
        },
        "detected_skills": detected_skills,
        "raw_text": raw_text
    }


def format_structured_data_for_ai(structured_data, target_role):
    """Format structured data for AI prompt"""
    prompt_parts = []
    
    prompt_parts.append("=== CANDIDATE INFORMATION ===")
    info = structured_data["candidate_info"]
    if info["name"]:
        prompt_parts.append(f"Name: {info['name']}")
    if info["email"]:
        prompt_parts.append(f"Email: {info['email']}")
    if info["phone"]:
        prompt_parts.append(f"Phone: {info['phone']}")
    if info["linkedin"]:
        prompt_parts.append(f"LinkedIn: {info['linkedin']}")
    if info["github"]:
        prompt_parts.append(f"GitHub: {info['github']}")
    
    sections = structured_data["sections"]
    
    if sections["summary"]:
        prompt_parts.append("\n=== PROFESSIONAL SUMMARY ===")
        prompt_parts.append(sections["summary"])
    
    if sections["experience"]:
        prompt_parts.append("\n=== WORK EXPERIENCE ===")
        prompt_parts.extend(sections["experience"])
    
    if sections["education"]:
        prompt_parts.append("\n=== EDUCATION ===")
        prompt_parts.extend(sections["education"])
    
    if sections["skills_section"]:
        prompt_parts.append("\n=== SKILLS (from resume) ===")
        prompt_parts.extend(sections["skills_section"])
    
    if structured_data["detected_skills"]:
        prompt_parts.append("\n=== AUTO-DETECTED TECHNICAL SKILLS ===")
        prompt_parts.append(", ".join(structured_data["detected_skills"]))
    
    if sections["projects"]:
        prompt_parts.append("\n=== PROJECTS ===")
        prompt_parts.extend(sections["projects"])
    
    if sections["certifications"]:
        prompt_parts.append("\n=== CERTIFICATIONS ===")
        prompt_parts.extend(sections["certifications"])
    
    if sections["achievements"]:
        prompt_parts.append("\n=== ACHIEVEMENTS ===")
        prompt_parts.extend(sections["achievements"])
    
    prompt_parts.append(f"\n=== TARGET ROLE ===\n{target_role}")
    prompt_parts.append("\n=== TASK ===")
    prompt_parts.append("Analyze this resume against the target role and provide the JSON response as specified.")
    
    return "\n".join(prompt_parts)


def generate_youtube_links(learning_resources):
    """Generate YouTube search links for learning resources"""
    if not learning_resources:
        return []
    
    resources_with_links = []
    for resource in learning_resources:
        skill = resource.get("skill", "Unknown Skill")
        query = resource.get("youtube_search_query", f"{skill} tutorial")
        description = resource.get("description", "Learn this skill")
        
        youtube_url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        resources_with_links.append({
            "skill": skill,
            "description": description,
            "youtube_search_query": query,
            "youtube_url": youtube_url
        })
    
    return resources_with_links


# ============ CACHING ============
def get_cache_key(file_bytes, target_role):
    """Generate unique cache key based on file content and role"""
    content_hash = hashlib.sha256(file_bytes + target_role.encode()).hexdigest()
    return f"resume_analysis:{content_hash}"

def get_cached_result(cache_key):
    """Get cached analysis result"""
    if not REDIS_AVAILABLE:
        return None
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except:
        pass
    return None

def cache_result(cache_key, result):
    """Cache analysis result"""
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
    except:
        pass


# ============ HELPER FUNCTION FOR AUTH ============
def get_current_user():
    """Get current logged in user from session"""
    user_data = session.get("user")
    if not user_data:
        return None
    return User.query.filter_by(email=user_data.get("email")).first()


# ============ AUTH ROUTES ============
@app.route("/auth/signup", methods=["POST"])
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


@app.route("/auth/login", methods=["POST"])
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


@app.route("/auth/logout", methods=["POST"])
def auth_logout():
    """User logout"""
    session.pop("user", None)
    return jsonify({"success": True, "message": "Logged out successfully"})


@app.route("/auth/me", methods=["GET"])
def auth_me():
    """Get current user with full profile"""
    user = get_current_user()
    if not user:
        return jsonify({"error": "Not authenticated"}), 401
    return jsonify({"success": True, "user": user.to_dict()})


# ============ PROFILE ROUTES ============
@app.route("/profile", methods=["GET"])
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


@app.route("/profile", methods=["PUT"])
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


# ============ ANALYSIS HISTORY ROUTES ============
@app.route("/analyses/history", methods=["GET"])
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


@app.route("/analyses/<int:analysis_id>", methods=["GET"])
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


@app.route("/analyses/<int:analysis_id>", methods=["DELETE"])
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
        return jsonify({"error": "Failed to delete analysis", "details": str(e)}), 500


# ============ LEARNING PROGRESS ROUTES ============
@app.route("/learning/progress", methods=["GET"])
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


@app.route("/learning/progress", methods=["POST"])
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
        return jsonify({"error": "Failed to add skill", "details": str(e)}), 500


@app.route("/learning/progress/<int:progress_id>", methods=["PUT"])
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
        return jsonify({"error": "Failed to update progress", "details": str(e)}), 500


@app.route("/learning/progress/<int:progress_id>", methods=["DELETE"])
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
        return jsonify({"error": "Failed to delete progress", "details": str(e)}), 500


# ============ API ROUTES ============
@app.route("/", methods=["GET"])
def home():
    """API health check"""
    return jsonify({
        "status": "running",
        "message": "AI Resume Analyzer API",
        "endpoints": {
            "POST /analyze-resume": "Analyze a resume PDF",
            "GET /health": "Health check"
        }
    })


@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})


@app.route("/analyze-resume", methods=["POST"])
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
        
        # Format prompt for AI
        prompt = format_structured_data_for_ai(structured_data, target_role)
        
        # Call AI API
        response = client.chat.completions.create(
            model="amazon/nova-micro-v1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
        )
        
        result = response.choices[0].message.content
        
        # Parse AI response
        try:
            cleaned = result.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.replace("```json", "").replace("```", "").strip()
            
            analysis = json.loads(cleaned)
        except json.JSONDecodeError:
            analysis = {
                "error": "Failed to parse AI response",
                "raw_response": result
            }
        
        # Add YouTube links to learning resources
        if "learning_resources" in analysis:
            analysis["learning_resources"] = generate_youtube_links(analysis["learning_resources"])
        
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
                    technical_skills=json.dumps(analysis.get("technical_skills", [])),
                    soft_skills=json.dumps(analysis.get("soft_skills", [])),
                    missing_skills=json.dumps(analysis.get("missing_skills", [])),
                    suggestions=json.dumps(analysis.get("suggestions", {})),
                    learning_resources=json.dumps(analysis.get("learning_resources", [])),
                    skill_roadmap=json.dumps(analysis.get("skill_roadmap", [])),
                    summary=analysis.get("summary"),
                    candidate_name=analysis.get("candidate_name") or structured_data["candidate_info"].get("name"),
                    candidate_email=structured_data["candidate_info"].get("email"),
                    candidate_phone=structured_data["candidate_info"].get("phone")
                )
                db.session.add(new_analysis)
                db.session.commit()
                analysis_id = new_analysis.id
            except Exception as save_error:
                print(f"Failed to save analysis: {save_error}")
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
    #working
    except Exception as e:
        import traceback
        print(f"Error analyzing resume: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            "error": "Failed to analyze resume",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
