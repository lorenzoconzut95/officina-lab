from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "role": row["role"],
        "goal": row["goal"],
        "status": row["status"],
        "project": row["project"],
        "created_at": row["created_at"]
    }


def list_agents():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM agents
        ORDER BY id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [row_to_dict(row) for row in rows]


def create_agent(name, role, goal, project):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO agents (
            name,
            role,
            goal,
            status,
            project
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        name,
        role,
        goal,
        "idle",
        project
    ))

    connection.commit()
    agent_id = cursor.lastrowid
    connection.close()

    return get_agent(agent_id)


def get_agent(agent_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM agents
        WHERE id = ?
    """, (agent_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def update_agent_status(agent_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE agents
        SET status = ?
        WHERE id = ?
    """, (
        status,
        agent_id
    ))

    connection.commit()
    connection.close()

    return get_agent(agent_id)
