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
            goal TEXT NOT NULL DEFAULT '',
            status TEXT NOT NULL DEFAULT 'idle',
            project TEXT NOT NULL DEFAULT 'Officina Lab',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    ensure_column(
        cursor,
        "agents",
        "goal",
        "TEXT NOT NULL DEFAULT ''"
    )

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
        CREATE TABLE IF NOT EXISTS approvals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT NOT NULL,
            payload TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            agent_name TEXT NOT NULL,
            run_id INTEGER,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tool_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            agent_name TEXT NOT NULL,
            tool_name TEXT NOT NULL,
            arguments TEXT NOT NULL,
            result TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS errors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER,
            agent_name TEXT NOT NULL,
            task TEXT NOT NULL,
            error_message TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_key TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL DEFAULT 'open',
            severity TEXT NOT NULL DEFAULT 'low',
            occurrences INTEGER NOT NULL DEFAULT 1,
            latest_run_id INTEGER,
            latest_agent_name TEXT,
            latest_task TEXT,
            latest_error_message TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            resolved_at TEXT
        )
    """)

    ensure_column(cursor, "incidents", "analysis_run_id", "INTEGER")
    ensure_column(cursor, "incidents", "builder_run_id", "INTEGER")
    ensure_column(cursor, "incidents", "approval_id", "INTEGER")
    ensure_column(cursor, "incidents", "verification_run_id", "INTEGER")

    # Keep the existing incident ID and links when adopting the stable key.
    cursor.execute("""
        UPDATE incidents
        SET incident_key = 'model_request_too_large'
        WHERE id = (
            SELECT MIN(id) FROM incidents
            WHERE incident_key LIKE 'model request is %'
        ) AND NOT EXISTS (
            SELECT 1 FROM incidents WHERE incident_key = 'model_request_too_large'
        )
    """)

    cursor.execute("""
        UPDATE incidents
        SET incident_key = 'context_length_exceeded'
        WHERE id = (
            SELECT MIN(id) FROM incidents
            WHERE incident_key LIKE 'llm execution failed:%your input exceeds the context window%'
               OR incident_key LIKE 'openai rejected the request because it exceeds the model''s context window.%'
        ) AND NOT EXISTS (
            SELECT 1 FROM incidents WHERE incident_key = 'context_length_exceeded'
        )
    """)

    cursor.execute("""
        UPDATE incidents
        SET incident_key = 'openai_token_rate_limit'
        WHERE id = (
            SELECT MIN(id) FROM incidents
            WHERE lower(latest_error_message) LIKE 'openai token rate limit reached (429).%'
               OR lower(latest_error_message) LIKE '%rate limit%tokens per min%'
        ) AND NOT EXISTS (
            SELECT 1 FROM incidents WHERE incident_key = 'openai_token_rate_limit'
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

    ensure_column(cursor, "runs", "tokens_in", "INTEGER NOT NULL DEFAULT 0")
    ensure_column(cursor, "runs", "tokens_out", "INTEGER NOT NULL DEFAULT 0")
    ensure_column(cursor, "runs", "cost_usd", "REAL NOT NULL DEFAULT 0")
    ensure_column(cursor, "runs", "duration_seconds", "INTEGER")
    ensure_column(cursor, "runs", "model", "TEXT")
    ensure_column(cursor, "runs", "context_sources", "TEXT")
    ensure_column(cursor, "runs", "context_snapshot", "TEXT")
    ensure_column(cursor, "runs", "execution_started_at", "TEXT")
    ensure_column(cursor, "runs", "execution_claimed_at", "TEXT")
    ensure_column(cursor, "runs", "retry_of_run_id", "INTEGER")
    cursor.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS runs_retry_of_run_id
        ON runs (retry_of_run_id)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS model_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES runs(id),
            model TEXT NOT NULL,
            request_bytes INTEGER NOT NULL,
            started_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        )
    """)

    connection.commit()
    connection.close()
