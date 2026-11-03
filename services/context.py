from pathlib import Path


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


def build_run_context(agent, task):
    system_context = load_officina_context()

    sources = [
        "context/officina.md",
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
        "OFFICINA SYSTEM CONTEXT\n"
        + system_context
    )

    return {
        "text": text,
        "sources": sources
    }
