import json

from repositories.tasks import list_tasks
from repositories.memories import list_memories
from services.approvals import create_approval


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
                    "description": (
                        "Optional project name. "
                        "Leave empty to read all projects."
                    )
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
            "Read saved Officina project memories, decisions, facts, and notes. "
            "Use this when prior project decisions or remembered facts matter."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "project": {
                    "type": "string",
                    "description": (
                        "Optional project name. "
                        "Leave empty to read recent memories from all projects."
                    )
                },
                "limit": {
                    "type": "integer",
                    "minimum": 1,
                    "maximum": 20,
                    "description": "Maximum number of memories to return."
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
            "This is a protected write action: it NEVER writes immediately. "
            "It creates an approval request that the user must approve or reject."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title."
                },
                "priority": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                    "description": "Task priority."
                },
                "project": {
                    "type": "string",
                    "description": "Project name."
                }
            },
            "required": ["title", "priority", "project"],
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
                task
                for task in tasks
                if task["project"].lower()
                == project.lower()
            ]

        if status != "all":
            tasks = [
                task
                for task in tasks
                if task["status"] == status
            ]

        return {
            "tool": "list_tasks",
            "count": len(tasks),
            "items": tasks[:30]
        }

    if name == "list_memories":
        project = arguments.get("project")
        limit = arguments.get("limit", 8)

        memories = list_memories(
            project=project,
            limit=limit
        )

        return {
            "tool": "list_memories",
            "count": len(memories),
            "items": memories
        }

    if name == "create_task":
        approval = create_approval(
            "create_task",
            arguments,
            agent_name or "unknown-agent",
            run_id
        )

        return {
            "tool": "create_task",
            "status": "approval_required",
            "approval_id": approval["id"],
            "message": (
                "Task creation has NOT been executed. "
                "A human approval is required."
            ),
            "proposed_action": arguments
        }

    return {
        "error": "Unknown tool: " + name
    }


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
