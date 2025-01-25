import os
import uuid
from typing import Optional

def save_resume(file, candidate_name: str) -> Optional[str]:
    """Save uploaded resume to disk"""
    try:
        file_extension = file.type.split('/')[-1]
        file_path = f"{RESUMES_DIR}/{candidate_name}_{uuid.uuid4().hex[:6]}.{file_extension}"
        with open(file_path, "wb") as f:
            f.write(file.getbuffer())
        return file_path
    except Exception as e:
        st.error(f"Error saving resume: {str(e)}")
        return None