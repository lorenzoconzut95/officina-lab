from database import get_connection


def record_model_request(run_id, model, request_bytes):
    connection = get_connection()
    try:
        with connection:
            connection.execute("""
                INSERT INTO model_requests (run_id, model, request_bytes)
                VALUES (?, ?, ?)
            """, (run_id, model, request_bytes))
    finally:
        connection.close()
