from pydantic import BaseModel, EmailStr,Field
from typing import Optional
from datetime import datetime
class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UploadProfileImage(BaseModel):
    profile_image:str

class Address(BaseModel):
    house_number: str
    street: str
    barangay:str
    city:str
    province:str

class AddressResponse(Address):
    id:int
    is_active:bool
    class Config:
        from_attributes = True
class ActivateAddress(BaseModel):
    is_active: bool

class UserProfile(BaseModel):
    email: EmailStr
    profile_picture: str

class FeedbackCreate(BaseModel):
    description: str = Field(..., min_length=1)
    rating: int = Field(..., ge=1, le=5)

class FeedbackOut(BaseModel):
    id: int
    email: str
    description: str
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True
