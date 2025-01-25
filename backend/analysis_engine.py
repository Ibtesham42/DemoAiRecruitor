import re
import PyPDF2
import docx
from io import BytesIO
from typing import Dict
from config.settings import MAX_FILE_SIZE_MB  # Import MAX_FILE_SIZE_MB
import streamlit as st  # Import Streamlit

def parse_resume(file) -> str:
    """Secure resume parsing with size validation"""
    try:
        max_size = MAX_FILE_SIZE_MB * 1024 * 1024
        if file.size > max_size:
            st.error(f"File too large. Max size: {MAX_FILE_SIZE_MB}MB")
            return ""

        if file.type == "application/pdf":
            with BytesIO(file.getbuffer()) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                return "".join(page.extract_text() for page in reader.pages)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return "\n".join(para.text for para in docx.Document(file).paragraphs)
        return ""
    except PyPDF2.errors.PdfReadError:
        st.error("Error: Could not read PDF file - may be corrupted or encrypted")
        return ""
    except Exception as e:
        st.error(f"Resume parsing error: {str(e)}")
        return ""

def analyze_resume(text: str, position: str) -> Dict:
    """Enhanced resume analysis with security checks"""
    sanitized_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    
    required_skills = POSITION_CONFIG[position]["required_skills"]
    preferred_skills = POSITION_CONFIG[position]["preferred_skills"]
    
    valid_skills = required_skills + preferred_skills
    found_skills = re.findall(
        r'\b(' + '|'.join(re.escape(skill) for skill in valid_skills) + r')\b',
        sanitized_text,
        re.IGNORECASE
    )
    normalized_skills = [skill.strip().title() for skill in found_skills]

    experience = 0
    try:
        exp_match = re.search(r'(\d+)\s*\+?\s*years?', sanitized_text, re.IGNORECASE)
        if exp_match:
            experience = int(exp_match.group(1))
    except ValueError:
        experience = 0

    required_matches = [skill for skill in normalized_skills if skill in required_skills]
    preferred_matches = [skill for skill in normalized_skills if skill in preferred_skills]
    
    base_score = (len(required_matches) / len(required_skills)) * 100 if required_skills else 0
    bonus_score = (len(preferred_matches) / len(preferred_skills)) * 20 if preferred_skills else 0
    total_score = max(0, min(base_score + bonus_score, 100))

    return {
        "skills": list(set(normalized_skills))[:8],
        "experience": experience,
        "resume_score": round(total_score, 1),
        "required_matches": required_matches,
        "preferred_matches": preferred_matches
    }