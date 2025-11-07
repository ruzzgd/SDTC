from fastapi import APIRouter, Depends, Response, HTTPException, Cookie
from sqlalchemy.orm import Session
from DatabaseConnector import get_db
from database.UserTable import User, ProfileImage, UserStatus
from database.AdminTable import RecentActivity,CustomerFeedback
from models.AdminModel import ChangePasswordRequest
from models.UserModel import UserLogin, UserCreate, UserProfile, UploadProfileImage,FeedbackCreate,FeedbackOut
import tools
from typing import List
from datetime import datetime

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login")
def login_user(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(
        User.email == user.email,
        User.password == user.password
    ).first()
    
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if db_user.status == UserStatus.Banned:
        raise HTTPException(status_code=403, detail="Your account has been banned")

    # Log recent activity
    activity = RecentActivity(
        email=db_user.email,
        activity="Logged in to the system",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)
    db.commit()

    response.set_cookie(
        key="user_email",
        value=db_user.email,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "Logged in successfully"}


@router.post("/register")
def register_user(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(email=user.email, password=user.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create empty profile image record
    profile_image = ProfileImage(user_id=new_user.id, image_url="")
    db.add(profile_image)
    db.commit()

    # Log recent activity
    activity = RecentActivity(
        email=new_user.email,
        activity="Newly registered",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)
    db.commit()

    response.set_cookie(
        key="user_email",
        value=new_user.email,
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"id": new_user.id, "email": new_user.email}

# ---------------- User Profile ----------------
@router.get("/profile", response_model=UserProfile)
def get_user_profile(user_email: str = Cookie(None), db: Session = Depends(get_db)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    profile_image_url = user.profile_image.image_url if user.profile_image else ""
    return UserProfile(email=user.email, profile_picture=profile_image_url)


# ---------------- Update Profile Image ----------------
@router.post("/upload-profile-image")
def update_profile_image(
    profile_data: UploadProfileImage,
    user_email: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    image_url = profile_data.profile_image

    if not user.profile_image:
        new_image = ProfileImage(user_id=user.id, image_url=image_url)
        db.add(new_image)
    else:
        user.profile_image.image_url = image_url

    db.commit()
    return {"message": "Profile image updated successfully", "image_url": image_url}


# ---------------- Submit Feedback ----------------
@router.post("/feedback", response_model=FeedbackOut)
def submit_feedback(
    feedback: FeedbackCreate,
    user_email: str = Cookie(None),
    db: Session = Depends(get_db)
):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    new_feedback = CustomerFeedback(
        email=user_email,
        description=feedback.description,
        rating=feedback.rating,
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


# ---------------- Get All Feedback ----------------
@router.get("/feedback", response_model=List[FeedbackOut])
def get_feedback(db: Session = Depends(get_db)):
    feedbacks = db.query(CustomerFeedback).order_by(CustomerFeedback.created_at.desc()).all()
    return feedbacks


# ---------------- Logout User ----------------
@router.post("/logout")
def logout_user(response: Response, user_email: str = Cookie(None)):
    if not user_email:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Clear the cookie
    response.delete_cookie(
        key="user_email",
        httponly=True,
        secure=False,
        samesite="lax"
    )

    return {"message": "Logged out successfully"}


@router.post("/change-password")
def change_password(data: ChangePasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the password
    user.password = data.new_password
    db.commit()

    # Log recent activity
    activity = RecentActivity(
        email=user.email,
        activity="Changed account password",
        created_at=datetime.now(tools.PH_TZ)
    )
    db.add(activity)
    db.commit()

    return {"message": "Password changed successfully"}