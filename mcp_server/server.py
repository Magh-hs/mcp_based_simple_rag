#!/usr/bin/env python3
import asyncio
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
import uvicorn


class RAGMCPServer:
    """HTTP-based MCP server for RAG chatbot providing FAQ resources and prompts."""
    
    def __init__(self):
        self.app = FastAPI(title="RAG MCP Server", version="1.0.0")
        self.base_path = Path(__file__).parent
        self.setup_routes()
    
    def setup_routes(self):
        """Set up HTTP routes."""
        
        @self.app.get("/")
        async def root():
            return {"message": "RAG MCP Server is running", "version": "1.0.0"}
        
        @self.app.get("/health")
        async def health():
            return {"status": "healthy"}
        
        @self.app.get("/resources/faq")
        async def get_faq_content():
            """Get FAQ content."""
            faq_path = self.base_path / "resources" / "faq.txt"
            try:
                with open(faq_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content}
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"FAQ file not found at {faq_path}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading FAQ: {str(e)}")
        
        @self.app.get("/prompts/query_generate")
        async def get_query_prompt():
            """Get query generation prompt."""
            prompt_path = self.base_path / "prompts" / "query_generate.txt"
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content}
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"Query prompt file not found at {prompt_path}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading query prompt: {str(e)}")
        
        @self.app.get("/prompts/answer_generate")
        async def get_answer_prompt():
            """Get answer generation prompt."""
            prompt_path = self.base_path / "prompts" / "answer_generate.txt"
            try:
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {"content": content}
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=f"Answer prompt file not found at {prompt_path}")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error reading answer prompt: {str(e)}")


def main():
    """Main entry point for the MCP server."""
    server = RAGMCPServer()
    uvicorn.run(
        server.app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )


if __name__ == "__main__":
    main()