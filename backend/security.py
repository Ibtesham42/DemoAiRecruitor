import hashlib
import os

def hash_data(data: str) -> str:
    """Secure hashing with pepper"""
    return hashlib.sha256((data + PEPPER).encode()).hexdigest()

def generate_auth_token(user_info: dict) -> str:
    """Generate secure auth token"""
    raw_token = f"{user_info['email']}{datetime.now().timestamp()}{PEPPER}"
    return hashlib.sha256(raw_token.encode()).hexdigest()