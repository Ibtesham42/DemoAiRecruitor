import os
import uuid
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import PyPDF2
import docx
import re
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from io import BytesIO
import hashlib
import json

RESUMES_DIR = "resumes"
POSITIONS_FILE = "positions.json"
os.makedirs(RESUMES_DIR, exist_ok=True)

PEPPER = os.environ.get("PEPPER", "default-secret-pepper")
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_password"
ADMIN_EMAIL = "admin@example.com"

class InterviewState:
    def __init__(self):
        self.stage = "registration"
        self.questions = []
        self.answers = []
        self.current_qindex = 0
        self.position = ""
        self.user_info = {
            "name": "", "email": "", "phone": "", "experience": 0,
            "resume_path": "", "skills": [], "resume_score": 0,
            "experience_mismatch": False, "interview_id": str(uuid.uuid4())
        }
        self.question_start_time = datetime.now()
        self.validation_errors = []
        self.auth_token = ""

def load_positions():
    if not os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, 'w') as f:
            json.dump({
                "Data Scientist": {
                    "required_skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
                    "preferred_skills": ["TensorFlow", "PyTorch", "Big Data", "Cloud Computing"],
                    "technical": [
                        ["Explain bias-variance tradeoff", ["bias", "variance", "overfitting"]],
                        ["Handle missing data techniques", ["imputation", "deletion", "modeling"]],
                        ["Cross-validation methods", ["k-fold", "stratified", "time-series"]]
                    ],
                    "behavioral": [
                        ["Describe complex data analysis project", ["process", "tools", "results"]],
                        ["Stay updated with DS trends", ["courses", "research", "experiments"]],
                        ["Handle tight deadlines", ["prioritization", "communication", "tools"]]
                    ],
                    "experience_threshold": 2
                }
            }, f)
    
    with open(POSITIONS_FILE, 'r') as f:
        return json.load(f)

POSITION_CONFIG = load_positions()

def parse_resume(file):
    try:
        if file.type == "application/pdf":
            with BytesIO(file.getbuffer()) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                return "".join(page.extract_text() for page in reader.pages)
        elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return "\n".join(para.text for para in docx.Document(file).paragraphs)
        return ""
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return ""

def analyze_resume(text, position):
    sanitized_text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    required_skills = POSITION_CONFIG[position]["required_skills"]
    preferred_skills = POSITION_CONFIG[position]["preferred_skills"]
    found_skills = re.findall(r'\b(' + '|'.join(re.escape(skill) for skill in required_skills+preferred_skills) + r')\b', sanitized_text, re.IGNORECASE)
    normalized_skills = [skill.strip().title() for skill in found_skills]
    
    experience = 0
    exp_match = re.search(r'(\d+)\s*\+?\s*years?', sanitized_text, re.IGNORECASE)
    if exp_match: experience = int(exp_match.group(1))
    
    required_matches = [skill for skill in normalized_skills if skill in required_skills]
    preferred_matches = [skill for skill in normalized_skills if skill in preferred_skills]
    base_score = (len(required_matches)/len(required_skills))*100 if required_skills else 0
    total_score = max(0, min(base_score + (len(preferred_matches)/len(preferred_skills))*20 if preferred_skills else 0, 100))
    
    return {
        "skills": list(set(normalized_skills))[:8],
        "experience": experience,
        "resume_score": round(total_score, 1),
        "required_matches": required_matches,
        "preferred_matches": preferred_matches
    }

def render_registration():
    state = st.session_state.state
    with st.form("reg_form"):
        st.header("Candidate Registration")
        state.user_info["name"] = st.text_input("Full Name")
        state.user_info["email"] = st.text_input("Email")
        state.user_info["phone"] = st.text_input("Phone Number")
        state.position = st.selectbox("Position", list(POSITION_CONFIG.keys()))
        state.user_info["experience"] = st.number_input("Experience (Years)", min_value=0)
        
        resume = st.file_uploader("Upload Resume (PDF/DOCX)")
        if resume:
            state.user_info["resume_path"] = f"{RESUMES_DIR}/{state.user_info['name']}_{uuid.uuid4().hex[:6]}.{resume.type.split('/')[-1]}"
            with open(state.user_info["resume_path"], "wb") as f:
                f.write(resume.getbuffer())
            
            resume_data = analyze_resume(parse_resume(resume), state.position)
            state.user_info.update(resume_data)
            st.subheader("Resume Analysis")
            cols = st.columns(3)
            cols[0].metric("Score", f"{resume_data['resume_score']}%")
            cols[1].metric("Required Skills", f"{len(resume_data['required_matches'])}/{len(required_skills)}")
            cols[2].metric("Preferred Skills", len(resume_data['preferred_matches']))
        
        if st.form_submit_button("Start Interview"):
            state.stage = "interview"
            tech_q = POSITION_CONFIG[state.position]["technical"]
            behave_q = POSITION_CONFIG[state.position]["behavioral"]
            state.questions = random.sample(tech_q + behave_q, min(5, len(tech_q + behave_q)))
            st.rerun()

def render_interview():
    state = st.session_state.state
    st.title(f"{state.position} Interview")
    st.markdown(f"Interview ID: {state.user_info['interview_id']}")
    
    if state.current_qindex < len(state.questions):
        question, keywords = state.questions[state.current_qindex]
        with st.form(f"q_{state.current_qindex}"):
            st.subheader(question)
            answer = st.text_area("Your Answer")
            if st.form_submit_button("Submit"):
                state.answers.append((question, answer))
                state.current_qindex += 1
                st.rerun()
    else:
        st.balloons()
        st.success("Interview Completed!")
        report_data = {
            "Name": state.user_info["name"],
            "Email": state.user_info["email"],
            "Position": state.position,
            "Experience": state.user_info["experience"],
            "Resume Score": state.user_info["resume_score"],
            "Interview ID": state.user_info["interview_id"]
        }
        pd.DataFrame([report_data]).to_excel("results.xlsx", index=False, mode='a')

def main():
    st.set_page_config(page_title="AI Recruiter Pro", layout="wide")
    st.sidebar.title("Navigation")
    menu = st.sidebar.radio("Menu", ["Registration", "Interview", "Admin"])
    
    if 'state' not in st.session_state:
        st.session_state.state = InterviewState()
    
    if menu == "Registration":
        render_registration()
    elif menu == "Interview":
        if st.session_state.state.stage == "interview":
            render_interview()
        else:
            st.info("Complete registration first")
    elif menu == "Admin":
        st.header("Admin Panel")

if __name__ == "__main__":
    main()