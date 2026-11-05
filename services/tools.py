import json

from repositories.tasks import list_tasks
from repositories.memories import list_memories
from repositories.runs import list_runs
from repositories.tool_calls import list_tool_calls
from repositories.errors import list_errors
from services.approvals import create_approval
from services.tool_calls import log_tool_call
from services.project_state import build_project_state
from services.project_files import (
    list_project_files,
    read_project_file
)


TOOL_DEFINITIONS = [
    {
        "type": "function",
        "name": "list_tasks",
        "description": (
            "Read tasks stored in Officina Lab. "
            "Use this when the user asks about current work, priorities, "
            "todo items, completed work, or project status."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Optional project name."
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "todo", "done"],
                    "description": "Optional task status filter."
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "list_memories",
        "description": (
            "Read saved Officina project memories, decisions, facts, and notes."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Optional project name."
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "list_recent_runs",
        "description": (
            "Read recent Officina agent runs. "
            "Use this to verify what has actually been executed, "
            "which context sources were used, and whether recent work "
            "provides evidence that a task may already be complete."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20
                },
                "status": {
                    "type": "string",
                    "enum": ["all", "running", "completed", "failed"]
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "list_recent_errors",
        "description": (
            "Read recent Officina run errors from the separate Error Log. "
            "Use this when diagnosing failures, identifying recurring error "
            "patterns, or proposing a minimal regression test."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "inspect_project_state",
        "description": (
            "Build a read-only evidence snapshot for a project by combining "
            "its tasks, saved memories, recent agent runs, and recent tool calls. "
            "Use this before deciding whether work is already implemented, "
            "what changed recently, or what action should come next."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": "Project name to inspect."
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 8,
                    "description": "Maximum recent runs/tool calls to include. Prefer 4-6."
                }
            },
            "required": ["project"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "list_project_files",
        "description": (
            "List readable source, test, documentation, and frontend files "
            "inside the Officina Lab project. This is read-only and excludes "
            "secrets, databases, virtual environments, and .git."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 200
                }
            },
            "required": [],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "read_project_file",
        "description": (
            "Read one allowed text source/test/documentation file from "
            "Officina Lab. Use this to verify whether a fix or regression "
            "test is actually implemented. This is read-only and cannot "
            "read secrets, databases, or files outside the project."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": (
                        "Project-relative path, for example "
                        "services/executor.py or tests/test_api_key_config.py."
                    )
                },
                "max_chars": {
                    "type": "integer",
                    "minimum": 1000,
                    "maximum": 20000
                }
            },
            "required": ["path"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "create_task",
        "description": (
            "Propose creating a new Officina task. "
            "This write action requires human approval before execution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"]
                },
                "project": {"type": "string"}
            },
            "required": ["title", "priority", "project"],
            "additionalProperties": False
        }
    },
    {
        "type": "function",
        "name": "update_task_status",
        "description": (
            "Propose changing an existing task status. "
            "This write action requires human approval before execution."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer"},
                "status": {
                    "type": "string",
                    "enum": ["todo", "done"]
                }
            },
            "required": ["task_id", "status"],
            "additionalProperties": False
        }
    }
]


def execute_tool(
    name,
    arguments,
    agent_name=None,
    run_id=None
):
    if name == "list_tasks":
        project = arguments.get("project")
        status = arguments.get("status", "all")

        tasks = list_tasks()

        if project:
            tasks = [
                task for task in tasks
                if task["project"].lower() == project.lower()
            ]

        if status != "all":
            tasks = [
                task for task in tasks
                if task["status"] == status
            ]

        result = {
            "tool": "list_tasks",
            "count": len(tasks),
            "items": tasks[:30]
        }

    elif name == "list_memories":
        project = arguments.get("project")
        limit = arguments.get("limit", 8)

        memories = list_memories(
            project=project,
            limit=limit
        )

        result = {
            "tool": "list_memories",
            "count": len(memories),
            "items": memories
        }

    elif name == "list_recent_runs":
        limit = arguments.get("limit", 8)
        status = arguments.get("status", "all")

        runs = list_runs()

        if status != "all":
            runs = [
                run for run in runs
                if run["status"] == status
            ]

        items = []

        for run in runs[:limit]:
            items.append({
                "id": run["id"],
                "agent_name": run["agent_name"],
                "task": run["task"],
                "status": run["status"],
                "output": run["output"],
                "started_at": run["started_at"],
                "ended_at": run["ended_at"],
                "model": run["model"],
                "context_sources": run["context_sources"]
            })

        result = {
            "tool": "list_recent_runs",
            "count": len(items),
            "items": items
        }

    elif name == "list_recent_errors":
        limit = min(
            arguments.get("limit", 8),
            20
        )

        errors = list_errors(
            limit=limit
        )

        result = {
            "tool": "list_recent_errors",
            "count": len(errors),
            "items": [
                {
                    "id": item["id"],
                    "run_id": item["run_id"],
                    "agent_name": item["agent_name"],
                    "task": (item["task"] or "")[:4000],
                    "error_message": (item["error_message"] or "")[:4000],
                    "created_at": item["created_at"]
                }
                for item in errors
            ]
        }

    elif name == "inspect_project_state":
        project = arguments["project"]
        limit = arguments.get("limit", 5)

        result = {
            "tool": "inspect_project_state",
            **build_project_state(
                project=project,
                limit=limit
            )
        }

    elif name == "list_project_files":
        limit = min(
            arguments.get("limit", 100),
            200
        )

        files = list_project_files(
            limit=limit
        )

        result = {
            "tool": "list_project_files",
            "count": len(files),
            "items": files
        }

    elif name == "read_project_file":
        path = arguments["path"]
        max_chars = min(
            arguments.get("max_chars", 12000),
            20000
        )

        file_result = read_project_file(
            path=path,
            max_chars=max_chars
        )

        result = {
            "tool": "read_project_file",
            **file_result
        }

    elif name == "create_task":
        approval = create_approval(
            "create_task",
            arguments,
            agent_name or "unknown-agent",
            run_id
        )

        result = {
            "tool": "create_task",
            "status": "approval_required",
            "approval_id": approval["id"],
            "message": (
                "Task creation has NOT been executed. "
                "Human approval is required."
            ),
            "proposed_action": arguments
        }

    elif name == "update_task_status":
        approval = create_approval(
            "update_task_status",
            arguments,
            agent_name or "unknown-agent",
            run_id
        )

        result = {
            "tool": "update_task_status",
            "status": "approval_required",
            "approval_id": approval["id"],
            "message": (
                "Task status has NOT been changed. "
                "Human approval is required."
            ),
            "proposed_action": arguments
        }

    else:
        result = {
            "error": "Unknown tool: " + name
        }

    log_tool_call(
        run_id,
        agent_name or "unknown-agent",
        name,
        arguments,
        result
    )

    return result


def execute_tool_json(
    name,
    arguments_json,
    agent_name=None,
    run_id=None
):
    try:
        arguments = json.loads(
            arguments_json or "{}"
        )
    except json.JSONDecodeError:
        arguments = {}

    return execute_tool(
        name,
        arguments,
        agent_name=agent_name,
        run_id=run_id
    )
