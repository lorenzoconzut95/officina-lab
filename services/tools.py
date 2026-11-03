import json

from repositories.tasks import list_tasks
from repositories.memories import list_memories
from services.approvals import create_approval
from services.tool_calls import log_tool_call


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
