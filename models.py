from typing import Optional
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    priority: str = "medium"
    project: str = "Officina Lab"


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    project: Optional[str] = None


class AgentCreate(BaseModel):
    name: str
    role: str
    goal: str = ""
    project: str = "Officina Lab"


class AgentStatusUpdate(BaseModel):
    status: str


class RunCreate(BaseModel):
    agent_id: int
    task: str


class RunFinish(BaseModel):
    status: str = "completed"
    output: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float = 0


class MemoryCreate(BaseModel):
    content: str
    project: str = "Officina Lab"
    memory_type: str = "note"
