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
