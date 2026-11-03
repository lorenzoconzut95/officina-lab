from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "content": row["content"],
        "project": row["project"],
        "memory_type": row["memory_type"],
        "created_at": row["created_at"]
    }


def list_memories(project=None, limit=20):
    connection = get_connection()
    cursor = connection.cursor()

    if project:
        cursor.execute("""
            SELECT *
            FROM memories
            WHERE project = ?
            ORDER BY id DESC
            LIMIT ?
        """, (project, limit))
    else:
        cursor.execute("""
            SELECT *
            FROM memories
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    connection.close()
    return [row_to_dict(row) for row in rows]


def create_memory(content, project, memory_type):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO memories (
            content,
            project,
            memory_type
        )
        VALUES (?, ?, ?)
    """, (
        content,
        project,
        memory_type
    ))

    connection.commit()
    memory_id = cursor.lastrowid

    cursor.execute("""
        SELECT *
        FROM memories
        WHERE id = ?
    """, (memory_id,))

    row = cursor.fetchone()
    connection.close()
    return row_to_dict(row)
