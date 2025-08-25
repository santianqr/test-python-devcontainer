#!/usr/bin/env python3
"""Alternative agent implementation for gpt-5-nano using direct tool calling."""

import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

from tools import check_property_availability, get_property_details, list_available_properties

load_dotenv()


class GPT5NanoAgent:
    """Custom agent that works with gpt-5-nano using direct tool calling."""

    def __init__(self):
        """Initialize the GPT-5-nano agent with tools and configuration."""
        self.llm = ChatOpenAI(
            model="gpt-5-nano",
            temperature=0.1,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )

        self.tools = [
            check_property_availability,
            get_property_details,
            list_available_properties,
        ]

        self.llm_with_tools = self.llm.bind_tools(self.tools)

        self.system_prompt = (
            "You are a helpful WhatsApp assistant for an Airbnb property management company in Miami.\n\n"
            "You MUST use the provided tools to answer questions about properties:\n"
            "- check_property_availability: Check if a property is available for specific dates\n"
            "- get_property_details: Get detailed information about a property\n"
            "- list_available_properties: List all available properties\n\n"
            "Guidelines:\n"
            "- ALWAYS use tools when users ask about properties, availability, or details\n"
            "- Be friendly and conversational, like a WhatsApp chat\n"
            "- Keep responses concise but informative\n"
            "- Use emojis appropriately for WhatsApp style\n"
            "- Do not make up property information - use the tools"
        )

    def process_message(
        self, message: str, business_context: str = "", conversation_history: str = ""
    ) -> dict[str, Any]:
        """Process a message and return response with tool usage info."""
        full_prompt = f"""{self.system_prompt}

Business Context:
{business_context}

Conversation History:
{conversation_history}

User message: {message}"""

        response = self.llm_with_tools.invoke([HumanMessage(content=full_prompt)])

        tools_used = []
        final_response = response.content

        if hasattr(response, "tool_calls") and response.tool_calls:
            tool_results = []

            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]

                tool_func = None
                for tool in self.tools:
                    if tool.name == tool_name:
                        tool_func = tool
                        break

                if tool_func:
                    try:
                        result = tool_func.invoke(tool_args)
                        tool_results.append(f"Tool {tool_name} result: {result}")
                        tools_used.append(tool_name)
                    except Exception as e:
                        tool_results.append(f"Tool {tool_name} error: {str(e)}")

            if tool_results:
                final_prompt = f"""Based on the following tool results, provide a final helpful response to the user.

Original user message: {message}
Tool results:
{chr(10).join(tool_results)}

Provide a friendly, conversational response in Spanish with appropriate emojis:"""

                final_response_msg = self.llm.invoke([HumanMessage(content=final_prompt)])
                final_response = final_response_msg.content

        return {"response": final_response, "tools_used": tools_used, "success": True}


def test_gpt5_nano_agent():
    """Test the custom gpt-5-nano agent."""
    print("🧪 Testing custom GPT-5-nano agent...")

    agent = GPT5NanoAgent()

    test_messages = [
        "Muéstrame las propiedades disponibles",
        "Verifica disponibilidad de miami_beach_01 del 2024-03-15 al 2024-03-17",
        "Dame detalles de la propiedad brickell_03",
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n=== Test {i}: {message} ===")
        try:
            result = agent.process_message(message)
            print(f"✅ Success: {result['success']}")
            print(f"🔧 Tools used: {result['tools_used']}")
            print(f"📝 Response: {result['response'][:150]}...")
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()


if __name__ == "__main__":
    test_gpt5_nano_agent()
