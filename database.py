import sqlite3


DB_NAME = "tasks.db"


def get_connection():
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def ensure_column(cursor, table, column, definition):
    cursor.execute("PRAGMA table_info(" + table + ")")
    existing_columns = {
        row[1]
        for row in cursor.fetchall()
    }

    if column not in existing_columns:
        cursor.execute(
            "ALTER TABLE " + table +
            " ADD COLUMN " + column + " " + definition
        )


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'todo',
            priority TEXT NOT NULL DEFAULT 'medium',
            project TEXT NOT NULL DEFAULT 'Officina Lab',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            task_title TEXT NOT NULL,
            project TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'idle',
            project TEXT NOT NULL DEFAULT 'Officina Lab',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            project TEXT NOT NULL DEFAULT 'Officina Lab',
            memory_type TEXT NOT NULL DEFAULT 'note',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            task TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'running',
            output TEXT,
            started_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            ended_at TEXT,
            tokens_in INTEGER NOT NULL DEFAULT 0,
            tokens_out INTEGER NOT NULL DEFAULT 0,
            cost_usd REAL NOT NULL DEFAULT 0,
            duration_seconds INTEGER,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    """)

    ensure_column(
        cursor,
        "runs",
        "tokens_in",
        "INTEGER NOT NULL DEFAULT 0"
    )

    ensure_column(
        cursor,
        "runs",
        "tokens_out",
        "INTEGER NOT NULL DEFAULT 0"
    )

    ensure_column(
        cursor,
        "runs",
        "cost_usd",
        "REAL NOT NULL DEFAULT 0"
    )

    ensure_column(
        cursor,
        "runs",
        "duration_seconds",
        "INTEGER"
    )

    ensure_column(
        cursor,
        "runs",
        "model",
        "TEXT"
    )

    ensure_column(
        cursor,
        "runs",
        "context_sources",
        "TEXT"
    )

    ensure_column(
        cursor,
        "runs",
        "context_snapshot",
        "TEXT"
    )

    connection.commit()
    connection.close()
