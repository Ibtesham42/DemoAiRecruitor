from typing import List
from config.settings import MIN_NAME_LENGTH, MAX_EXPERIENCE, VALID_PHONE_REGEX
import re

def validate_candidate_info(info: dict) -> List[str]:
    """Comprehensive candidate validation"""
    errors = []
    
    if len(info["name"]) < MIN_NAME_LENGTH:
        errors.append(f"Name must be at least {MIN_NAME_LENGTH} characters")
        
    email = info["email"].strip()
    if not re.match(r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email):
        errors.append("Invalid email format")
        
    if not re.match(VALID_PHONE_REGEX, info["phone"]):
        errors.append("Invalid phone number format")
        
    if info["experience"] > MAX_EXPERIENCE:
        errors.append(f"Experience cannot exceed {MAX_EXPERIENCE} years")
        
    return errors