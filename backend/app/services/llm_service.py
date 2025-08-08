import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from ..schemas import ConversationMessage


class LLMService:
    """Service for interacting with LLM using LangChain."""
    
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            openai_api_key=api_key
        )
    
    def _format_conversation_history(self, history: List[ConversationMessage]) -> str:
        """Format conversation history for prompt."""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history:
            role = "User" if msg.role == "user" else "Assistant"
            formatted.append(f"{role}: {msg.content}")
        
        return "\n".join(formatted)
    
    async def generate_query(self, user_query: str, conversation_history: List[ConversationMessage], prompt_template: str) -> str:
        """Generate refined query using LLM."""
        
        # Format conversation history
        history_text = self._format_conversation_history(conversation_history)
        
        # Fill in the prompt template
        prompt = prompt_template.format(
            conversation_history=history_text,
            user_query=user_query
        )
        
        # Create messages
        messages = [
            SystemMessage(content="You are a helpful assistant that refines user queries."),
            HumanMessage(content=prompt)
        ]
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        return response.content.strip()
    
    async def generate_answer(self, refined_query: str, faq_content: str, prompt_template: str) -> str:
        """Generate answer using LLM."""
        
        # Fill in the prompt template
        prompt = prompt_template.format(
            faq_content=faq_content,
            refined_query=refined_query
        )
        
        # Create messages
        messages = [
            SystemMessage(content="You are a helpful customer support assistant."),
            HumanMessage(content=prompt)
        ]
        
        # Get response from LLM
        response = await self.llm.ainvoke(messages)
        return response.content.strip()


# Global LLM service instance
llm_service = LLMService()