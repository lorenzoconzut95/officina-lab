from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "run_id": row["run_id"],
        "agent_name": row["agent_name"],
        "task": row["task"],
        "error_message": row["error_message"],
        "created_at": row["created_at"]
    }


def create_error(
    run_id,
    agent_name,
    task,
    error_message
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO errors (
            run_id,
            agent_name,
            task,
            error_message
        )
        VALUES (?, ?, ?, ?)
    """, (
        run_id,
        agent_name,
        task,
        error_message
    ))

    connection.commit()
    error_id = cursor.lastrowid

    cursor.execute("""
        SELECT *
        FROM errors
        WHERE id = ?
    """, (error_id,))

    row = cursor.fetchone()
    connection.close()

    return row_to_dict(row)


def list_errors(limit=50):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM errors
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    return [
        row_to_dict(row)
        for row in rows
    ]
