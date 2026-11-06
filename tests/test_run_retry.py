import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from fastapi import HTTPException

import database
from repositories.incidents import get_incident
from repositories.runs import create_run, get_run
from routes.runs import prepare_run_retry


class RunRetryTests(unittest.TestCase):
    def test_rate_limit_retry_is_prepared_once_and_keeps_incident_link(self):
        with TemporaryDirectory() as directory, patch.object(
            database, "DB_NAME", str(Path(directory) / "test.db")
        ):
            database.init_db()
            connection = database.get_connection()
            with connection:
                agent_id = connection.execute(
                    "INSERT INTO agents (name, role) VALUES ('Bug Hunter', 'debug')"
                ).lastrowid
            connection.close()
            source = create_run(agent_id, "Inspect the incident")
            oversized = create_run(agent_id, "An oversized task")
            connection = database.get_connection()
            with connection:
                connection.executemany(
                    "UPDATE runs SET status = 'failed', output = ? WHERE id = ?",
                    [("OpenAI token rate limit reached (429).", source["id"]),
                     ("Model request blocked locally before sending to OpenAI.", oversized["id"])]
                )
                incident_id = connection.execute(
                    "INSERT INTO incidents (incident_key, status, analysis_run_id) "
                    "VALUES ('test', 'investigating', ?)", (source["id"],)
                ).lastrowid
            connection.close()

            with ThreadPoolExecutor(max_workers=2) as pool:
                first, second = pool.map(prepare_run_retry, [source["id"], source["id"]])

            self.assertEqual(first["id"], second["id"])
            self.assertNotEqual(first["id"], source["id"])
            self.assertEqual(first["agent_id"], agent_id)
            self.assertEqual(first["task"], source["task"])
            self.assertEqual(first["status"], "running")
            self.assertIsNone(first["execution_started_at"])
            self.assertEqual(get_run(source["id"])["status"], "failed")
            self.assertEqual(get_incident(incident_id)["analysis_run_id"], first["id"])

            with self.assertRaises(HTTPException) as error:
                prepare_run_retry(oversized["id"])
            self.assertEqual(error.exception.status_code, 409)
