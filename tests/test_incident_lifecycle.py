import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import database
from repositories.errors import create_error
from repositories.incidents import create_incident
from services.incidents import sync_incidents


class IncidentLifecycleTests(unittest.TestCase):
    def test_context_window_errors_share_the_existing_incident(self):
        with TemporaryDirectory() as directory, patch.object(
            database, "DB_NAME", str(Path(directory) / "test.db")
        ):
            database.init_db()
            legacy = (
                "LLM execution failed: Error code: 400 - {'error': {'message': "
                "'Your input exceeds the context window of this model.', "
                "'code': 'context_length_exceeded'}}"
            )
            create_error(56, "Bug Hunter", "Test", legacy)
            existing = create_incident(
                legacy.lower()[:120], "low", 1, 56, "Bug Hunter", "Test", legacy
            )
            database.init_db()
            create_error(73, "Bug Hunter", "Test", (
                "OpenAI rejected the request because it exceeds the model's context window. "
                "Reduce the task or context and create a new run."
            ))

            incidents = sync_incidents()

        self.assertEqual(len(incidents), 1)
        incident = incidents[0]
        self.assertEqual(incident["id"], existing["id"])
        self.assertEqual(incident["incident_key"], "context_length_exceeded")
        self.assertEqual(incident["occurrences"], 2)

    def test_local_request_blocks_share_the_existing_incident(self):
        with TemporaryDirectory() as directory, patch.object(
            database, "DB_NAME", str(Path(directory) / "test.db")
        ):
            database.init_db()
            legacy = "Model request is 540,386 bytes. The limit is 524,288 bytes."
            create_error(72, "Bug Hunter", "Test", legacy)
            existing = create_incident(legacy.lower(), "low", 1, 72, "Bug Hunter", "Test", legacy)

            database.init_db()
            for run_id, size in [(73, 600_000), (74, 700_000)]:
                message = (
                    "Model request blocked locally before sending to OpenAI. "
                    f"The request is {size:,} bytes. The limit is 524,288 bytes."
                )
                create_error(run_id, "Bug Hunter", "Test", message)

            incidents = sync_incidents()

        self.assertEqual(len(incidents), 1)
        incident = incidents[0]
        self.assertEqual(incident["id"], existing["id"])
        self.assertEqual(incident["incident_key"], "model_request_too_large")
        self.assertEqual(incident["occurrences"], 3)
        self.assertEqual(incident["latest_run_id"], 74)

    @patch("services.incidents.repo_list_incidents")
    @patch("services.incidents.refresh_incident")
    @patch("services.incidents.repo_update_incident_status")
    @patch("services.incidents.get_incident_by_key")
    @patch("services.incidents.derive_incidents")
    def test_resolved_incident_reopens_when_occurrence_count_increases(
        self,
        mock_derive,
        mock_get_by_key,
        mock_update_status,
        mock_refresh,
        mock_list
    ):
        mock_derive.return_value = [{
            "key": "openai_api_key",
            "severity": "high",
            "count": 4,
            "latest_run_id": 99,
            "latest_agent_name": "Bug Hunter",
            "latest_task": "Analyze recurring API key failure",
            "latest_error_message": "invalid_api_key"
        }]

        mock_get_by_key.return_value = {
            "id": 7,
            "incident_key": "openai_api_key",
            "status": "resolved",
            "occurrences": 3
        }

        mock_list.return_value = []

        sync_incidents()

        mock_update_status.assert_called_once_with(
            7,
            "open"
        )
        mock_refresh.assert_called_once()

    @patch("services.incidents.repo_list_incidents")
    @patch("services.incidents.refresh_incident")
    @patch("services.incidents.repo_update_incident_status")
    @patch("services.incidents.get_incident_by_key")
    @patch("services.incidents.derive_incidents")
    def test_resolved_incident_stays_resolved_without_new_occurrence(
        self,
        mock_derive,
        mock_get_by_key,
        mock_update_status,
        mock_refresh,
        mock_list
    ):
        mock_derive.return_value = [{
            "key": "openai_api_key",
            "severity": "high",
            "count": 3,
            "latest_run_id": 21,
            "latest_agent_name": "Explorer",
            "latest_task": "Historical failure",
            "latest_error_message": "invalid_api_key"
        }]

        mock_get_by_key.return_value = {
            "id": 7,
            "incident_key": "openai_api_key",
            "status": "resolved",
            "occurrences": 3
        }

        mock_list.return_value = []

        sync_incidents()

        mock_update_status.assert_not_called()
        mock_refresh.assert_called_once()


if __name__ == "__main__":
    unittest.main()
