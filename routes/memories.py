from fastapi import APIRouter

from models import MemoryCreate
from services.memories import (
    list_memories,
    create_memory
)


router = APIRouter(
    prefix="/api/memories",
    tags=["memories"]
)


@router.get("")
def read_memories(
    project: str = None,
    limit: int = 20
):
    return list_memories(
        project=project,
        limit=limit
    )


@router.post("", status_code=201)
def create_new_memory(memory: MemoryCreate):
    return create_memory(
        memory.content,
        memory.project,
        memory.memory_type
    )
