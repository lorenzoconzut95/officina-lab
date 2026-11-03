from database import get_connection


def create_activity(action, task_title, project):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO activities (
            action,
            task_title,
            project
        )
        VALUES (?, ?, ?)
    """, (
        action,
        task_title,
        project
    ))

    connection.commit()
    connection.close()


def list_activities(limit=20):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, action, task_title, project, created_at
        FROM activities
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    return [
        {
            "id": row["id"],
            "action": row["action"],
            "task_title": row["task_title"],
            "project": row["project"],
            "created_at": row["created_at"]
        }
        for row in rows
    ]
