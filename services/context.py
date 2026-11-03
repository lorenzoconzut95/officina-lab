from pathlib import Path

from services.memories import list_memories


CONTEXT_PATH = (
    Path(__file__).resolve().parent.parent
    / "context"
    / "officina.md"
)


def load_officina_context():
    if not CONTEXT_PATH.exists():
        return (
            "Officina Lab context file is missing."
        )

    return CONTEXT_PATH.read_text(
        encoding="utf-8"
    )


def format_project_memories(project):
    memories = list_memories(
        project=project,
        limit=8
    )

    if not memories:
        return (
            "No project memories available."
        )

    lines = []

    for memory in memories:
        lines.append(
            "- [" + memory["memory_type"] + "] "
            + memory["content"]
        )

    return "\n".join(lines)


def build_run_context(agent, task):
    system_context = load_officina_context()
    memory_context = format_project_memories(
        agent["project"]
    )

    sources = [
        "context/officina.md",
        "memory:project:" + agent["project"],
        "agent:" + agent["name"],
        "project:" + agent["project"],
        "task:current_run"
    ]

    text = (
        "AGENT IDENTITY\n"
        "Agent name: " + agent["name"] + "\n"
        "Role: " + agent["role"] + "\n"
        "Project: " + agent["project"] + "\n\n"
        "CURRENT TASK\n"
        + task + "\n\n"
        "PROJECT MEMORY\n"
        + memory_context + "\n\n"
        "OFFICINA SYSTEM CONTEXT\n"
        + system_context
    )

    return {
        "text": text,
        "sources": sources
    }
