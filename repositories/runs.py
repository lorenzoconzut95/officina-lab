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
        "execution_started_at": row["execution_started_at"],
        "ended_at": row["ended_at"],
        "tokens_in": row["tokens_in"],
        "tokens_out": row["tokens_out"],
        "cost_usd": row["cost_usd"],
        "duration_seconds": row["duration_seconds"],
        "model": row["model"],
        "context_sources": row["context_sources"],
        "context_snapshot": row["context_snapshot"]
    }


def run_select():
    return """
        SELECT
            runs.id,
            runs.agent_id,
            agents.name AS agent_name,
            runs.task,
            runs.status,
            runs.output,
            runs.started_at,
            runs.execution_started_at,
            runs.ended_at,
            runs.tokens_in,
            runs.tokens_out,
            runs.cost_usd,
            runs.duration_seconds,
            runs.model,
            runs.context_sources,
            runs.context_snapshot
        FROM runs
        JOIN agents ON agents.id = runs.agent_id
    """


def list_runs():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        run_select() + """
        ORDER BY runs.id DESC
        """
    )

    rows = cursor.fetchall()
    connection.close()

    return [
        row_to_dict(row)
        for row in rows
    ]


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


def mark_execution_started(run_id):
    connection = get_connection()
    try:
        connection.execute(
            """
            UPDATE runs
            SET execution_started_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (run_id,)
        )
        connection.commit()
    finally:
        connection.close()


def get_run(run_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        run_select() + """
        WHERE runs.id = ?
        """,
        (run_id,)
    )

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def finish_run(
    run_id,
    status,
    output,
    tokens_in,
    tokens_out,
    cost_usd
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE runs
        SET
            status = ?,
            output = ?,
            tokens_in = ?,
            tokens_out = ?,
            cost_usd = ?,
            ended_at = CURRENT_TIMESTAMP,
            duration_seconds = CAST(
                (
                    julianday(CURRENT_TIMESTAMP) -
                    julianday(started_at)
                ) * 86400
                AS INTEGER
            )
        WHERE id = ?
    """, (
        status,
        output,
        tokens_in,
        tokens_out,
        cost_usd,
        run_id
    ))

    connection.commit()
    connection.close()

    return get_run(run_id)


def set_run_context(
    run_id,
    model,
    context_sources,
    context_snapshot
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE runs
        SET
            model = ?,
            context_sources = ?,
            context_snapshot = ?
        WHERE id = ?
    """, (
        model,
        context_sources,
        context_snapshot,
        run_id
    ))

    connection.commit()
    connection.close()

    return get_run(run_id)
