from database import get_connection


def row_to_dict(row):
    return {
        "id": row["id"],
        "incident_key": row["incident_key"],
        "status": row["status"],
        "severity": row["severity"],
        "occurrences": row["occurrences"],
        "latest_run_id": row["latest_run_id"],
        "latest_agent_name": row["latest_agent_name"],
        "latest_task": row["latest_task"],
        "latest_error_message": row["latest_error_message"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "resolved_at": row["resolved_at"],
        "analysis_run_id": row["analysis_run_id"]
    }


def list_incidents():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM incidents
        ORDER BY
            CASE status
                WHEN 'open' THEN 1
                WHEN 'investigating' THEN 2
                WHEN 'resolved' THEN 3
                ELSE 4
            END,
            updated_at DESC,
            id DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return [row_to_dict(row) for row in rows]


def get_incident(incident_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM incidents
        WHERE id = ?
    """, (incident_id,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def get_incident_by_key(incident_key):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM incidents
        WHERE incident_key = ?
    """, (incident_key,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return None

    return row_to_dict(row)


def create_incident(
    incident_key,
    severity,
    occurrences,
    latest_run_id,
    latest_agent_name,
    latest_task,
    latest_error_message
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO incidents (
            incident_key,
            status,
            severity,
            occurrences,
            latest_run_id,
            latest_agent_name,
            latest_task,
            latest_error_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        incident_key,
        "open",
        severity,
        occurrences,
        latest_run_id,
        latest_agent_name,
        latest_task,
        latest_error_message
    ))

    connection.commit()
    incident_id = cursor.lastrowid
    connection.close()

    return get_incident(incident_id)


def refresh_incident(
    incident_id,
    severity,
    occurrences,
    latest_run_id,
    latest_agent_name,
    latest_task,
    latest_error_message
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE incidents
        SET
            severity = ?,
            occurrences = ?,
            latest_run_id = ?,
            latest_agent_name = ?,
            latest_task = ?,
            latest_error_message = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        severity,
        occurrences,
        latest_run_id,
        latest_agent_name,
        latest_task,
        latest_error_message,
        incident_id
    ))

    connection.commit()
    connection.close()

    return get_incident(incident_id)


def update_incident_status(incident_id, status):
    connection = get_connection()
    cursor = connection.cursor()

    if status == "resolved":
        cursor.execute("""
            UPDATE incidents
            SET
                status = ?,
                resolved_at = CURRENT_TIMESTAMP,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, incident_id))
    else:
        cursor.execute("""
            UPDATE incidents
            SET
                status = ?,
                resolved_at = NULL,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (status, incident_id))

    connection.commit()
    connection.close()

    return get_incident(incident_id)



def link_analysis_run(incident_id, run_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE incidents
        SET
            analysis_run_id = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (
        run_id,
        incident_id
    ))

    connection.commit()
    connection.close()

    return get_incident(incident_id)
