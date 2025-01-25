import streamlit as st
from backend.data_manager import load_positions
from backend.analysis_engine import parse_resume, analyze_resume
from backend.email_service import send_email
from backend.security import hash_data, generate_auth_token
from utils.validators import validate_candidate_info
from utils.session_manager import initialize_session  # Import from utils
import uuid
import os
import random
from datetime import datetime
from backend.data_manager import load_positions
from config.settings import RESUMES_DIR


# Load positions configuration
POSITION_CONFIG = load_positions()

def render_registration():
    """Enhanced registration form with validation"""
    state = initialize_session()
    
    with st.form("reg_form", clear_on_submit=False):
        st.header("📝 Candidate Registration")
        
        col1, col2 = st.columns(2)
        state.user_info["name"] = col1.text_input("Full Name*", value=state.user_info["name"])
        state.user_info["email"] = col2.text_input("Email*", value=state.user_info["email"])
        state.user_info["phone"] = st.text_input("Phone Number*", value=state.user_info["phone"])
        
        col1, col2 = st.columns(2)
        state.position = col1.selectbox("Position*", list(POSITION_CONFIG.keys()))
        state.user_info["experience"] = col2.number_input(
            "Experience (Years)*", 
            min_value=0,
            value=state.user_info["experience"]
        )
        
        resume = st.file_uploader("Upload Resume (PDF/DOCX)", type=["pdf", "docx"])
        if resume:
            state.user_info["resume_path"] = f"{RESUMES_DIR}/{state.user_info['name']}_{uuid.uuid4().hex[:6]}.{resume.type.split('/')[-1]}"
            with open(state.user_info["resume_path"], "wb") as f:
                f.write(resume.getbuffer())
            
            resume_text = parse_resume(resume)
            if resume_text:
                resume_data = analyze_resume(resume_text, state.position)
                state.user_info.update(resume_data)
                
                exp_diff = abs(state.user_info["experience"] - resume_data["experience"])
                state.user_info["experience_mismatch"] = exp_diff > 0
                
                st.subheader("📄 Resume Analysis")
                
                cols = st.columns(3)
                cols[0].metric("Compatibility", f"{resume_data['resume_score']}%")
                cols[1].metric("Required Skills", f"{len(resume_data['required_matches'])}/{len(POSITION_CONFIG[state.position]['required_skills'])}")
                cols[2].metric("Preferred Skills", len(resume_data['preferred_matches']))
                
                with st.expander("Detailed Analysis"):
                    st.write("**Required Skills Found:**")
                    st.write(", ".join(resume_data["required_matches"]) or "None")
                    st.write("**Preferred Skills Found:**")
                    st.write(", ".join(resume_data["preferred_matches"]) or "None")
                    st.write(f"**Resume Experience:** {resume_data['experience']} years")
                    
                    if state.user_info["experience_mismatch"]:
                        st.warning(f"⚠️ Experience mismatch: Resume shows {resume_data['experience']} years vs entered {state.user_info['experience']} years")
                
                st.progress(min(resume_data["resume_score"] / 100, 1.0))

        submitted = st.form_submit_button("Start Interview")
        if submitted:
            state.validation_errors = validate_candidate_info(state.user_info)
            
            if not state.validation_errors:
                if state.user_info["experience"] < POSITION_CONFIG[state.position]["experience_threshold"]:
                    state.validation_errors.append(
                        f"Minimum experience required: {POSITION_CONFIG[state.position]['experience_threshold']} years"
                    )
            
            if not state.validation_errors:
                tech_q = POSITION_CONFIG[state.position]["technical"]
                behave_q = POSITION_CONFIG[state.position]["behavioral"]
                combined_questions = tech_q + behave_q
                sample_size = min(5, len(combined_questions))
                
                if len(combined_questions) == 0:
                    state.validation_errors.append("No interview questions configured for this position")
                else:
                    state.questions = random.sample(combined_questions, k=sample_size)
                    state.stage = "interview"
                    
                    html_content = create_resume_scorecard(state.user_info, state.position)
                    send_email(
                        state.user_info["email"],
                        "Interview Started",
                        f"Hi {state.user_info['name']},\n\nYour {state.position} interview has begun!",
                        html_content
                    )
                    st.rerun()

    if state.validation_errors:
        st.error("Please fix the following issues:")
        for error in state.validation_errors:
            st.write(f"- {error}")

def render_interview():
    """Enhanced interview interface with time management"""
    state = initialize_session()
    
    st.title(f"🔍 {state.position} Interview - {state.user_info['name']}")
    st.markdown(f"**Interview ID:** `{state.user_info['interview_id']}`")
    
    elapsed_time = datetime.now() - state.question_start_time
    time_left = max(120 - elapsed_time.total_seconds(), 0)
    mins, secs = divmod(int(time_left), 60)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Time Remaining:** {mins:02d}:{secs:02d}")
    with col2:
        progress = state.current_qindex / len(state.questions)
        st.progress(min(progress, 1.0), text=f"Question {state.current_qindex+1}/{len(state.questions)}")

    if state.current_qindex < len(state.questions):
        question, keywords = state.questions[state.current_qindex]
        
        with st.form(f"q_{state.current_qindex}"):
            st.subheader("Current Question")
            st.markdown(f"**{question}**")
            st.caption(f"Key points to cover: {', '.join(keywords)}")
            
            answer = st.text_area("Your Answer", height=200, key=f"ans_{state.current_qindex}")
            
            if st.form_submit_button("Submit Answer"):
                found_keywords = [kw for kw in keywords if kw.lower() in answer.lower()]
                missing_keywords = [kw for kw in keywords if kw.lower() not in answer.lower()]
                
                state.answers.append((question, answer))
                state.current_qindex += 1
                state.question_start_time = datetime.now()
                
                if found_keywords:
                    st.success(f"✅ Covered keywords: {', '.join(found_keywords)}")
                if missing_keywords:
                    st.error(f"❌ Missing keywords: {', '.join(missing_keywords)}")
                
                st.rerun()
    else:
        st.balloons()
        st.success("🎉 Interview Completed!")
        
        report_data = {
            "Name": state.user_info["name"],
            "Email": state.user_info["email"],
            "Position": state.position,
            "Experience": state.user_info["experience"],
            "Resume Score": state.user_info["resume_score"],
            "Skills": ", ".join(state.user_info["skills"]) if state.user_info["skills"] else "",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Responses": "\n\n".join([f"Q: {q}\nA: {a}" for q, a in state.answers]),
            "Interview ID": state.user_info["interview_id"]
        }
        
        df = pd.DataFrame([report_data])
        if os.path.exists("results.xlsx"):
            existing_df = pd.read_excel("results.xlsx")
            df = pd.concat([existing_df, df], ignore_index=True)
        df.to_excel("results.xlsx", index=False)
        
        send_email(
            ADMIN_EMAIL,
            "New Interview Completed",
            f"Interview results for {state.user_info['name']} ({state.position})"
        )
        
        col1, col2 = st.columns(2)
        col1.download_button(
            "Download Report",
            data=df.to_csv(index=False),
            file_name="interview_report.csv"
        )
        if col2.button("Start New Interview"):
            st.session_state.clear()
            st.rerun()
