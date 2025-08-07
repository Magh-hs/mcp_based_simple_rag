import asyncio
import json
from typing import Dict, Any
import httpx
import os
from pathlib import Path


class MCPClient:
    """Client for communicating with the MCP server."""
    
    def __init__(self, mcp_server_url: str = None):
        if mcp_server_url is None:
            mcp_server_url = os.getenv("MCP_SERVER_URL", "http://mcp_server:8001")
        self.mcp_server_url = mcp_server_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def get_faq_content(self) -> str:
        """Get FAQ content from MCP server."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/resources/faq")
            response.raise_for_status()
            result = response.json()
            return result.get("content", "")
        except Exception as e:
            # Fallback to direct file reading if MCP server is not available
            print(f"Warning: Could not connect to MCP server ({e}), falling back to local file")
            try:
                # Try to read from local file system
                mcp_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "resources" / "faq.txt"
                if mcp_path.exists():
                    with open(mcp_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    raise Exception(f"Could not find FAQ file at {mcp_path}")
            except Exception as fallback_error:
                raise Exception(f"Could not get FAQ content from MCP server or local file: {e}, {fallback_error}")
    
    async def get_query_prompt(self) -> str:
        """Get query generation prompt from MCP server."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/prompts/query_generate")
            response.raise_for_status()
            result = response.json()
            return result.get("content", "")
        except Exception as e:
            # Fallback to direct file reading
            print(f"Warning: Could not connect to MCP server ({e}), falling back to local file")
            try:
                mcp_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "prompts" / "query_generate.txt"
                if mcp_path.exists():
                    with open(mcp_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    raise Exception(f"Could not find query prompt file at {mcp_path}")
            except Exception as fallback_error:
                raise Exception(f"Could not get query prompt from MCP server or local file: {e}, {fallback_error}")
    
    async def get_answer_prompt(self) -> str:
        """Get answer generation prompt from MCP server."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/prompts/answer_generate")
            response.raise_for_status()
            result = response.json()
            return result.get("content", "")
        except Exception as e:
            # Fallback to direct file reading
            print(f"Warning: Could not connect to MCP server ({e}), falling back to local file")
            try:
                mcp_path = Path(__file__).parent.parent.parent.parent / "mcp_server" / "prompts" / "answer_generate.txt"
                if mcp_path.exists():
                    with open(mcp_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    raise Exception(f"Could not find answer prompt file at {mcp_path}")
            except Exception as fallback_error:
                raise Exception(f"Could not get answer prompt from MCP server or local file: {e}, {fallback_error}")
    
    async def health_check(self) -> bool:
        """Check if MCP server is healthy."""
        try:
            response = await self.client.get(f"{self.mcp_server_url}/health")
            return response.status_code == 200
        except Exception:
            return False
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Global MCP client instance
mcp_client = MCPClient()