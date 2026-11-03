import json

from repositories.tasks import list_tasks
from repositories.memories import list_memories


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
    }
]


def execute_tool(name, arguments):
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

    return {
        "error": "Unknown tool: " + name
    }


def execute_tool_json(name, arguments_json):
    try:
        arguments = json.loads(
            arguments_json or "{}"
        )
    except json.JSONDecodeError:
        arguments = {}

    return execute_tool(
        name,
        arguments
    )
