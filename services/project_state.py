from repositories.tasks import list_tasks
from repositories.memories import list_memories
from repositories.runs import list_runs
from repositories.tool_calls import list_tool_calls
from repositories.errors import list_errors
from repositories.agents import list_agents


def build_project_state(project, limit=5):
    limit = min(max(limit, 1), 8)

    project_tasks = [
        task for task in list_tasks()
        if task["project"].lower() == project.lower()
    ]

    project_memories = list_memories(
        project=project,
        limit=limit
    )

    project_agents = [
        agent for agent in list_agents()
        if agent["project"].lower() == project.lower()
    ]

    recent_runs = [
        run for run in list_runs()
        if any(
            agent["id"] == run["agent_id"]
            for agent in project_agents
        )
    ][:limit]

    recent_tool_calls = list_tool_calls(
        limit=limit
    )

    recent_errors = list_errors(
        limit=limit
    )

    return {
        "project": project,
        "covers": [
            "tasks",
            "agents",
            "memories",
            "recent_runs",
            "recent_tool_calls",
            "recent_errors"
        ],
        "summary": {
            "task_count": len(project_tasks),
            "todo_count": len([
                task for task in project_tasks
                if task["status"] == "todo"
            ]),
            "done_count": len([
                task for task in project_tasks
                if task["status"] == "done"
            ]),
            "agent_count": len(project_agents),
            "memory_count": len(project_memories),
            "recent_run_count": len(recent_runs),
            "recent_tool_call_count": len(recent_tool_calls),
            "recent_error_count": len(recent_errors)
        },
        "tasks": [
            {
                "id": task["id"],
                "title": task["title"],
                "status": task["status"],
                "priority": task["priority"]
            }
            for task in project_tasks
        ],
        "agents": [
            {
                "id": agent["id"],
                "name": agent["name"],
                "role": agent["role"],
                "goal": agent["goal"],
                "status": agent["status"]
            }
            for agent in project_agents
        ],
        "memories": [
            {
                "type": memory["memory_type"],
                "content": memory["content"]
            }
            for memory in project_memories
        ],
        "recent_runs": [
            {
                "id": run["id"],
                "agent_name": run["agent_name"],
                "task": run["task"],
                "status": run["status"],
                "context_sources": run["context_sources"],
                "output_preview": (
                    (run["output"] or "")[:280]
                )
            }
            for run in recent_runs
        ],
        "recent_tool_calls": [
            {
                "tool_name": item["tool_name"],
                "arguments": item["arguments"],
                "run_id": item["run_id"]
            }
            for item in recent_tool_calls
        ],
        "recent_errors": [
            {
                "run_id": item["run_id"],
                "agent_name": item["agent_name"],
                "task": item["task"],
                "error_message": item["error_message"]
            }
            for item in recent_errors
        ]
    }
