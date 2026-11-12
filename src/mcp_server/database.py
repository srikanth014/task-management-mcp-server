"""Database access module for task persistence using SQLite.

Manages task records in a local SQLite database (data/tasks.db).
Automatically initializes the database and table schema if they do not exist.
"""

from pathlib import Path
import sqlite3
from typing import Any

# Compute the project root directory and database storage path
project_root = Path(__file__).resolve().parents[2]
data_dir = project_root / "data"
db_path = data_dir / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite database connection with row factory configured.

    Ensures that the parent directory exists before establishing the connection.

    Returns:
        sqlite3.Connection: Connection object with sqlite3.Row row_factory.
    """
    data_dir.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Initialize the SQLite database schema.

    Creates the `tasks` table if it does not already exist.
    Columns:
        - task_id (TEXT, PRIMARY KEY): Unique identifier (UUID).
        - title (TEXT, NOT NULL): Short summary or title of the task.
        - description (TEXT, NOT NULL): Detailed task description.
        - priority (TEXT, NOT NULL): Priority level (e.g. low, medium, high).
        - status (TEXT, NOT NULL): Current progress (e.g. todo, in_progress, done).
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                priority TEXT NOT NULL DEFAULT 'medium',
                status TEXT NOT NULL DEFAULT 'todo'
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def save_task(task: dict[str, Any]) -> dict[str, Any]:
    """Insert or replace a task record in the database.

    Args:
        task (dict[str, Any]): Dictionary containing task fields:
            - task_id (str): Unique task identifier.
            - title (str): Title of the task.
            - description (str, optional): Description of the task.
            - priority (str, optional): Priority level ('low', 'medium', 'high').
            - status (str, optional): Task status ('todo', 'in_progress', 'done').

    Returns:
        dict[str, Any]: The saved task dictionary.
    """
    conn = get_connection()
    normalized_task = {
        "task_id": str(task["task_id"]),
        "title": str(task["title"]),
        "description": str(task.get("description", "")),
        "priority": str(task.get("priority", "medium")),
        "status": str(task.get("status", "todo")),
    }
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO tasks (
                task_id, title, description, priority, status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                normalized_task["task_id"],
                normalized_task["title"],
                normalized_task["description"],
                normalized_task["priority"],
                normalized_task["status"],
            ),
        )
        conn.commit()
    finally:
        conn.close()

    return normalized_task


def get_task_by_id(task_id: str) -> dict[str, Any] | None:
    """Retrieve a single task by its unique identifier.

    Args:
        task_id (str): The ID of the task to retrieve.

    Returns:
        dict[str, Any] | None: The task record as a dict, or None if not found.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def update_task_status_in_db(task_id: str, status: str) -> dict[str, Any]:
    """Update the status of an existing task in the database.

    Args:
        task_id (str): The unique ID of the task to update.
        status (str): The new status (e.g. 'todo', 'in_progress', 'done').

    Returns:
        dict[str, Any]: The updated task record or an error dictionary if not found.
    """
    conn = get_connection()
    try:
        conn.execute(
            """
            UPDATE tasks
            SET status = ?
            WHERE task_id = ?
            """,
            (status, task_id),
        )
        conn.commit()

        row = conn.execute(
            "SELECT * FROM tasks WHERE task_id = ?",
            (task_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        return {"error": f"The task_id '{task_id}' does not exist"}
    return dict(row)


def delete_task_in_db(task_id: str) -> dict[str, Any]:
    """Delete a task record from the database by its ID.

    Args:
        task_id (str): Unique task identifier to delete.

    Returns:
        dict[str, Any]: Status dictionary indicating success or failure.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE task_id = ?",
            (task_id,),
        )
        conn.commit()
        if cursor.rowcount == 0:
            return {"error": f"The task_id '{task_id}' does not exist"}
        return {"success": True, "message": f"Task '{task_id}' deleted successfully"}
    finally:
        conn.close()


def get_all_tasks() -> list[dict[str, Any]]:
    """Retrieve all task records from the database.

    Returns:
        list[dict[str, Any]]: A list of dictionaries representing all stored tasks.
    """
    conn = get_connection()
    try:
        rows = conn.execute("SELECT * FROM tasks ORDER BY task_id ASC").fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


# Ensure the table is created automatically when the module is loaded
init_db()


if __name__ == "__main__":
    print("Database path:", db_path)
    print("Current tasks:", get_all_tasks())
