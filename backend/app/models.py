from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class MessageLog(Base):
    """Database model for logging user messages and responses."""
    __tablename__ = "message_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(Text, nullable=False)
    refined_query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    conversation_id = Column(String(100), nullable=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<MessageLog(id={self.id}, timestamp={self.timestamp})>"