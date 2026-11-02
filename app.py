from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import sqlite3


app = FastAPI()

DB_NAME = "tasks.db"


class TaskCreate(BaseModel):
    title: str

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = None


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


@app.get("/")
def home():
    return {
        "project": "Officina Lab",
        "version": "0.4",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/tasks")
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


@app.post("/api/tasks", status_code=201)
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


@app.patch("/api/tasks/{task_id}")
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


@app.delete("/api/tasks/{task_id}")
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


init_db()