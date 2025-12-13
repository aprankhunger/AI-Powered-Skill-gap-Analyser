from flask import Flask, request, jsonify, render_template_string
import pdfplumber
from openai import OpenAI
import json
import re

app = Flask(__name__)

# Configure OpenRouter
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
)

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

BASE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }} - AI Resume Analyzer</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }
        
        .navbar {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
            position: fixed;
            width: 100%;
            top: 0;
            z-index: 1000;
        }
        
        .navbar-content {
            max-width: 1200px;
            margin: 0 auto;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .logo {
            font-size: 1.5rem;
            font-weight: 700;
            color: #667eea;
            text-decoration: none;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .logo-icon {
            font-size: 1.8rem;
        }
        
        .nav-links {
            display: flex;
            gap: 2rem;
            list-style: none;
        }
        
        .nav-links a {
            text-decoration: none;
            color: #555;
            font-weight: 500;
            transition: color 0.3s;
        }
        
        .nav-links a:hover {
            color: #667eea;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 100px 2rem 2rem;
        }
        
        .hero {
            text-align: center;
            padding: 4rem 0;
            color: white;
        }
        
        .hero h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 1rem;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }
        
        .hero p {
            font-size: 1.2rem;
            opacity: 0.9;
            max-width: 600px;
            margin: 0 auto;
        }
        
        .card {
            background: white;
            border-radius: 20px;
            padding: 2.5rem;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
            margin-top: 2rem;
        }
        
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 3rem;
            text-align: center;
            transition: all 0.3s;
            cursor: pointer;
            background: #fafafa;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background: #f0f0ff;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background: #f0f0ff;
            transform: scale(1.02);
        }
        
        .upload-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
        
        .upload-area h3 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .upload-area p {
            color: #777;
            font-size: 0.9rem;
        }
        
        .file-input {
            display: none;
        }
        
        .file-name {
            margin-top: 1rem;
            padding: 0.75rem 1.5rem;
            background: #e8f5e9;
            border-radius: 25px;
            color: #2e7d32;
            font-weight: 500;
            display: none;
        }
        
        .file-name.show {
            display: inline-block;
        }
        
        .form-group {
            margin-top: 2rem;
        }
        
        .form-group label {
            display: block;
            font-weight: 600;
            margin-bottom: 0.75rem;
            color: #333;
        }
        
        .form-group input[type="text"] {
            width: 100%;
            padding: 1rem 1.5rem;
            border: 2px solid #eee;
            border-radius: 12px;
            font-size: 1rem;
            transition: border-color 0.3s;
        }
        
        .form-group input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .btn {
            display: inline-block;
            padding: 1rem 2.5rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s, box-shadow 0.3s;
            margin-top: 2rem;
            width: 100%;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4);
        }
        
        .btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .btn-secondary {
            background: #f5f5f5;
            color: #667eea;
            border: 2px solid #667eea;
        }
        
        .btn-secondary:hover {
            background: #667eea;
            color: white;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-top: 3rem;
        }
        
        .feature-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            color: white;
            text-align: center;
        }
        
        .feature-icon {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .feature-card h3 {
            margin-bottom: 0.5rem;
        }
        
        .feature-card p {
            opacity: 0.8;
            font-size: 0.9rem;
        }
        
        .loading {
            display: none;
            text-align: center;
            padding: 2rem;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            width: 50px;
            height: 50px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 1rem;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .footer {
            text-align: center;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9rem;
        }
        
        /* Results Page Styles */
        .results-header {
            text-align: center;
            color: white;
            padding: 2rem 0;
        }
        
        .results-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }
        
        .score-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .score-card {
            background: white;
            border-radius: 15px;
            padding: 1.5rem;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .score-value {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .score-label {
            color: #777;
            font-size: 0.9rem;
            margin-top: 0.5rem;
        }
        
        .section {
            background: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }
        
        .section h2 {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 1.5rem;
            color: #333;
            font-size: 1.3rem;
        }
        
        .section-icon {
            font-size: 1.5rem;
        }
        
        .skill-tags {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
        }
        
        .skill-tag {
            padding: 0.5rem 1rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 25px;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        .skill-tag.missing {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
        }
        
        .skill-tag.soft {
            background: linear-gradient(135deg, #26de81 0%, #20bf6b 100%);
        }
        
        .suggestion-list {
            list-style: none;
        }
        
        .suggestion-list li {
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: flex-start;
            gap: 0.75rem;
        }
        
        .suggestion-list li::before {
            content: "💡";
            flex-shrink: 0;
        }
        
        .summary-box {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            font-size: 1.1rem;
            line-height: 1.6;
        }
        
        .action-buttons {
            display: flex;
            gap: 1rem;
            margin-top: 2rem;
        }
        
        .action-buttons .btn {
            flex: 1;
            margin-top: 0;
        }
        
        .resources-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1.5rem;
            margin-top: 1rem;
        }
        
        .resource-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border-radius: 12px;
            padding: 1.5rem;
            transition: transform 0.3s, box-shadow 0.3s;
        }
        
        .resource-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }
        
        .resource-skill {
            font-size: 1.2rem;
            font-weight: 700;
            color: #667eea;
            margin-bottom: 0.75rem;
        }
        
        .resource-description {
            color: #555;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            line-height: 1.5;
        }
        
        .youtube-link {
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
            padding: 0.75rem 1.5rem;
            background: #FF0000;
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: 600;
            font-size: 0.9rem;
            transition: background 0.3s, transform 0.2s;
        }
        
        .youtube-link:hover {
            background: #cc0000;
            transform: scale(1.05);
        }
        
        .yt-icon {
            font-size: 1.2rem;
        }

        @media (max-width: 768px) {
            .hero h1 {
                font-size: 2rem;
            }
            
            .card {
                padding: 1.5rem;
            }
            
            .upload-area {
                padding: 2rem;
            }
            
            .action-buttons {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <a href="/" class="logo">
                <span class="logo-icon">📄</span>
                ResumeAI
            </a>
            <ul class="nav-links">
                <li><a href="/">Home</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#about">About</a></li>
            </ul>
        </div>
    </nav>
    {{ content|safe }}
    <footer class="footer">
        <p>© 2025 ResumeAI - Powered by AI | Built with ❤️</p>
    </footer>
</body>
</html>
'''

HOME_CONTENT = '''
<div class="container">
    <div class="hero">
        <h1>🚀 AI Resume & Skill Gap Analyzer</h1>
        <p>Upload your resume and get instant AI-powered insights to land your dream job</p>
    </div>
    
    <div class="card">
        <form action="/analyze-resume" method="POST" enctype="multipart/form-data" id="uploadForm">
            <div class="upload-area" id="dropZone">
                <div class="upload-icon">📤</div>
                <h3>Drop your resume here</h3>
                <p>or click to browse (PDF only)</p>
                <input type="file" name="resume" accept=".pdf" required class="file-input" id="fileInput">
                <div class="file-name" id="fileName"></div>
            </div>
            
            <div class="form-group">
                <label for="target_role">🎯 Target Role</label>
                <input type="text" name="target_role" id="target_role" placeholder="e.g., Senior Software Engineer, Data Scientist, Product Manager" required>
            </div>
            
            <button type="submit" class="btn" id="submitBtn">
                ✨ Analyze My Resume
            </button>
            
            <div class="loading" id="loading">
                <div class="spinner"></div>
                <p>Analyzing your resume with AI magic... This may take a moment.</p>
            </div>
        </form>
    </div>
    
    <div class="features" id="features">
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <h3>Skill Extraction</h3>
            <p>Automatically identifies technical and soft skills from your resume</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h3>Gap Analysis</h3>
            <p>Compares your skills with job requirements to find gaps</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🎯</div>
            <h3>ATS Optimization</h3>
            <p>Get suggestions to pass Applicant Tracking Systems</p>
        </div>
        <div class="feature-card">
            <div class="feature-icon">💡</div>
            <h3>Smart Suggestions</h3>
            <p>Personalized recommendations to improve your resume</p>
        </div>
    </div>
</div>

<script>
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const fileName = document.getElementById('fileName');
    const form = document.getElementById('uploadForm');
    const loading = document.getElementById('loading');
    const submitBtn = document.getElementById('submitBtn');
    
    dropZone.addEventListener('click', () => fileInput.click());
    
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
            fileInput.files = e.dataTransfer.files;
            updateFileName();
        }
    });
    
    fileInput.addEventListener('change', updateFileName);
    
    function updateFileName() {
        if (fileInput.files.length) {
            fileName.textContent = '✅ ' + fileInput.files[0].name;
            fileName.classList.add('show');
        }
    }
    
    form.addEventListener('submit', () => {
        loading.classList.add('show');
        submitBtn.disabled = true;
        submitBtn.textContent = 'Analyzing...';
    });
</script>
'''

def extract_text_from_pdf(file):
    """Extract raw text from PDF"""
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def extract_email(text):
    """Extract email from text"""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    match = re.search(email_pattern, text)
    return match.group(0) if match else None


def extract_phone(text):
    """Extract phone number from text"""
    phone_patterns = [
        r'\+?1?[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
        r'\+?\d{10,12}',
        r'\d{3}[-.\s]\d{3}[-.\s]\d{4}'
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(0)
    return None


def extract_links(text):
    """Extract URLs like LinkedIn, GitHub, Portfolio"""
    url_pattern = r'https?://[^\s<>"\']+|www\.[^\s<>"\']+'
    urls = re.findall(url_pattern, text)
    
    links = {"linkedin": None, "github": None, "portfolio": None, "other": []}
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
    """Try to extract name from first few lines"""
    lines = text.strip().split('\n')[:5]
    for line in lines:
        line = line.strip()
        # Skip lines that look like contact info or headers
        if '@' in line or 'http' in line.lower() or len(line) < 2:
            continue
        if any(word in line.lower() for word in ['resume', 'cv', 'curriculum', 'phone', 'email', 'address']):
            continue
        # Check if line looks like a name (2-4 words, mostly letters)
        words = line.split()
        if 1 <= len(words) <= 4 and all(word.replace('.', '').replace('-', '').isalpha() for word in words):
            return line
    return None


def identify_section(line):
    """Identify which section a header belongs to"""
    line_lower = line.lower().strip()
    
    section_keywords = {
        "education": ["education", "academic", "qualification", "degree", "university", "college", "school"],
        "experience": ["experience", "employment", "work history", "professional experience", "career"],
        "skills": ["skills", "technical skills", "competencies", "technologies", "tools", "expertise"],
        "projects": ["projects", "personal projects", "academic projects", "portfolio"],
        "certifications": ["certification", "certificates", "licensed", "credentials"],
        "summary": ["summary", "objective", "profile", "about me", "professional summary"],
        "achievements": ["achievements", "accomplishments", "awards", "honors"],
        "languages": ["languages", "language proficiency"],
        "interests": ["interests", "hobbies", "activities"]
    }
    
    for section, keywords in section_keywords.items():
        if any(keyword in line_lower for keyword in keywords):
            return section
    return None


def parse_resume_sections(text):
    """Parse resume into structured sections"""
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
    
    current_section = "contact"  # Start with contact info at top
    contact_lines_count = 0
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if this line is a section header
        detected_section = identify_section(line)
        if detected_section:
            current_section = detected_section
            continue
        
        # First few lines are usually contact info
        if current_section == "contact" and contact_lines_count < 6:
            sections["contact"].append(line)
            contact_lines_count += 1
        else:
            if current_section == "contact":
                current_section = "other"
            sections[current_section].append(line)
    
    return sections


def extract_skills_from_text(text):
    """Extract common technical skills from text"""
    # Common technical skills to look for
    skill_patterns = [
        # Programming Languages
        r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|Scala|R|MATLAB|Perl|SQL)\b',
        # Frameworks & Libraries
        r'\b(React|Angular|Vue|Node\.?js|Express|Django|Flask|Spring|\.NET|Rails|Laravel|FastAPI|Next\.?js)\b',
        # Databases
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQLite|DynamoDB|Cassandra|Firebase|Elasticsearch)\b',
        # Cloud & DevOps
        r'\b(AWS|Azure|GCP|Google Cloud|Docker|Kubernetes|Jenkins|Git|CI/CD|Terraform|Ansible)\b',
        # Data Science & ML
        r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Spark|Hadoop|Tableau|Power BI)\b',
        # Tools
        r'\b(Linux|Unix|Windows|macOS|Jira|Confluence|Slack|VS Code|IntelliJ|Eclipse)\b',
        # Web Technologies
        r'\b(HTML|CSS|SASS|REST|GraphQL|API|JSON|XML|OAuth|JWT)\b',
        # Methodologies
        r'\b(Agile|Scrum|Kanban|DevOps|TDD|BDD|OOP|Microservices)\b'
    ]
    
    found_skills = set()
    text_to_search = text.upper() + " " + text  # Search both cases
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        found_skills.update(matches)
    
    return list(found_skills)


def structure_resume_data(file):
    """Main function to extract and structure resume data"""
    raw_text = extract_text_from_pdf(file)
    
    # Extract contact info
    email = extract_email(raw_text)
    phone = extract_phone(raw_text)
    links = extract_links(raw_text)
    name = extract_name(raw_text)
    
    # Parse sections
    sections = parse_resume_sections(raw_text)
    
    # Extract skills
    detected_skills = extract_skills_from_text(raw_text)
    
    # Build structured output
    structured_data = {
        "candidate_info": {
            "name": name,
            "email": email,
            "phone": phone,
            "linkedin": links["linkedin"],
            "github": links["github"],
            "portfolio": links["portfolio"]
        },
        "sections": {
            "summary": "\n".join(sections["summary"]) if sections["summary"] else None,
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
    
    return structured_data


def generate_youtube_links(learning_resources):
    """Generate YouTube search links for learning resources"""
    if not learning_resources:
        return '<p style="color: #777;">No learning resources available. Complete all skills - Great job!</p>'
    
    links_html = []
    for resource in learning_resources:
        skill = resource.get("skill", "Unknown Skill")
        query = resource.get("youtube_search_query", f"{skill} tutorial")
        description = resource.get("description", "Learn this skill")
        
        # URL encode the query for YouTube search
        encoded_query = query.replace(" ", "+")
        youtube_url = f"https://www.youtube.com/results?search_query={encoded_query}"
        
        links_html.append(f'''
            <div class="resource-card">
                <div class="resource-skill">{skill}</div>
                <p class="resource-description">{description}</p>
                <a href="{youtube_url}" target="_blank" class="youtube-link">
                    <span class="yt-icon">▶</span> Find Tutorials on YouTube
                </a>
            </div>
        ''')
    
    return "".join(links_html)


def format_structured_data_for_ai(structured_data, target_role):
    """Format structured data into a clear prompt for AI"""
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
        prompt_parts.append("\n".join(sections["experience"]))
    
    if sections["education"]:
        prompt_parts.append("\n=== EDUCATION ===")
        prompt_parts.append("\n".join(sections["education"]))
    
    if sections["skills_section"]:
        prompt_parts.append("\n=== SKILLS (from resume) ===")
        prompt_parts.append("\n".join(sections["skills_section"]))
    
    if structured_data["detected_skills"]:
        prompt_parts.append("\n=== AUTO-DETECTED TECHNICAL SKILLS ===")
        prompt_parts.append(", ".join(structured_data["detected_skills"]))
    
    if sections["projects"]:
        prompt_parts.append("\n=== PROJECTS ===")
        prompt_parts.append("\n".join(sections["projects"]))
    
    if sections["certifications"]:
        prompt_parts.append("\n=== CERTIFICATIONS ===")
        prompt_parts.append("\n".join(sections["certifications"]))
    
    if sections["achievements"]:
        prompt_parts.append("\n=== ACHIEVEMENTS ===")
        prompt_parts.append("\n".join(sections["achievements"]))
    
    prompt_parts.append(f"\n=== TARGET ROLE ===")
    prompt_parts.append(target_role)
    
    prompt_parts.append("\n=== TASK ===")
    prompt_parts.append("Analyze this resume for the target role. Provide skill gap analysis and improvement suggestions.")
    
    return "\n".join(prompt_parts)


@app.route("/analyze-resume", methods=["POST"])
def analyze_resume():
    if "resume" not in request.files:
        return jsonify({"error": "No resume uploaded"}), 400

    resume_file = request.files["resume"]
    target_role = request.form.get("target_role", "")

    # Extract structured data from resume
    structured_data = structure_resume_data(resume_file)
    
    # Format for AI
    prompt = format_structured_data_for_ai(structured_data, target_role)

    # Print extracted text to terminal
    # print("\n" + "="*60)
    # print("📄 EXTRACTED RESUME DATA SENT TO AI")
    # print("="*60)
    # print(prompt)
    # print("="*60 + "\n")

    response = client.chat.completions.create(
        model="amazon/nova-2-lite-v1:free",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    result = response.choices[0].message.content
    
    # Try to parse the JSON
    try:
        # Clean up the response - remove markdown code blocks if present
        clean_result = result.strip()
        if clean_result.startswith('```'):
            clean_result = clean_result.split('```')[1]
            if clean_result.startswith('json'):
                clean_result = clean_result[4:]
        clean_result = clean_result.strip()
        
        data = json.loads(clean_result)
    except:
        # If parsing fails, create a basic structure
        data = {
            "candidate_name": "Unknown",
            "experience_level": "Unknown",
            "years_of_experience": "Unknown",
            "technical_skills": [],
            "soft_skills": [],
            "missing_skills": [],
            "skill_match_percentage": 0,
            "ats_score": 0,
            "suggestions": {
                "ats_optimization": [],
                "skill_section": [],
                "project_section": [],
                "general": [result]
            },
            "learning_resources": [],
            "summary": "Could not parse AI response. Raw output included in general suggestions."
        }

    results_content = f'''
    <div class="container">
        <div class="results-header">
            <h1>📊 Analysis Complete!</h1>
            <p>Here's a detailed breakdown of your resume for <strong>{target_role}</strong></p>
        </div>
        
        <div class="score-cards">
            <div class="score-card">
                <div class="score-value">{data.get("skill_match_percentage", "N/A")}%</div>
                <div class="score-label">Skill Match</div>
            </div>
            <div class="score-card">
                <div class="score-value">{data.get("ats_score", "N/A")}%</div>
                <div class="score-label">ATS Score</div>
            </div>
            <div class="score-card">
                <div class="score-value">{data.get("experience_level", "N/A")}</div>
                <div class="score-label">Experience Level</div>
            </div>
            <div class="score-card">
                <div class="score-value">{data.get("years_of_experience", "N/A")}</div>
                <div class="score-label">Experience</div>
            </div>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">👤</span> Candidate Profile</h2>
            <div class="summary-box">
                <strong>{data.get("candidate_name", "Unknown")}</strong><br><br>
                {data.get("summary", "No summary available.")}
            </div>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">💻</span> Technical Skills Found</h2>
            <div class="skill-tags">
                {"".join([f'<span class="skill-tag">{skill}</span>' for skill in data.get("technical_skills", [])]) or '<span style="color: #777;">No technical skills identified</span>'}
            </div>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">🤝</span> Soft Skills Found</h2>
            <div class="skill-tags">
                {"".join([f'<span class="skill-tag soft">{skill}</span>' for skill in data.get("soft_skills", [])]) or '<span style="color: #777;">No soft skills identified</span>'}
            </div>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">⚠️</span> Missing Skills for {target_role}</h2>
            <div class="skill-tags">
                {"".join([f'<span class="skill-tag missing">{skill}</span>' for skill in data.get("missing_skills", [])]) or '<span style="color: #777;">No skill gaps identified - Great job!</span>'}
            </div>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">🎯</span> ATS Optimization Tips</h2>
            <ul class="suggestion-list">
                {"".join([f'<li>{tip}</li>' for tip in data.get("suggestions", {}).get("ats_optimization", [])]) or '<li>No specific ATS suggestions at this time.</li>'}
            </ul>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">📝</span> Skill Section Improvements</h2>
            <ul class="suggestion-list">
                {"".join([f'<li>{tip}</li>' for tip in data.get("suggestions", {}).get("skill_section", [])]) or '<li>No specific skill section suggestions at this time.</li>'}
            </ul>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">🚀</span> Project Section Improvements</h2>
            <ul class="suggestion-list">
                {"".join([f'<li>{tip}</li>' for tip in data.get("suggestions", {}).get("project_section", [])]) or '<li>No specific project section suggestions at this time.</li>'}
            </ul>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">💡</span> General Recommendations</h2>
            <ul class="suggestion-list">
                {"".join([f'<li>{tip}</li>' for tip in data.get("suggestions", {}).get("general", [])]) or '<li>No additional recommendations at this time.</li>'}
            </ul>
        </div>
        
        <div class="section">
            <h2><span class="section-icon">📺</span> Learning Resources - YouTube Tutorials</h2>
            <div class="resources-grid">
                {generate_youtube_links(data.get("learning_resources", []))}
            </div>
        </div>
        
        <div class="action-buttons">
            <a href="/" class="btn btn-secondary">← Analyze Another Resume</a>
        </div>
    </div>
    '''

    return render_template_string(BASE_TEMPLATE, title="Results", content=results_content)


@app.route("/")
def home():
    return render_template_string(BASE_TEMPLATE, title="Home", content=HOME_CONTENT)


if __name__ == "__main__":
    app.run(debug=True)
