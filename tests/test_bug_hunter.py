import unittest
from unittest.mock import patch

from services.llm_provider import role_instructions
from services.tools import execute_tool


class BugHunterTests(unittest.TestCase):
    def test_bug_hunter_gets_specialized_instructions(self):
        agent = {
            "name": "Bug Hunter",
            "role": "Debugging Agent"
        }

        instructions = role_instructions(agent)

        self.assertIn("BUG HUNTER MODE", instructions)
        self.assertIn("list_recent_errors", instructions)
        self.assertIn("Separate observed evidence", instructions)

    @patch("services.tools.log_tool_call")
    @patch("services.tools.list_errors")
    def test_list_recent_errors_tool_returns_error_log(
        self,
        mock_list_errors,
        mock_log_tool_call
    ):
        mock_list_errors.return_value = [
            {
                "id": 1,
                "run_id": 42,
                "agent_name": "Explorer",
                "task": "Test failure",
                "error_message": "Example error",
                "created_at": "2026-11-04 09:00:00"
            }
        ]

        result = execute_tool(
            "list_recent_errors",
            {"limit": 5},
            agent_name="Bug Hunter",
            run_id=99
        )

        self.assertEqual(result["tool"], "list_recent_errors")
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["items"][0]["run_id"], 42)
        self.assertEqual(
            result["items"][0]["error_message"],
            "Example error"
        )
        mock_log_tool_call.assert_called_once()


if __name__ == "__main__":
    unittest.main()
