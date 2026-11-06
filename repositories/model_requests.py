from database import get_connection


def list_model_requests(run_id):
    connection = get_connection()
    try:
        rows = connection.execute("""
            SELECT started_at, tokens_in, tokens_out, outcome, http_status
            FROM model_requests
            WHERE run_id = ?
            ORDER BY id
        """, (run_id,)).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def record_model_request(run_id, model, request_bytes):
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute("""
                INSERT INTO model_requests (run_id, model, request_bytes, outcome)
                VALUES (?, ?, ?, 'pending')
            """, (run_id, model, request_bytes))
            return cursor.lastrowid
    finally:
        connection.close()


def finish_model_request(request_id, outcome, *, tokens_in=None, tokens_out=None, http_status=None):
    connection = get_connection()
    try:
        with connection:
            connection.execute("""
                UPDATE model_requests
                SET outcome = ?, tokens_in = ?, tokens_out = ?, http_status = ?
                WHERE id = ?
            """, (outcome, tokens_in, tokens_out, http_status, request_id))
    finally:
        connection.close()
