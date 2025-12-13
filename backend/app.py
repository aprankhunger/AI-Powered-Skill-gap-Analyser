from flask import Flask, request, jsonify
from flask_cors import CORS
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

app = Flask(__name__)
CORS(app)

load_dotenv()

# Configure OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),  # Never hardcode API keys!
)

redis_client = redis.Redis(host='localhost', port=6379, db=0)
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
    "learning_resources": [
        {
            "skill": "missing skill name",
            "youtube_search_query": "best tutorial playlist for [skill] beginners",
            "description": "Brief description of what to learn"
        }
    ],
    "summary": "Brief overall assessment"
}

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
    raw_text = extract_text_from_pdf(file)
    
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
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)
    return None

def cache_result(cache_key, result):
    """Cache analysis result"""
    redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))


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
        
        # Return complete response
        return jsonify({
            "success": True,
            "target_role": target_role,
            "candidate_info": structured_data["candidate_info"],
            "detected_skills": structured_data["detected_skills"],
            "analysis": analysis
        })
    
    except Exception as e:
        return jsonify({
            "error": "Failed to analyze resume",
            "details": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
