"""FastAPI application with LangChain and OpenAI integration for WhatsApp message responses."""

import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain.schema import HumanMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

load_dotenv()

app = FastAPI(
    title="WhatsApp AI Assistant",
    description="Simple FastAPI app with LangChain and OpenAI for WhatsApp message responses",
    version="1.0.0",
)


def get_llm():
    """Initialize and return the LangChain OpenAI model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    return ChatOpenAI(openai_api_key=api_key, model=model, temperature=0.7)


class WhatsAppMessage(BaseModel):
    """Model for incoming WhatsApp message."""

    message: str
    sender: str = "user"


class AIResponse(BaseModel):
    """Model for AI response."""

    response: str
    model_used: str
    success: bool


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with basic info."""
    return {
        "message": "WhatsApp AI Assistant API",
        "status": "active",
        "endpoints": "/chat, /health",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    try:
        get_llm()
        return {"status": "healthy", "openai": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.post("/chat", response_model=AIResponse)
async def chat_with_ai(message: WhatsAppMessage) -> AIResponse:
    """Main endpoint to process WhatsApp messages and return AI responses.

    Args:
        message: WhatsAppMessage containing the user's message

    Returns:
        AIResponse with the AI's response
    """
    try:
        llm = get_llm()

        system_context = """You are a friendly and helpful WhatsApp assistant. 
        Respond in a concise and natural way, as if you were a friend replying to a message.
        Keep your responses short and conversational, appropriate for WhatsApp."""

        full_prompt = f"{system_context}\n\nUser: {message.message}"
        human_message = HumanMessage(content=full_prompt)
        response = llm.invoke([human_message])

        return AIResponse(
            response=response.content, model_used=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"), success=True
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}") from e


@app.get("/test")
async def test_endpoint() -> dict[str, Any]:
    """Simple test endpoint to verify the API is working."""
    return {
        "message": "API is working!",
        "test_chat_endpoint": "/chat",
        "sample_request": {"message": "Hello, how are you?", "sender": "user"},
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
