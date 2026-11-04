from pathlib import Path


ROOT_PATH = Path(__file__).resolve().parent.parent

ALLOWED_SUFFIXES = {
    ".py",
    ".md",
    ".txt",
    ".json",
    ".html",
    ".css",
    ".js"
}

EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules"
}

EXCLUDED_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    "tasks.db"
}


def _is_safe_path(path):
    try:
        path.resolve().relative_to(
            ROOT_PATH.resolve()
        )
    except ValueError:
        return False

    if any(
        part in EXCLUDED_PARTS
        for part in path.parts
    ):
        return False

    if path.name in EXCLUDED_NAMES:
        return False

    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        return False

    return True


def list_project_files(limit=100):
    items = []

    for path in ROOT_PATH.rglob("*"):
        if not path.is_file():
            continue

        if not _is_safe_path(path):
            continue

        relative = path.relative_to(
            ROOT_PATH
        ).as_posix()

        items.append(relative)

    items.sort()

    return items[:limit]


def read_project_file(path, max_chars=12000):
    candidate = (
        ROOT_PATH
        / path
    )

    if not candidate.exists():
        return {
            "error": "file_not_found",
            "path": path
        }

    if not candidate.is_file():
        return {
            "error": "not_a_file",
            "path": path
        }

    if not _is_safe_path(candidate):
        return {
            "error": "file_not_allowed",
            "path": path
        }

    text = candidate.read_text(
        encoding="utf-8",
        errors="replace"
    )

    truncated = len(text) > max_chars

    return {
        "path": path,
        "content": text[:max_chars],
        "truncated": truncated
    }
