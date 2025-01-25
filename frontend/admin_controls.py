import os
import streamlit as st
from backend.data_manager import load_positions, save_positions
import pandas as pd
from config.settings import RESUMES_DIR

def render_admin_panel():
    """Enhanced admin panel with position management"""
    POSITION_CONFIG = load_positions()  # Load POSITION_CONFIG at the start
    st.header("🔧 Admin Panel")
    
    with st.expander("🛠 Position Management", expanded=True):
        action = st.radio("Position Action", ["Create New", "Edit Existing"], horizontal=True, key="pos_action")
        
        if action == "Create New":
            st.subheader("Create New Position")
            new_position = st.text_input("Position Name*", key="new_pos_name")
            
            col1, col2 = st.columns(2)
            new_required = col1.text_input("Required Skills* (comma-separated)", key="new_req_skills")
            new_preferred = col2.text_input("Preferred Skills (comma-separated)", key="new_pref_skills")
            
            st.subheader("Technical Questions")
            tech_q = st.text_area(
                "Format: 'Question|keyword1, keyword2' (one per line)",
                height=150,
                key="tech_q_create"
            )
            
            st.subheader("Behavioral Questions")
            behave_q = st.text_area(
                "Format: 'Question|keyword1, keyword2' (one per line)",
                height=150,
                key="behave_q_create"
            )
            
            exp_threshold = st.number_input("Experience Threshold*", min_value=0, key="new_exp_thresh")
            
            if st.button("Create Position", key="create_pos_btn"):
                validation = []
                if not new_position:
                    validation.append("Position name is required")
                if not new_required:
                    validation.append("Required skills are mandatory")
                if not tech_q:
                    validation.append("Technical questions required")
                if not behave_q:
                    validation.append("Behavioral questions required")
                
                if validation:
                    st.error("Validation errors:\n- " + "\n- ".join(validation))
                else:
                    # Process questions
                    technical = []
                    for line in tech_q.split('\n'):
                        if '|' in line:
                            q, kw = line.split('|', 1)
                            technical.append([q.strip(), [k.strip() for k in kw.split(',')]])
                    
                    behavioral = []
                    for line in behave_q.split('\n'):
                        if '|' in line:
                            q, kw = line.split('|', 1)
                            behavioral.append([q.strip(), [k.strip() for k in kw.split(',')]])
                    
                    POSITION_CONFIG[new_position] = {
                        "required_skills": [s.strip() for s in new_required.split(',')],
                        "preferred_skills": [s.strip() for s in new_preferred.split(',')] if new_preferred else [],
                        "technical": technical,
                        "behavioral": behavioral,
                        "experience_threshold": exp_threshold
                    }
                    save_positions(POSITION_CONFIG)
                    st.success(f"Position '{new_position}' created successfully!")
        
        else:  # Edit Existing
            position = st.selectbox("Select Position", list(POSITION_CONFIG.keys()), key="pos_select")
            config = POSITION_CONFIG[position]
            
            col1, col2 = st.columns(2)
            new_required = col1.text_input(
                "Required Skills",
                value=", ".join(config["required_skills"]),
                key=f"req_{position}"
            )
            new_preferred = col2.text_input(
                "Preferred Skills", 
                value=", ".join(config["preferred_skills"]),
                key=f"pref_{position}"
            )
            
            st.subheader("Technical Questions")
            tech_q = '\n'.join([f"{q[0]}|{', '.join(q[1])}" for q in config["technical"]])
            updated_tech = st.text_area(
                "Technical Questions",
                value=tech_q,
                height=150,
                key=f"tech_edit_{position}"
            )
            
            st.subheader("Behavioral Questions")
            behave_q = '\n'.join([f"{q[0]}|{', '.join(q[1])}" for q in config["behavioral"]])
            updated_behave = st.text_area(
                "Behavioral Questions",
                value=behave_q,
                height=150,
                key=f"behave_edit_{position}"
            )
            
            new_exp = st.number_input(
                "Experience Threshold",
                value=config["experience_threshold"],
                key=f"exp_{position}"
            )
            
            if st.button("Update Position", key=f"update_{position}"):
                # Process technical questions
                technical = []
                for line in updated_tech.split('\n'):
                    if '|' in line:
                        q, kw = line.split('|', 1)
                        technical.append([q.strip(), [k.strip() for k in kw.split(',')]])
                
                # Process behavioral questions
                behavioral = []
                for line in updated_behave.split('\n'):
                    if '|' in line:
                        q, kw = line.split('|', 1)
                        behavioral.append([q.strip(), [k.strip() for k in kw.split(',')]])
                
                POSITION_CONFIG[position] = {
                    "required_skills": [s.strip() for s in new_required.split(',')],
                    "preferred_skills": [s.strip() for s in new_preferred.split(',')] if new_preferred else [],
                    "technical": technical,
                    "behavioral": behavioral,
                    "experience_threshold": new_exp
                }
                save_positions(POSITION_CONFIG)
                st.success("Position updated successfully!")
    
    with st.expander("📊 Database Management"):
        if os.path.exists("results.xlsx"):
            df = pd.read_excel("results.xlsx")
            st.subheader("Candidate Records")
            st.dataframe(df)
            
            cols = st.columns(3)
            if cols[0].button("Refresh Data", key="refresh_data"):
                st.rerun()
            
            if cols[1].button("Download Full Data", key="download_data"):
                st.download_button(
                    label="Download CSV",
                    data=df.to_csv(index=False),
                    file_name="candidate_records.csv"
                )
            
            if cols[2].button("Purge All Data", key="purge_data"):
                try:
                    os.remove("results.xlsx")
                    st.success("Database cleared successfully!")
                except Exception as e:
                    st.error(f"Error clearing database: {str(e)}")
        else:
            st.warning("No candidate records found")
    
    with st.expander("🔐 System Controls"):
        st.subheader("Server Monitoring")
        st.write(f"Resumes Directory: {len(os.listdir(RESUMES_DIR))} files")
        st.write(f"Positions Configured: {len(POSITION_CONFIG)}")
        
        if st.button("Restart Service", key="restart_service"):
            st.rerun()  