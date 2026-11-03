import json

from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "action": row["action"],
        "payload": json.loads(row["payload"]),
        "status": row["status"],
        "agent_name": row["agent_name"],
        "run_id": row["run_id"],
        "created_at": row["created_at"],
        "resolved_at": row["resolved_at"]
    }


def list_approvals(status=None):
    connection = get_connection()
    cursor = connection.cursor()

    if status:
        cursor.execute("""
            SELECT *
            FROM approvals
            WHERE status = ?
            ORDER BY id DESC
        """, (status,))
    else:
        cursor.execute("""
            SELECT *
            FROM approvals
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()
    connection.close()

    return [
        row_to_dict(row)
        for row in rows
    ]


def create_approval(
    action,
    payload,
    agent_name,
    run_id
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO approvals (
            action,
            payload,
            status,
            agent_name,
            run_id
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        action,
        json.dumps(
            payload,
            ensure_ascii=False
        ),
        "pending",
        agent_name,
        run_id
    ))

    connection.commit()
    approval_id = cursor.lastrowid

    cursor.execute("""
        SELECT *
        FROM approvals
        WHERE id = ?
    """, (approval_id,))

    row = cursor.fetchone()
    connection.close()

    return row_to_dict(row)


def get_approval(approval_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM approvals
        WHERE id = ?
    """, (approval_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def resolve_approval(
    approval_id,
    status
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE approvals
        SET
            status = ?,
            resolved_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        status,
        approval_id
    ))

    connection.commit()
    connection.close()

    return get_approval(
        approval_id
    )
