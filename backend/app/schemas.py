from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class ConversationMessage(BaseModel):
    """Single message in conversation history."""
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: Optional[datetime] = None


class QueryGenerateRequest(BaseModel):
    """Request for query generation endpoint."""
    user_query: str
    conversation_history: List[ConversationMessage] = []


class QueryGenerateResponse(BaseModel):
    """Response from query generation endpoint."""
    refined_query: str
    original_query: str


class AnswerGenerateRequest(BaseModel):
    """Request for answer generation endpoint."""
    refined_query: str
    original_query: str
    conversation_history: List[ConversationMessage] = []


class AnswerGenerateResponse(BaseModel):
    """Response from answer generation endpoint."""
    answer: str
    refined_query: str
    original_query: str


class ChatRequest(BaseModel):
    """Complete chat request combining both endpoints."""
    user_query: str
    conversation_history: List[ConversationMessage] = []


class ChatResponse(BaseModel):
    """Complete chat response."""
    answer: str
    refined_query: str
    original_query: str
    conversation_id: Optional[str] = None


class MessageLog(BaseModel):
    """Database model for message logging."""
    id: Optional[int] = None
    user_query: str
    refined_query: str
    answer: str
    conversation_id: Optional[str] = None
    timestamp: datetime
    
    class Config:
        from_attributes = True