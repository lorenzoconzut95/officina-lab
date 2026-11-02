from fastapi import APIRouter, HTTPException

from models import TaskCreate, TaskUpdate
from services.tasks import (
    list_tasks,
    get_task,
    create_task,
    update_task,
    delete_task
)


router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"]
)


@router.get("")
def read_tasks():
    return list_tasks()


@router.get("/{task_id}")
def read_task(task_id: int):
    task = get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@router.post("", status_code=201)
def create_new_task(task: TaskCreate):
    return create_task(
        task.title,
        task.priority,
        task.project
    )


@router.patch("/{task_id}")
def update_existing_task(
    task_id: int,
    task: TaskUpdate
):
    updated_task = update_task(
        task_id,
        task.title,
        task.status,
        task.priority,
        task.project
    )

    if updated_task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return updated_task


@router.delete("/{task_id}")
def delete_existing_task(task_id: int):
    deleted = delete_task(task_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "message": "Task deleted"
    }