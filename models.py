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