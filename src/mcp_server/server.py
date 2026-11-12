"""FastMCP Server providing task management tools over HTTP/SSE.

Exposes CRUD operations for task tracking to MCP-compatible clients
(such as LangChain, Claude Desktop, Cursor, and Antigravity).
"""

from typing import Any, Literal
from uuid import uuid4

from fastmcp import FastMCP
from mcp_server.database import (
    delete_task_in_db,
    get_all_tasks,
    get_task_by_id,
    save_task,
    update_task_status_in_db,
)

# Initialize the FastMCP server instance
mcp = FastMCP("Task Management MCP Server")


@mcp.tool(name="create_task", description="Create a new task with a title, priority, and optional description.")
def create_task(
    title: str,
    priority: Literal["low", "medium", "high"] = "medium",
    description: str = "",
) -> dict[str, Any]:
    """Create a new task and persist it to the SQLite database.

    Args:
        title (str): Concise title or summary of the task.
        priority (Literal["low", "medium", "high"]): Task priority level. Defaults to 'medium'.
        description (str, optional): Detailed explanation of the task. Defaults to ''.

    Returns:
        dict[str, Any]: The newly created task object including its generated UUID and 'todo' status.
    """
    task_id = str(uuid4())
    task = {
        "task_id": task_id,
        "title": title,
        "priority": priority,
        "description": description,
        "status": "todo",
    }
    return save_task(task)


@mcp.tool(name="get_all_tasks", description="Retrieve all tasks currently stored in the database.")
def get_all_tasks_tool() -> list[dict[str, Any]]:
    """Retrieve all tasks from the database.

    Returns:
        list[dict[str, Any]]: A list of all tasks with their IDs, titles, descriptions, priorities, and statuses.
    """
    return get_all_tasks()


@mcp.tool(name="get_task", description="Retrieve details of a single task by its task_id.")
def get_task_tool(task_id: str) -> dict[str, Any]:
    """Fetch a specific task by its unique ID.

    Args:
        task_id (str): The unique identifier of the task.

    Returns:
        dict[str, Any]: The task dictionary, or an error message if not found.
    """
    task = get_task_by_id(task_id)
    if task is None:
        return {"error": f"The task_id '{task_id}' does not exist"}
    return task


@mcp.tool(name="update_task_status", description="Update the status of an existing task (e.g. todo, in_progress, done).")
def update_task_status_tool(
    task_id: str,
    status: Literal["todo", "in_progress", "done"],
) -> dict[str, Any]:
    """Update an existing task's status in the database.

    Args:
        task_id (str): The unique ID of the task to update.
        status (Literal["todo", "in_progress", "done"]): The updated status value.

    Returns:
        dict[str, Any]: The updated task object or an error message if not found.
    """
    return update_task_status_in_db(task_id, status)


@mcp.tool(name="update_task_status_in_db", description="Alias for update_task_status for backwards compatibility.")
def update_task_status_in_db_tool(
    task_id: str,
    status: Literal["todo", "in_progress", "done"],
) -> dict[str, Any]:
    """Alias for update_task_status to maintain backward compatibility."""
    return update_task_status_in_db(task_id, status)


@mcp.tool(name="delete_task", description="Delete a task permanently from the database by its task_id.")
def delete_task_tool(task_id: str) -> dict[str, Any]:
    """Delete a task by its unique ID.

    Args:
        task_id (str): The unique ID of the task to delete.

    Returns:
        dict[str, Any]: Result indicating success or error if not found.
    """
    return delete_task_in_db(task_id)


@mcp.tool(name="save_task", description="Save or overwrite a task dictionary directly in the database.")
def save_task_tool(task: dict[str, Any]) -> dict[str, Any]:
    """Save a raw task dictionary to the database. Generates a task_id if one is not provided.

    Args:
        task (dict[str, Any]): Dictionary containing at minimum a 'title'.

    Returns:
        dict[str, Any]: The saved task record.
    """
    if "task_id" not in task:
        task["task_id"] = str(uuid4())
    return save_task(task)


def main() -> None:
    """Entry point to run the MCP server over HTTP transport on port 8000."""
    print("Starting Task Management MCP Server on http://127.0.0.1:8000/mcp ...")
    mcp.run(transport="http", port=8000)


if __name__ == "__main__":
    main()
