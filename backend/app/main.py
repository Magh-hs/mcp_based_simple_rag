import os
import uuid
from datetime import datetime
from typing import List
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .database import get_async_db, create_tables
from .models import MessageLog
from .schemas import (
    QueryGenerateRequest, QueryGenerateResponse,
    AnswerGenerateRequest, AnswerGenerateResponse,
    ChatRequest, ChatResponse, MessageLog as MessageLogSchema
)
from .services.llm_service import llm_service
from .services.mcp_client import mcp_client

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="A RAG-based chatbot API with MCP integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup."""
    create_tables()


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await mcp_client.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "RAG Chatbot API is running"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.utcnow()}


@app.post("/query_generate", response_model=QueryGenerateResponse)
async def query_generate(request: QueryGenerateRequest):
    """Generate refined query from user query and conversation history."""
    try:
        # Get query generation prompt from MCP server
        prompt_template = await mcp_client.get_query_prompt()
        
        # Generate refined query using LLM
        refined_query = await llm_service.generate_query(
            user_query=request.user_query,
            conversation_history=request.conversation_history,
            prompt_template=prompt_template
        )
        
        return QueryGenerateResponse(
            refined_query=refined_query,
            original_query=request.user_query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query generation failed: {str(e)}")


@app.post("/answer_generate", response_model=AnswerGenerateResponse)
async def answer_generate(request: AnswerGenerateRequest):
    """Generate answer from refined query and FAQ content."""
    try:
        # Get FAQ content and answer generation prompt from MCP server
        faq_content = await mcp_client.get_faq_content()
        prompt_template = await mcp_client.get_answer_prompt()
        
        # Generate answer using LLM
        answer = await llm_service.generate_answer(
            refined_query=request.refined_query,
            faq_content=faq_content,
            prompt_template=prompt_template
        )
        
        return AnswerGenerateResponse(
            answer=answer,
            refined_query=request.refined_query,
            original_query=request.original_query
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Answer generation failed: {str(e)}")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, db: AsyncSession = Depends(get_async_db)):
    """Complete chat pipeline: query generation + answer generation + logging."""
    try:
        # Step 1: Generate refined query
        query_request = QueryGenerateRequest(
            user_query=request.user_query,
            conversation_history=request.conversation_history
        )
        query_response = await query_generate(query_request)
        
        # Step 2: Generate answer
        answer_request = AnswerGenerateRequest(
            refined_query=query_response.refined_query,
            original_query=request.user_query,
            conversation_history=request.conversation_history
        )
        answer_response = await answer_generate(answer_request)
        
        # Step 3: Log to database
        conversation_id = str(uuid.uuid4())
        message_log = MessageLog(
            user_query=request.user_query,
            refined_query=query_response.refined_query,
            answer=answer_response.answer,
            conversation_id=conversation_id,
            timestamp=datetime.utcnow()
        )
        
        db.add(message_log)
        await db.commit()
        await db.refresh(message_log)
        
        return ChatResponse(
            answer=answer_response.answer,
            refined_query=query_response.refined_query,
            original_query=request.user_query,
            conversation_id=conversation_id
        )
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@app.get("/messages", response_model=List[MessageLogSchema])
async def get_messages(
    limit: int = 100,
    offset: int = 0,
    conversation_id: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get logged messages with optional filtering."""
    try:
        query = select(MessageLog).order_by(MessageLog.timestamp.desc())
        
        if conversation_id:
            query = query.where(MessageLog.conversation_id == conversation_id)
        
        query = query.offset(offset).limit(limit)
        
        result = await db.execute(query)
        messages = result.scalars().all()
        
        return [MessageLogSchema.from_orm(msg) for msg in messages]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch messages: {str(e)}")


@app.get("/messages/count")
async def get_message_count(
    conversation_id: str = None,
    db: AsyncSession = Depends(get_async_db)
):
    """Get total count of logged messages."""
    try:
        from sqlalchemy import func
        
        query = select(func.count(MessageLog.id))
        
        if conversation_id:
            query = query.where(MessageLog.conversation_id == conversation_id)
        
        result = await db.execute(query)
        count = result.scalar()
        
        return {"count": count}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to count messages: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)