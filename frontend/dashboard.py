import streamlit as st
import pandas as pd
import os

def analytics_dashboard():
    """Advanced analytics dashboard"""
    st.header("📈 Advanced Analytics")
    
    if not os.path.exists("results.xlsx"):
        st.info("No data available")
        return
    
    df = pd.read_excel("results.xlsx")
    
    # Ensure required columns exist
    for col in ["Skills", "Interview ID"]:
        if col not in df.columns:
            df[col] = ""
    
    st.subheader("Summary Statistics")
    cols = st.columns(3)
    cols[0].metric("Total Candidates", len(df))
    cols[1].metric("Average Score", f"{df['Resume Score'].mean():.1f}%")
    cols[2].metric("Success Rate", f"{len(df[df['Resume Score'] >= 70])/len(df)*100:.1f}%")
    
    st.subheader("Temporal Analysis")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Hour"] = df["Timestamp"].dt.hour
    st.bar_chart(df["Hour"].value_counts())
    
    if "Skills" in df.columns and not df["Skills"].empty:
        st.subheader("Skill Distribution")
        all_skills = df["Skills"].str.split(", ").explode()
        st.bar_chart(all_skills.value_counts().head(10))
    else:
        st.warning("Skills data not available in historical records")