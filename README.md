# FastMCP Task Server & AI Agent

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![MCP](https://img.shields.io/badge/protocol-MCP-orange.svg)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/framework-FastMCP-green.svg)](https://github.com/jlowin/fastmcp)
[![LangChain](https://img.shields.io/badge/agent-LangChain-purple.svg)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/LLM-Groq-red.svg)](https://groq.com/)

A production-ready [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server providing task management capabilities with SQLite persistence. It includes:
1. **FastMCP Server**: Exposes standard MCP tools over HTTP/SSE.
2. **FastMCP Client**: Demonstrates direct asynchronous MCP tool execution.
3. **LangChain AI Agent**: An interactive conversational agent using Groq and LangChain's `MCPAdapter` to automatically invoke task tools based on natural language requests.
4. **MCP Host Integration**: Out-of-the-box support for MCP clients like Claude Desktop, Cursor, and Antigravity.

---

## Architecture Overview

```
                          ┌─────────────────────────────────────┐
                          │         MCP Host / Consumer         │
                          │ (Claude Desktop / Cursor / Antigravity)
                          └──────────────────┬──────────────────┘
                                             │ HTTP/SSE
                                             ▼
┌─────────────────────────┐       ┌─────────────────────────────────────┐
│  LangChain AI Agent     │       │       FastMCP Server                │
│  (Groq LLM + MCPAdapter)├──────►│   (http://127.0.0.1:8000/mcp)       │
└─────────────────────────┘       └──────────────────┬──────────────────┘
                                                     │
┌─────────────────────────┐                          │ CRUD Operations
│  FastMCP Python Client  ├──────────────────────────┤
│  (Async Tool Calls)     │                          ▼
└─────────────────────────┘       ┌─────────────────────────────────────┐
                                  │       SQLite Database               │
                                  │       (data/tasks.db)               │
                                  └─────────────────────────────────────┘
```

---

## Project Structure

```
.
├── .env.example              # Template for environment variables (Groq API keys)
├── .gitignore                # Comprehensive Git ignore rules (DBs, venvs, caches)
├── .mcp.json                 # MCP server client configuration for MCP hosts
├── .python-version           # Target Python version (3.13)
├── README.md                 # Project documentation and guide
├── data/
│   └── .gitkeep              # Ensures data directory exists in Git checkouts
│   └── tasks.db              # Local SQLite database (git-ignored, created on run)
├── pyproject.toml            # Project metadata, dependencies, and CLI entry points
├── src/
│   └── mcp_server/
│       ├── __init__.py       # Package definition & CLI exports
│       ├── database.py       # SQLite layer with schema init & CRUD operations
│       ├── server.py         # FastMCP server exposing task tools over HTTP
│       ├── client.py         # Asynchronous FastMCP client and demo suite
│       └── langchain_client.py # Interactive LangChain AI Agent powered by Groq
└── uv.lock                   # Deterministic lockfile for uv package manager
```

---

## Prerequisites

- **Python**: `>= 3.13`
- **Package Manager**: [uv](https://docs.astral.sh/uv/) (recommended) or standard `pip` / `venv`
- **Groq API Key**: (Optional, only needed for the LangChain AI agent) [Get a free Groq API key](https://console.groq.com/keys)

---

## Getting Started

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd mcp_server
```

### 2. Install Dependencies

Using `uv` (recommended):
```bash
uv sync
```

Or using standard `pip`:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Open `.env` and set your Groq API credentials (required for running `langchain_client.py`):
```ini
GROQ_API_KEY=gsk_your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile
```

---

## How to Run

### Step 1: Start the MCP Server

Start the FastMCP HTTP server on `http://127.0.0.1:8000/mcp`:

```bash
uv run mcp-server
# Or:
uv run python -m mcp_server.server
```

The server will automatically create `data/tasks.db` and initialize the schema if it does not exist.

### Step 2: Run the Direct FastMCP Client

In a new terminal window (while the server is running), execute the client demonstration:

```bash
uv run mcp-client
# Or:
uv run python -m mcp_server.client
```

This script performs an automated end-to-end demonstration:
- Lists all available tools from the MCP server
- Creates a new demo task
- Fetches and displays all tasks
- Updates the status of the demo task to `done`
- Cleans up the demo task

### Step 3: Run the Conversational AI Agent

To interact with your tasks using natural language via Groq LLM:

```bash
uv run mcp-agent
# Or:
uv run python -m mcp_server.langchain_client
```

Example session:
```text
============================================================
Initializing Task Management AI Agent (Groq + FastMCP)
Connecting to MCP server at: http://127.0.0.1:8000/mcp
Using Groq model: llama-3.3-70b-versatile
============================================================
Loaded 6 tools from MCP server:
 - create_task
 - get_all_tasks
 - get_task
 - update_task_status
 - delete_task
 - save_task

User: Hello! What tasks can you help me manage today?
AI: Hello! I can help you create, view, update, and delete tasks in your task manager.

You (q to exit): Create a high priority task to prepare the release notes
AI thinking...
AI: I've created the task:
- Title: Prepare the release notes
- Priority: High
- Status: todo
- Task ID: 5f98a21e-7b3b-472e-8302-39c878939b56

You (q to exit): List all my tasks
AI thinking...
AI: Here are your current tasks:
1. Prepare the release notes (Priority: High, Status: todo)
...
```

---

## MCP Tools Reference

The server exposes the following MCP tools:

| Tool Name | Parameters | Description | Returns |
| :--- | :--- | :--- | :--- |
| `create_task` | `title: str`<br>`priority: "low" \| "medium" \| "high"`<br>`description: str` | Creates a new task and persists it to SQLite with status `todo` and a generated UUID. | Created task dictionary |
| `get_all_tasks` | *None* | Retrieves all tasks stored in the database. | List of task dictionaries |
| `get_task` | `task_id: str` | Fetches a single task by its unique ID. | Task dictionary or error object |
| `update_task_status` | `task_id: str`<br>`status: "todo" \| "in_progress" \| "done"` | Updates the progress status of an existing task. | Updated task dictionary or error object |
| `delete_task` | `task_id: str` | Deletes a task permanently by its ID. | Success confirmation or error object |
| `save_task` | `task: dict` | Direct task dictionary insertion / update. | Saved task dictionary |

---

## Connecting to MCP Hosts

You can connect this server to external MCP clients like Claude Desktop, Cursor, and Antigravity.

### Antigravity / Cursor (`.mcp.json`)

The project includes `.mcp.json` at the root directory:
```json
{
  "mcpServers": {
    "mcp_server_acl": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

### Claude Desktop (`claude_desktop_config.json`)

Add the server to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "task-manager": {
      "type": "http",
      "url": "http://127.0.0.1:8000/mcp"
    }
  }
}
```

---

## Database Schema

Tasks are stored in `data/tasks.db` using the following schema:

```sql
CREATE TABLE IF NOT EXISTS tasks (
    task_id     TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    priority    TEXT NOT NULL DEFAULT 'medium',
    status      TEXT NOT NULL DEFAULT 'todo'
);
```

---

## Contributing & Git Workflow

- **Branching**: Create feature branches from `master` or `main`.
- **Environment variables**: Never commit `.env` or files containing secret API keys.
- **Databases**: SQLite databases (`*.db`, `*.sqlite`) are ignored via `.gitignore`.
- **Formatting**: Adhere to PEP 8 standards with type hints and docstrings on all functions.
