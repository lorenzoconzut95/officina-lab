import unittest
from unittest.mock import patch

from services.incidents import sync_incidents


class IncidentLifecycleTests(unittest.TestCase):
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
