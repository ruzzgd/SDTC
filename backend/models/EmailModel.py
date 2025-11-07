from pydantic import BaseModel, EmailStr

class SendCodeRequest(BaseModel):
    email: EmailStr
    role: str 
    purpose: str = "register"
    
class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: str
    role: str 
