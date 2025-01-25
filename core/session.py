import streamlit as st
from datetime import datetime
import uuid

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

def initialize_session():
    if 'state' not in st.session_state:
        st.session_state.state = InterviewState()
    return st.session_state.state