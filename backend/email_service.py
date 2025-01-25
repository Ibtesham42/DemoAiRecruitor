from typing import Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st

def send_email(recipient: str, subject: str, body: str, html: Optional[str] = None):
    """Enhanced email with HTML support"""
    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = subject
        
        part1 = MIMEText(body, 'plain')
        msg.attach(part1)
        
        if html:
            part2 = MIMEText(html, 'html')
            msg.attach(part2)
            
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        st.error(f"Email error: {str(e)}")