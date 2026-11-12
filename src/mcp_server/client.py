"""FastMCP client demonstration for interacting with the MCP Task Server.

Provides asynchronous functions to connect to the running MCP server over HTTP,
discover available tools, and execute task management operations (create, list,
update, delete).
"""

import asyncio
from typing import Any
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8000/mcp"
client = Client(SERVER_URL)


async def get_tools_from_server() -> list[Any]:
    """Retrieve and display the list of all tools exposed by the MCP server.

    Returns:
        list[Any]: List of tool definitions provided by the MCP server.
    """
    async with client:
        tools = await client.list_tools()
        print(f"Discovered {len(tools)} tools on the server:")
        for tool in tools:
            print(f" - {tool.name}: {tool.description}")
        return tools


async def create_task_using_mcp(
    title: str = "Learn Fast MCP",
    priority: str = "high",
    description: str = "Complete the Fast MCP tutorial to understand how MCP works.",
) -> Any:
    """Invoke the 'create_task' MCP tool to create and persist a new task.

    Args:
        title (str): Title of the task.
        priority (str): Priority level ('low', 'medium', 'high').
        description (str): Detailed description of the task.

    Returns:
        Any: Tool call result containing the created task record.
    """
    async with client:
        result = await client.call_tool(
            "create_task",
            {
                "title": title,
                "priority": priority,
                "description": description,
            },
        )
        print("Created task:", result.data)
        return result


async def get_all_tasks_from_server() -> Any:
    """Invoke the 'get_all_tasks' MCP tool to retrieve all tasks.

    Returns:
        Any: Tool call result containing the list of all stored tasks.
    """
    async with client:
        result = await client.call_tool("get_all_tasks", {})
        print("All tasks:", result.data)
        return result


async def get_task_from_server(task_id: str) -> Any:
    """Invoke the 'get_task' MCP tool to fetch a single task by ID.

    Args:
        task_id (str): The ID of the task to retrieve.

    Returns:
        Any: Tool call result containing the retrieved task.
    """
    async with client:
        result = await client.call_tool("get_task", {"task_id": task_id})
        print(f"Task '{task_id}':", result.data)
        return result


async def update_task_status_using_mcp(task_id: str, status: str = "done") -> Any:
    """Invoke the 'update_task_status' MCP tool to update an existing task.

    Args:
        task_id (str): The ID of the task to update.
        status (str): The new status ('todo', 'in_progress', 'done').

    Returns:
        Any: Tool call result containing the updated task record.
    """
    async with client:
        result = await client.call_tool(
            "update_task_status",
            {
                "task_id": task_id,
                "status": status,
            },
        )
        print(f"Updated task '{task_id}' status to '{status}':", result.data)
        return result


async def delete_task_using_mcp(task_id: str) -> Any:
    """Invoke the 'delete_task' MCP tool to delete a task by ID.

    Args:
        task_id (str): The ID of the task to delete.

    Returns:
        Any: Tool call result containing the deletion response.
    """
    async with client:
        result = await client.call_tool("delete_task", {"task_id": task_id})
        print(f"Deleted task '{task_id}':", result.data)
        return result


async def run_demo() -> None:
    """Run an end-to-end demonstration of the MCP client workflow.

    Demonstrates:
    1. Listing available server tools.
    2. Creating a new task.
    3. Listing all tasks.
    4. Updating the task status.
    5. Fetching the updated task.
    6. Cleaning up by deleting the demo task.
    """
    print("=" * 60)
    print("Starting FastMCP Client Demo")
    print(f"Target Server: {SERVER_URL}")
    print("=" * 60)

    try:
        # 1. Discover tools
        print("\n[Step 1] Listing tools from MCP server...")
        await get_tools_from_server()

        # 2. Create a new task
        print("\n[Step 2] Creating a demo task...")
        create_res = await create_task_using_mcp(
            title="FastMCP Demo Task",
            priority="high",
            description="Demonstration task created by mcp_server/client.py",
        )
        task_id = create_res.data.get("task_id") if isinstance(create_res.data, dict) else None

        # 3. Retrieve all tasks
        print("\n[Step 3] Fetching all tasks...")
        await get_all_tasks_from_server()

        if task_id:
            # 4. Update the created task
            print(f"\n[Step 4] Updating task '{task_id}' status to 'done'...")
            await update_task_status_using_mcp(task_id, status="done")

            # 5. Fetch the task by ID
            print(f"\n[Step 5] Fetching single task '{task_id}'...")
            await get_task_from_server(task_id)

            # 6. Delete the task
            print(f"\n[Step 6] Cleaning up demo task '{task_id}'...")
            await delete_task_using_mcp(task_id)

        print("\n" + "=" * 60)
        print("FastMCP Client Demo completed successfully!")
        print("=" * 60)

    except Exception as exc:
        print(f"\n[Error] Unable to communicate with MCP server: {exc}")
        print("\nPlease make sure the server is running first:")
        print("  uv run mcp-server")
        print("  # or: uv run python -m mcp_server.server\n")


def main() -> None:
    """Synchronous entry point for the MCP client."""
    asyncio.run(run_demo())


if __name__ == "__main__":
    main()
