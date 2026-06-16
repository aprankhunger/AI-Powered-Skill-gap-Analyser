import os
import json
import logging
import hashlib
import redis
from openai import OpenAI

logger = logging.getLogger(__name__)

# Redis setup
try:
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'), 
        port=int(os.getenv('REDIS_PORT', 6379)), 
        db=0
    )
    redis_client.ping()  # Test connection
    REDIS_AVAILABLE = True
    logger.info("Redis cache is available.")
except Exception as e:
    redis_client = None
    REDIS_AVAILABLE = False
    logger.warning(f"Redis not available. Caching disabled. Reason: {e}")

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
    
    # Sanitize target role to prevent basic prompt injection
    safe_target_role = str(target_role)[:200].replace("\n", " ").strip()
    
    prompt_parts.append(f"\n=== TARGET ROLE ===\n{safe_target_role}")
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

def get_cache_key(file_bytes, target_role):
    """Generate unique cache key based on file content and role"""
    content_hash = hashlib.sha256(file_bytes + str(target_role).encode()).hexdigest()
    return f"resume_analysis:{content_hash}"

def get_cached_result(cache_key):
    """Get cached analysis result"""
    if not REDIS_AVAILABLE:
        return None
    try:
        cached = redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Failed to get cache for {cache_key}: {e}")
    return None

def cache_result(cache_key, result):
    """Cache analysis result"""
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(result))
    except Exception as e:
        logger.warning(f"Failed to set cache for {cache_key}: {e}")

def get_openai_client():
    """Lazily load the OpenAI client to ensure app context and env vars are ready"""
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY environment variable is missing.")
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )

def analyze_resume_with_ai(structured_data, target_role):
    """Calls OpenRouter AI to analyze the structured resume data"""
    prompt = format_structured_data_for_ai(structured_data, target_role)
    client = get_openai_client()
    
    response = client.chat.completions.create(
        model="amazon/nova-micro-v1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
    )
    
    result = response.choices[0].message.content
    
    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.replace("```json", "").replace("```", "").strip()
        
        analysis = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI JSON response. Raw response: {result}")
        analysis = {
            "error": "Failed to parse AI response",
            "raw_response": result
        }
    
    if "learning_resources" in analysis:
        analysis["learning_resources"] = generate_youtube_links(analysis.get("learning_resources", []))
        
    return analysis
