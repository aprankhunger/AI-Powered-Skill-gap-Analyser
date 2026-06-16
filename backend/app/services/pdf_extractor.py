import pdfplumber
import PyPDF2
from pdf2image import convert_from_bytes
import pytesseract
import re
import logging

logger = logging.getLogger(__name__)

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
        logger.warning(f"pdfplumber extraction failed: {str(e)}")
    
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
        logger.warning(f"PyPDF2 extraction failed: {str(e)}")
    
    # Method 3: OCR (for scanned PDFs)
    if not extraction_results or all(len(r["text"]) < 100 for r in extraction_results):
        try:
            logger.info("Attempting OCR extraction...")
            images = convert_from_bytes(file_bytes)
            text = ""
            for image in images:
                text += pytesseract.image_to_string(image) + "\n"
            if text.strip():
                extraction_results.append({"method": "OCR", "text": text})
        except Exception as e:
            logger.warning(f"OCR extraction failed: {str(e)}")
    
    # Return best result (longest text)
    if extraction_results:
        best = max(extraction_results, key=lambda x: len(x["text"]))
        logger.info(f"Successfully extracted text using {best['method']} (length: {len(best['text'])})")
        return {
            "text": best["text"],
            "method": best["method"],
            "confidence": "high" if len(best["text"]) > 500 else "medium" if len(best["text"]) > 100 else "low"
        }
    
    logger.error("All PDF extraction methods failed.")
    return {"text": "", "method": None, "confidence": "failed"}

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

def extract_skills_from_text(text):
    """Auto-detect technical skills from text"""
    skill_patterns = [
        r'\b(Python|Java|JavaScript|TypeScript|C\+\+|C#|Ruby|Go|Rust|PHP|Swift|Kotlin|Scala|R|MATLAB|Perl|SQL)\b',
        r'\b(React|Angular|Vue|Node\.js|Express|Django|Flask|Spring|\.NET|Rails|Laravel|FastAPI|Next\.js)\b',
        r'\b(MySQL|PostgreSQL|MongoDB|Redis|Oracle|SQLite|DynamoDB|Cassandra|Firebase|Elasticsearch)\b',
        r'\b(AWS|Azure|GCP|Docker|Kubernetes|Jenkins|Git|CI/CD|Terraform|Ansible)\b',
        r'\b(TensorFlow|PyTorch|Keras|Scikit-learn|Pandas|NumPy|Spark|Hadoop|Tableau|Power BI)\b',
        r'\b(Linux|Unix|Jira|Confluence|VS Code|IntelliJ|Eclipse)\b',
        r'\b(HTML|CSS|SASS|REST|GraphQL|API|JSON|XML|OAuth|JWT)\b',
        r'\b(Agile|Scrum|Kanban|DevOps|TDD|BDD|OOP|Microservices)\b'
    ]
    
    skills = set()
    search_text = text.upper() + " " + text
    
    for pattern in skill_patterns:
        matches = re.findall(pattern, search_text, re.IGNORECASE)
        skills.update(matches)
    
    return list(skills)

def structure_resume_data(file):
    """Structure resume data from PDF"""
    raw_result = extract_text_from_pdf(file)
    raw_text = raw_result["text"]
    
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
