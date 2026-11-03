from repositories.memories import (
    list_memories as repo_list_memories,
    create_memory as repo_create_memory
)


def list_memories(project=None, limit=20):
    return repo_list_memories(
        project=project,
        limit=limit
    )


def create_memory(content, project, memory_type):
    return repo_create_memory(
        content,
        project,
        memory_type
    )
