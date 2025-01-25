import streamlit as st
import pandas as pd
import os

def candidate_portal():
    """Candidate self-service portal"""
    st.header("👤 Candidate Portal")
    
    with st.form("auth_form"):
        email = st.text_input("Enter your email")
        interview_id = st.text_input("Enter interview ID")
        
        if st.form_submit_button("View History"):
            if os.path.exists("results.xlsx"):
                df = pd.read_excel("results.xlsx")
                if 'Interview ID' in df.columns and 'Email' in df.columns:
                    filtered = df[(df["Email"] == email) & (df["Interview ID"] == interview_id)]
                    
                    if not filtered.empty:
                        st.success("Authentication successful!")
                        st.dataframe(filtered)
                    else:
                        st.error("No records found")
                else:
                    st.error("Required columns missing in data")
            else:
                st.warning("No interview data available")