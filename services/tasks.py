from database import get_connection


def list_tasks():
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


def get_task(task_id):
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
        return None

    return {
        "id": row[0],
        "title": row[1],
        "status": row[2]
    }


def create_task(title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (title, status)
        VALUES (?, ?)
    """, (
        title,
        "todo"
    ))

    connection.commit()
    task_id = cursor.lastrowid
    connection.close()

    return {
        "id": task_id,
        "title": title,
        "status": "todo"
    }


def update_task(task_id, title=None, status=None):
    existing_task = get_task(task_id)

    if existing_task is None:
        return None

    new_title = title if title is not None else existing_task["title"]
    new_status = status if status is not None else existing_task["status"]

    connection = get_connection()
    cursor = connection.cursor()

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


def delete_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    deleted_rows = cursor.rowcount
    connection.close()

    return deleted_rows > 0