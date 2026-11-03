import json

from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "run_id": row["run_id"],
        "agent_name": row["agent_name"],
        "tool_name": row["tool_name"],
        "arguments": json.loads(row["arguments"]),
        "result": json.loads(row["result"]),
        "created_at": row["created_at"]
    }


def log_tool_call(
    run_id,
    agent_name,
    tool_name,
    arguments,
    result
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tool_calls (
            run_id,
            agent_name,
            tool_name,
            arguments,
            result
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        run_id,
        agent_name,
        tool_name,
        json.dumps(arguments, ensure_ascii=False),
        json.dumps(result, ensure_ascii=False)
    ))

    connection.commit()
    tool_call_id = cursor.lastrowid

    cursor.execute("""
        SELECT *
        FROM tool_calls
        WHERE id = ?
    """, (tool_call_id,))

    row = cursor.fetchone()
    connection.close()

    return row_to_dict(row)


def list_tool_calls(limit=50):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tool_calls
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    return [row_to_dict(row) for row in rows]
