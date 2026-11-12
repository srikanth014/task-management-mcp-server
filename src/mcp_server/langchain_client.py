"""LangChain AI Agent with FastMCP integration and Groq LLM.

Connects to the FastMCP Task Server via LangChain's MCPAdapter, loads all tools
dynamically into an agentic loop, and enables natural language task management.
"""

import asyncio
import os
import sys
from uuid import uuid4

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.mcp import MCPAdapter
from langchain.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver

# Load environment variables from .env file
load_dotenv()

MCP_SERVER_URL = "http://127.0.0.1:8000/mcp"


def check_environment() -> tuple[str, str]:
    """Validate required environment variables for the Groq model provider.

    Returns:
        tuple[str, str]: The GROQ_API_KEY and GROQ_MODEL values.

    Raises:
        SystemExit: If GROQ_API_KEY is not configured.
    """
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    if not api_key:
        print("\n[Configuration Error] GROQ_API_KEY is not set.")
        print("Please configure your .env file:")
        print("  1. Copy .env.example to .env:  cp .env.example .env")
        print("  2. Add your Groq API key:      GROQ_API_KEY=gsk_...")
        print("  3. (Optional) Set your model:   GROQ_MODEL=llama-3.3-70b-versatile\n")
        sys.exit(1)

    return api_key, model


async def run_agent() -> None:
    """Initialize and run the interactive LangChain agent session."""
    _, model_name = check_environment()

    print("=" * 60)
    print("Initializing Task Management AI Agent (Groq + FastMCP)")
    print(f"Connecting to MCP server at: {MCP_SERVER_URL}")
    print(f"Using Groq model: {model_name}")
    print("=" * 60)

    adapter = MCPAdapter(MCP_SERVER_URL)

    try:
        async with adapter:
            # Dynamically fetch all tools exposed by the MCP server
            tools = await adapter.list_tools()
            print(f"Loaded {len(tools)} tools from MCP server:")
            for tool in tools:
                print(f" - {getattr(tool, 'name', tool)}")

            # Initialize Groq chat model
            model = init_chat_model(
                model_name,
                model_provider="groq",
            )

            # Create agent with memory checkpointer
            agent = create_agent(
                model=model,
                tools=tools,
                system_prompt=(
                    "You are a helpful, proactive task management assistant. "
                    "You can create tasks, list all tasks, inspect specific tasks, "
                    "update task statuses, and delete tasks using your available tools. "
                    "Always confirm actions clearly to the user."
                ),
                checkpointer=InMemorySaver(),
            )

            # Conversation thread configuration
            thread_id = str(uuid4())
            config = {"configurable": {"thread_id": thread_id}}

            print("\nAgent initialized! Type your task request or 'q' / 'exit' to quit.\n")

            # Initial greeting
            initial_prompt = "Hello! What tasks can you help me manage today?"
            print(f"User: {initial_prompt}\n")
            print("AI thinking...")
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=initial_prompt)]},
                config=config,
            )
            last_message = result["messages"][-1]
            ai_text = getattr(last_message, "content", getattr(last_message, "text", str(last_message)))
            print(f"AI: {ai_text}\n")

            # Interactive chat loop
            while True:
                try:
                    user_input = input("You (q to exit): ").strip()
                except (EOFError, KeyboardInterrupt):
                    print("\nExiting session. Goodbye!")
                    break

                if not user_input:
                    continue

                if user_input.lower() in ("q", "quit", "exit"):
                    print("Goodbye!")
                    break

                print("\nAI thinking...")
                result = await agent.ainvoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config,
                )
                last_message = result["messages"][-1]
                ai_text = getattr(last_message, "content", getattr(last_message, "text", str(last_message)))
                print(f"\nAI: {ai_text}\n")

    except ConnectionRefusedError:
        print(f"\n[Error] Connection refused to MCP server at {MCP_SERVER_URL}.")
        print("Please start the MCP server before running this agent:")
        print("  uv run mcp-server")
        print("  # or: uv run python -m mcp_server.server\n")
    except Exception as exc:
        print(f"\n[Error] An unexpected error occurred: {exc}")
        print("Please check that your MCP server is running and your GROQ_API_KEY is valid.\n")


def main() -> None:
    """Synchronous entry point for the LangChain agent."""
    try:
        asyncio.run(run_agent())
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting.")


if __name__ == "__main__":
    main()
