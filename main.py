"""FastAPI application with LangChain AI Agent for WhatsApp message responses."""

import os
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from database import init_database, test_connection
from gpt5_nano_agent import GPT5NanoAgent
from memory import ConversationMemory
from tools import check_property_availability, get_property_details, list_available_properties
from vector_store import BusinessKnowledgeStore

load_dotenv()

app = FastAPI(
    title="WhatsApp AI Agent",
    description="AI Agent with memory, vector store, and tools for Airbnb property management",
    version="2.0.0",
)


class ChatMessage(BaseModel):
    """Model for incoming chat message."""

    message: str
    chat_id: str = "default_chat"
    sender: str = "user"


class AgentResponse(BaseModel):
    """Model for agent response."""

    response: str
    chat_id: str
    model_used: str
    tools_used: list[str]
    success: bool


def get_llm():
    """Initialize and return the LangChain OpenAI model."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    model = os.getenv("OPENAI_MODEL", "gpt-4o")
    return ChatOpenAI(openai_api_key=api_key, model=model, temperature=0.1)


def create_agent() -> AgentExecutor:
    """Create the AI agent with tools and memory."""
    llm = get_llm()

    tools = [
        check_property_availability,
        get_property_details,
        list_available_properties,
    ]

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """You are a helpful WhatsApp assistant for an Airbnb property management company in Miami.

You MUST use the provided tools to answer questions about properties:
- check_property_availability: Check if a property is available for specific dates
- get_property_details: Get detailed information about a property  
- list_available_properties: List all available properties

Guidelines:
- ALWAYS use tools when users ask about properties, availability, or details
- Be friendly and conversational, like a WhatsApp chat
- Keep responses concise but informative
- Use emojis appropriately for WhatsApp style
- Do not make up property information - use the tools

Business Context:
{business_context}

Conversation History:
{conversation_history}""",
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    )

    agent = create_openai_functions_agent(llm, tools, prompt)
    return AgentExecutor(agent=agent, tools=tools, verbose=True, return_intermediate_steps=True)


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint with basic info."""
    return {
        "message": "WhatsApp AI Agent API",
        "status": "active",
        "version": "2.0.0",
        "features": "memory, vector_store, tools",
        "endpoints": "/chat, /health, /db-status",
    }


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    try:
        get_llm()
        return {"status": "healthy", "openai": "connected", "agent": "ready"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


@app.get("/db-status")
async def database_status() -> dict[str, Any]:
    """Check database connection status."""
    return test_connection()


@app.post("/chat", response_model=AgentResponse)
async def chat_with_agent(message: ChatMessage) -> AgentResponse:
    """Main endpoint to process messages with the AI agent.

    Args:
        message: ChatMessage containing the user's message and chat_id

    Returns:
        AgentResponse with the agent's response and metadata
    """
    try:
        memory = ConversationMemory(message.chat_id)
        knowledge_store = BusinessKnowledgeStore()

        conversation_history = memory.build_conversation_context(limit=5)
        relevant_knowledge = knowledge_store.search_knowledge(message.message, limit=3)
        business_context = "\n".join([item["content"] for item in relevant_knowledge])

        model_name = os.getenv("OPENAI_MODEL", "gpt-4o")

        if model_name == "gpt-5-nano":
            gpt5_agent = GPT5NanoAgent()
            result = gpt5_agent.process_message(
                message.message, business_context=business_context, conversation_history=conversation_history
            )
            response_text = result["response"]
            tools_used = result["tools_used"]
        else:
            agent_executor = create_agent()

            agent_input = {
                "input": message.message,
                "business_context": business_context,
                "conversation_history": conversation_history,
                "chat_history": [],
            }

            result = agent_executor.invoke(agent_input)
            response_text = result["output"]
            intermediate_steps = result.get("intermediate_steps", [])
            tools_used = []
            for step in intermediate_steps:
                if len(step) >= 1 and hasattr(step[0], "tool"):
                    tools_used.append(step[0].tool)
                elif len(step) >= 1 and hasattr(step[0], "name"):
                    tools_used.append(step[0].name)

        memory.add_message(message.message, response_text)

        return AgentResponse(
            response=response_text,
            chat_id=message.chat_id,
            model_used=model_name,
            tools_used=tools_used,
            success=True,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}") from e


@app.get("/chat/{chat_id}/history")
async def get_chat_history(chat_id: str, limit: int = 10) -> dict[str, Any]:
    """Get conversation history for a specific chat."""
    try:
        memory = ConversationMemory(chat_id)
        history = memory.get_recent_messages(limit)
        summary = memory.get_conversation_summary()

        return {
            "chat_id": chat_id,
            "history": history,
            "summary": summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving history: {str(e)}") from e


@app.delete("/chat/{chat_id}/history")
async def clear_chat_history(chat_id: str) -> dict[str, Any]:
    """Clear conversation history for a specific chat."""
    try:
        memory = ConversationMemory(chat_id)
        deleted_count = memory.clear_history()

        return {
            "chat_id": chat_id,
            "deleted_messages": deleted_count,
            "status": "cleared",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing history: {str(e)}") from e


@app.get("/test")
async def test_endpoint() -> dict[str, Any]:
    """Simple test endpoint to verify the API is working."""
    return {
        "message": "AI Agent API is working!",
        "chat_endpoint": "/chat",
        "sample_request": {
            "message": "Hello, show me available properties",
            "chat_id": "test_chat_123",
            "sender": "user",
        },
        "features": (
            "memory: ✅ Conversation history, vector_store: ✅ Business knowledge search, "
            "tools: ✅ Property availability checking"
        ),
    }


if __name__ == "__main__":
    import uvicorn

    print("🚀 Initializing database...")
    init_database()
    print("✅ Database ready!")

    uvicorn.run(app, host="0.0.0.0", port=8000)
