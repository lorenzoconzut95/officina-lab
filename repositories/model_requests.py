from database import get_connection


def record_model_request(run_id, model, request_bytes):
    connection = get_connection()
    try:
        with connection:
            cursor = connection.execute("""
                INSERT INTO model_requests (run_id, model, request_bytes)
                VALUES (?, ?, ?)
            """, (run_id, model, request_bytes))
            return cursor.lastrowid
    finally:
        connection.close()


def record_model_request_usage(request_id, tokens_in, tokens_out):
    connection = get_connection()
    try:
        with connection:
            connection.execute("""
                UPDATE model_requests
                SET tokens_in = ?, tokens_out = ?
                WHERE id = ?
            """, (tokens_in, tokens_out, request_id))
    finally:
        connection.close()
