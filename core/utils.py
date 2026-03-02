import google.generativeai as genai
import PyPDF2
import docx
import os
import json
import langdetect
from django.conf import settings

# Configure Gemini
# You should set GEMINI_API_KEY in your settings.py or environment
GEMINI_API_KEY = getattr(settings, "GEMINI_API_KEY", "YOUR_API_KEY")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    text = ""
    if ext == ".pdf":
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
    elif ext == ".docx":
        doc = docx.Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
    return text

def detect_language(text):
    try:
        return langdetect.detect(text)
    except:
        return "en"

def extract_json(response_text):
    """Robustly extract JSON from a string that might contain markdown or extra text."""
    try:
        # Try to find the first '{' or '[' and the last '}' or ']'
        start_idx = response_text.find('{')
        list_start_idx = response_text.find('[')
        
        if list_start_idx != -1 and (start_idx == -1 or list_start_idx < start_idx):
            start_idx = list_start_idx
            end_idx = response_text.rfind(']')
        else:
            end_idx = response_text.rfind('}')
            
        if start_idx != -1 and end_idx != -1:
            json_str = response_text[start_idx:end_idx + 1]
            return json.loads(json_str)
        return json.loads(response_text) # Fallback
    except Exception as e:
        print(f"JSON extraction failed: {e}")
        return None

def parse_resume_ai(text):
    prompt = f"""
    Analyze the following resume text and extract:
    1. Skills (as a comma-separated list)
    2. Projects (summary of key projects)
    3. Experience (summary of work history)
    4. Main language of the resume

    Return the result in JSON format with keys: skills, projects, experience, language.
    
    Resume Text:
    {text[:5000]}
    """
    try:
        response = model.generate_content(prompt)
        data = extract_json(response.text)
        return data if data else {"skills": "", "projects": "", "experience": "", "language": "en"}
    except Exception as e:
        print(f"AI Parsing Error: {e}")
        return {"skills": "", "projects": "", "experience": "", "language": "en"}

def evaluate_match_ai(candidate_data, job_requirements):
    prompt = f"""
    Compare the following candidate profile with the job requirements.
    Return a match score (0-100) and a brief reasoning.
    
    Candidate Skills: {candidate_data.get('skills')}
    Candidate Projects: {candidate_data.get('projects')}
    Job Requirements: {job_requirements}
    
    Return JSON: {{"score": 85, "reasoning": "..."}}
    """
    try:
        response = model.generate_content(prompt)
        data = extract_json(response.text)
        return data if data else {"score": 50, "reasoning": "Matching failed, default score applied."}
    except:
        return {"score": 50, "reasoning": "Matching failed, error occurred."}

def generate_questions_ai(candidate_data, job_title, language="en"):
    prompt = f"""
    Generate 5 technical multiple-choice questions for a {job_title} role.
    Target the questions based on these skills/projects: {candidate_data.get('skills')} {candidate_data.get('projects')}
    The language of the questions must be: {language}
    
    Format: JSON list of objects:
    [
      {{
        "text": "Question text...",
        "options": ["A) ...", "B) ...", "C) ...", "D) ..."],
        "answer": "A"
      }}
    ]
    """
    try:
        response = model.generate_content(prompt)
        data = extract_json(response.text)
        return data if data else []
    except Exception as e:
        print(f"Question Generation Error: {e}")
        return []

