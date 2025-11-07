import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
from dotenv import load_dotenv

load_dotenv() 

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    """
    Create Gmail API service using OAuth2 refresh token.
    """
    creds = Credentials(
        None,
        refresh_token=os.getenv("GMAIL_REFRESH_TOKEN"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GMAIL_CLIENT_ID"),
        client_secret=os.getenv("GMAIL_CLIENT_SECRET"),
        scopes=SCOPES
    )
    service = build("gmail", "v1", credentials=creds)
    return service

def send_email(to_email: str, code: str, purpose: str = "register"):
    """
    Send a verification email via Gmail API with SDTC-style design.
    """
    sender_email = os.getenv("SENDER_EMAIL")
    
    # Email content based on purpose
    if purpose == "register":
        subject = "SDTC - Verify Your Email"
        heading = "Welcome to SDTC"
        body_text = "Thank you for signing up with SDTC!"
    elif purpose == "reset":
        subject = "SDTC - Password Reset Verification Code"
        heading = "Password Reset Request"
        body_text = "You requested to reset your password. Use this code to proceed."
    else:
        subject = "SDTC - Verification Code"
        heading = "Email Verification"
        body_text = "Use the verification code below to continue."

    # Plain text fallback
    text = f"[SDTC] Your verification code is: {code}"

    # HTML email content
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
          <h2 style="color: #4CAF50; text-align: center;">{heading}</h2>
          <p style="font-size: 16px; color: #333;">Hello,</p>
          <p style="font-size: 16px; color: #333;">
            {body_text}<br>
            Your verification code is:
          </p>
          <div style="text-align: center; margin: 20px 0;">
            <span style="font-size: 24px; font-weight: bold; color: #4CAF50; letter-spacing: 4px;">
              {code}
            </span>
          </div>
          <p style="font-size: 14px; color: #777;">
            If you didn’t request this code, please ignore this email.
          </p>
          <p style="font-size: 14px; color: #999; text-align: center; margin-top: 20px;">
            © {datetime.datetime.now().year} SDTC. All rights reserved.
          </p>
        </div>
      </body>
    </html>
    """

    # Create MIME message
    msg = MIMEMultipart("alternative")
    msg["From"] = f"SDTC <{sender_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(text, "plain"))
    msg.attach(MIMEText(html, "html"))

    # Encode and send
    try:
        raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service = get_gmail_service()
        service.users().messages().send(userId="me", body={"raw": raw_message}).execute()
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
