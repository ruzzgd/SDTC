from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from DatabaseConnector import Base  
import tools
class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime,nullable=True)

class CustomerFeedback(Base):
    __tablename__ = "customer_feedback"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    description = Column(String, nullable=False)
    rating = Column(Integer,nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tools.PH_TZ))

class RecentActivity(Base):
    __tablename__ = "recent_activity"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    activity = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(tools.PH_TZ))