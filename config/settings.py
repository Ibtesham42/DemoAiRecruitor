import os

# ----------------- Configuration -----------------
RESUMES_DIR = "data/resumes"
POSITIONS_FILE = "data/positions/positions.json"
os.makedirs(RESUMES_DIR, exist_ok=True)

# Security Configuration
PEPPER = os.environ.get("PEPPER", "default-secret-pepper")

# Email Configuration
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_password"
ADMIN_EMAIL = "admin@example.com"

# Validation Constants
MIN_NAME_LENGTH = 3  # Ensure this is defined
MAX_EXPERIENCE = 20  # Ensure this is defined
VALID_PHONE_REGEX = r'^\+?[1-9]\d{1,14}$'  # Ensure this is defined
MAX_FILE_SIZE_MB = 5