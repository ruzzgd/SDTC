from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from DatabaseConnector import Base
import enum
import tools
from datetime import datetime
# Updated enum with Active / Banned
class UserStatus(str, enum.Enum):
    Active = "active"
    Banned = "banned"

# ---------------- USER ----------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(tools.PH_TZ))
    status = Column(Enum(UserStatus), default=UserStatus.Active, nullable=False)

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    profile_image = relationship("ProfileImage", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Address(Base):
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    house_number = Column(String, nullable=True)
    street = Column(String, nullable=False)
    barangay = Column(String, nullable=True)
    city = Column(String, nullable=False)
    province = Column(String, nullable=True)
    is_active = Column(Boolean, default=False)

    user = relationship("User", back_populates="addresses")
    

class ProfileImage(Base):
    __tablename__ = "profile_images"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    image_url = Column(String, nullable=False)  
    user = relationship("User", back_populates="profile_image")
