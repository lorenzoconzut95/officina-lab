from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "agent_id": row["agent_id"],
        "agent_name": row["agent_name"],
        "task": row["task"],
        "status": row["status"],
        "output": row["output"],
        "started_at": row["started_at"],
        "ended_at": row["ended_at"]
    }


def list_runs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            runs.id,
            runs.agent_id,
            agents.name AS agent_name,
            runs.task,
            runs.status,
            runs.output,
            runs.started_at,
            runs.ended_at
        FROM runs
        JOIN agents ON agents.id = runs.agent_id
        ORDER BY runs.id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [row_to_dict(row) for row in rows]


def create_run(agent_id, task):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO runs (
            agent_id,
            task,
            status
        )
        VALUES (?, ?, ?)
    """, (
        agent_id,
        task,
        "running"
    ))

    connection.commit()
    run_id = cursor.lastrowid
    connection.close()

    return get_run(run_id)


def get_run(run_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            runs.id,
            runs.agent_id,
            agents.name AS agent_name,
            runs.task,
            runs.status,
            runs.output,
            runs.started_at,
            runs.ended_at
        FROM runs
        JOIN agents ON agents.id = runs.agent_id
        WHERE runs.id = ?
    """, (run_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def finish_run(run_id, status, output):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE runs
        SET
            status = ?,
            output = ?,
            ended_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        status,
        output,
        run_id
    ))

    connection.commit()
    connection.close()

    return get_run(run_id)
