import asyncio
import json
from typing import Dict, Any
import httpx


class MCPClient:
    """Client for communicating with the MCP server."""
    
    def __init__(self, mcp_server_url: str = "http://mcp_server:8001"):
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient()
    
    async def get_faq_content(self) -> str:
        """Get FAQ content from MCP server."""
        try:
            # For now, we'll implement a simple HTTP interface to the MCP server
            # In a production setup, you'd use proper MCP protocol
            response = await self.client.get(f"{self.mcp_server_url}/resources/faq")
            response.raise_for_status()
            return response.text
        except Exception as e:
            # Fallback to direct file reading if MCP server is not available
            import os
            from pathlib import Path
            
            # Try to read from local file system
            mcp_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "resources" / "faq.txt"
            if mcp_path.exists():
                with open(mcp_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise Exception(f"Could not get FAQ content: {e}")
    
    async def get_query_prompt(self) -> str:
        """Get query generation prompt from MCP server."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/prompts/query_generate")
            response.raise_for_status()
            return response.text
        except Exception as e:
            # Fallback to direct file reading
            import os
            from pathlib import Path
            
            mcp_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "prompts" / "query_generate.txt"
            if mcp_path.exists():
                with open(mcp_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise Exception(f"Could not get query prompt: {e}")
    
    async def get_answer_prompt(self) -> str:
        """Get answer generation prompt from MCP server."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/prompts/answer_generate")
            response.raise_for_status()
            return response.text
        except Exception as e:
            # Fallback to direct file reading
            import os
            from pathlib import Path
            
            mcp_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "prompts" / "answer_generate.txt"
            if mcp_path.exists():
                with open(mcp_path, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                raise Exception(f"Could not get answer prompt: {e}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global MCP client instance
mcp_client = MCPClient()