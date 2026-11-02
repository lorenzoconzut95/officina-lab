from fastapi import APIRouter, HTTPException

from database import get_connection
from models import TaskCreate, TaskUpdate


router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"]
)


@router.get("")
def get_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, status
        FROM tasks
    """)

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "status": row[2]
        }
        for row in rows
    ]


@router.get("/{task_id}")
def get_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, status
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "id": row[0],
        "title": row[1],
        "status": row[2]
    }


@router.post("", status_code=201)
def create_task(task: TaskCreate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, status)
        VALUES (?, ?)
    """, (
        task.title,
        "todo"
    ))

    connection.commit()
    task_id = cursor.lastrowid
    connection.close()

    return {
        "id": task_id,
        "title": task.title,
        "status": "todo"
    }


@router.patch("/{task_id}")
def update_task(task_id: int, task: TaskUpdate):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, title, status
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()

    if row is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    new_title = task.title if task.title is not None else row[1]
    new_status = task.status if task.status is not None else row[2]

    cursor.execute("""
        UPDATE tasks
        SET title = ?, status = ?
        WHERE id = ?
    """, (
        new_title,
        new_status,
        task_id
    ))

    connection.commit()
    connection.close()

    return {
        "id": task_id,
        "title": new_title,
        "status": new_status
    }


@router.delete("/{task_id}")
def delete_task(task_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    connection.commit()

    deleted_rows = cursor.rowcount

    connection.close()

    if deleted_rows == 0:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "message": "Task deleted"
    }