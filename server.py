from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3


DB_NAME = "tasks.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


class OfficinaHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def get_task_id(self):
        parts = self.path.strip("/").split("/")

        if len(parts) == 3 and parts[0] == "api" and parts[1] == "tasks":
            try:
                return int(parts[2])
            except ValueError:
                return None

        return None

    def do_GET(self):

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(
                b"<h1>Officina Lab</h1><p>Server v0.3 is running.</p>"
            )

        elif self.path == "/health":
            self.send_json({
                "status": "ok"
            })

        elif self.path == "/api/tasks":
            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT id, title, status
                FROM tasks
            """)

            rows = cursor.fetchall()
            connection.close()

            tasks = []

            for row in rows:
                tasks.append({
                    "id": row[0],
                    "title": row[1],
                    "status": row[2]
                })

            self.send_json(tasks)

        else:
            task_id = self.get_task_id()

            if task_id is not None:
                connection = get_connection()
                cursor = connection.cursor()

                cursor.execute("""
                    SELECT id, title, status
                    FROM tasks
                    WHERE id = ?
                """, (task_id,))

                row = cursor.fetchone()
                connection.close()

                if row:
                    self.send_json({
                        "id": row[0],
                        "title": row[1],
                        "status": row[2]
                    })
                else:
                    self.send_json({
                        "error": "Task not found"
                    }, 404)

            else:
                self.send_json({
                    "error": "Not found"
                }, 404)

    def do_POST(self):

        if self.path == "/api/tasks":

            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)
            new_task_data = json.loads(body.decode())

            connection = get_connection()
            cursor = connection.cursor()

            cursor.execute("""
                INSERT INTO tasks (title, status)
                VALUES (?, ?)
            """, (
                new_task_data["title"],
                "todo"
            ))

            connection.commit()
            task_id = cursor.lastrowid
            connection.close()

            self.send_json({
                "id": task_id,
                "title": new_task_data["title"],
                "status": "todo"
            }, 201)

        else:
            self.send_json({
                "error": "Not found"
            }, 404)

    def do_PATCH(self):

        task_id = self.get_task_id()

        if task_id is None:
            self.send_json({
                "error": "Not found"
            }, 404)
            return

        content_length = int(
            self.headers.get("Content-Length", 0)
        )

        body = self.rfile.read(content_length)
        update_data = json.loads(body.decode())

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            SELECT id, title, status
            FROM tasks
            WHERE id = ?
        """, (task_id,))

        row = cursor.fetchone()

        if row is None:
            connection.close()

            self.send_json({
                "error": "Task not found"
            }, 404)

            return

        new_title = update_data.get("title", row[1])
        new_status = update_data.get("status", row[2])

        cursor.execute("""
            UPDATE tasks
            SET title = ?, status = ?
            WHERE id = ?
        """, (
            new_title,
            new_status,
            task_id
        ))

        connection.commit()
        connection.close()

        self.send_json({
            "id": task_id,
            "title": new_title,
            "status": new_status
        })

    def do_DELETE(self):

        task_id = self.get_task_id()

        if task_id is None:
            self.send_json({
                "error": "Not found"
            }, 404)
            return

        connection = get_connection()
        cursor = connection.cursor()

        cursor.execute("""
            DELETE FROM tasks
            WHERE id = ?
        """, (task_id,))

        connection.commit()

        deleted_rows = cursor.rowcount

        connection.close()

        if deleted_rows == 0:
            self.send_json({
                "error": "Task not found"
            }, 404)

        else:
            self.send_json({
                "message": "Task deleted"
            })


init_db()

server = HTTPServer(
    ("localhost", 8000),
    OfficinaHandler
)

print(
    "Officina Server running on http://localhost:8000"
)

server.serve_forever()