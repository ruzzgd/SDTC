from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from DatabaseConnector import get_db
from database.UserTable import User
from database.AdminTable import Admin
from database.EmailVeificationTable import EmailCode
from models.EmailModel import SendCodeRequest, VerifyCodeRequest
from EmailAuth import send_email
import random
import tools
router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/send-code")
def send_code(data: SendCodeRequest, db: Session = Depends(get_db)):

    # Determine table
    if data.role == "user":
        account = db.query(User).filter(User.email == data.email).first()
        if data.purpose == "register" and account:
            raise HTTPException(status_code=400, detail="Email already exists")
    elif data.role == "admin":
        account = db.query(Admin).filter(Admin.email == data.email).first()
        if data.purpose == "reset" and not account:
            raise HTTPException(status_code=404, detail="Admin not found")
    else:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Generate code
    code = str(random.randint(100000, 999999))
    expires_at = datetime.now(tools.PH_TZ) + timedelta(minutes=5)

    # Check if code already exists for this email+role
    email_code = db.query(EmailCode).filter(
        EmailCode.email == data.email,
        EmailCode.role == data.role
    ).first()

    if email_code:
        email_code.code = code
        email_code.expires_at = expires_at
    else:
        email_code = EmailCode(email=data.email, role=data.role, code=code, expires_at=expires_at)
        db.add(email_code)

    db.commit()
    send_email(data.email, code, purpose=data.purpose) 

    return {"message": f"Verification code sent to {data.role} email"}

@router.post("/verify-code")
def verify_code(data: VerifyCodeRequest, db: Session = Depends(get_db)):

    email_code = db.query(EmailCode).filter(
        EmailCode.email == data.email,
        EmailCode.role == data.role
    ).first()

    if not email_code or email_code.code != data.code:
        raise HTTPException(status_code=400, detail="Invalid code")

    if email_code.is_expired():
        raise HTTPException(status_code=400, detail="Code expired")

    db.delete(email_code)
    db.commit()

    return {"message": f"{data.role.capitalize()} email verified successfully"}
