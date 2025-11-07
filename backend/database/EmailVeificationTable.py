from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from DatabaseConnector import Base
import tools

class EmailCode(Base):
    __tablename__ = "email_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    role = Column(String, nullable=False)
    code = Column(String, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)

    def is_expired(self):

        current_time = datetime.now(tools.PH_TZ)
        return current_time > self.expires_at
