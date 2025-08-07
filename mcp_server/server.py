#!/usr/bin/env python3
import asyncio
import os
from pathlib import Path
from typing import Any, Sequence

import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio


class RAGMCPServer:
    """MCP server for RAG chatbot providing FAQ resources and prompts."""
    
    def __init__(self):
        self.server = Server("rag-chatbot-mcp")
        self.base_path = Path(__file__).parent
        self.setup_handlers()
    
    def setup_handlers(self):
        """Set up MCP server handlers."""
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[types.Resource]:
            """List available resources."""
            return [
                types.Resource(
                    uri="file://faq",
                    name="FAQ Content",
                    description="Frequently Asked Questions content for the chatbot",
                    mimeType="text/plain"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: str) -> str:
            """Read resource content."""
            if uri == "file://faq":
                faq_path = self.base_path / "resources" / "faq.txt"
                try:
                    with open(faq_path, 'r', encoding='utf-8') as f:
                        return f.read()
                except FileNotFoundError:
                    raise ValueError(f"FAQ file not found at {faq_path}")
            else:
                raise ValueError(f"Unknown resource: {uri}")
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools."""
            return [
                types.Tool(
                    name="get_query_prompt",
                    description="Get the prompt template for query generation",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                types.Tool(
                    name="get_answer_prompt",
                    description="Get the prompt template for answer generation",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
            """Handle tool calls."""
            if name == "get_query_prompt":
                prompt_path = self.base_path / "prompts" / "query_generate.txt"
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return [types.TextContent(type="text", text=content)]
                except FileNotFoundError:
                    raise ValueError(f"Query prompt file not found at {prompt_path}")
            
            elif name == "get_answer_prompt":
                prompt_path = self.base_path / "prompts" / "answer_generate.txt"
                try:
                    with open(prompt_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    return [types.TextContent(type="text", text=content)]
                except FileNotFoundError:
                    raise ValueError(f"Answer prompt file not found at {prompt_path}")
            
            else:
                raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server."""
    server_instance = RAGMCPServer()
    
    # Initialize options
    options = InitializationOptions(
        server_name="rag-chatbot-mcp",
        server_version="1.0.0",
        capabilities=server_instance.server.get_capabilities()
    )
    
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server_instance.server.run(
            read_stream,
            write_stream,
            options
        )


if __name__ == "__main__":
    asyncio.run(main())