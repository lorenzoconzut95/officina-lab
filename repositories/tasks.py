from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "status": row["status"],
        "priority": row["priority"],
        "project": row["project"],
        "created_at": row["created_at"]
    }


def list_tasks():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY created_at DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [
        row_to_dict(row)
        for row in rows
    ]


def get_task(task_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def create_task(title, priority, project):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks (
            title,
            status,
            priority,
            project
        )
        VALUES (?, ?, ?, ?)
    """, (
        title,
        "todo",
        priority,
        project
    ))

    connection.commit()

    task_id = cursor.lastrowid

    connection.close()

    return get_task(task_id)


def update_task(
    task_id,
    title,
    status,
    priority,
    project
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tasks
        SET
            title = ?,
            status = ?,
            priority = ?,
            project = ?
        WHERE id = ?
    """, (
        title,
        status,
        priority,
        project,
        task_id
    ))

    connection.commit()
    connection.close()

    return get_task(task_id)


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