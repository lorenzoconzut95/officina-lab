import os
import unittest
from unittest.mock import patch

from services.executor import execute_run, humanize_llm_error


class ExecutorErrorMessageTests(unittest.TestCase):
    def test_rate_limit_message_matches_the_limit_type(self):
        cases = {
            "tokens per min (TPM)": (
                "OpenAI token rate limit reached (429). "
                "Wait before retrying or reduce the amount of text sent to the model."
            ),
            "requests per minute (RPM)": (
                "OpenAI request rate limit reached (429). "
                "Wait before retrying or send requests less frequently."
            ),
            "unspecified": (
                "OpenAI rate limit reached (429). "
                "Retry later or reduce request frequency."
            ),
        }
        for detail, expected in cases.items():
            with self.subTest(detail=detail):
                error = RuntimeError("Error code: 429 - Rate limit reached: " + detail)
                self.assertEqual(humanize_llm_error(error), expected)

    def test_context_window_error_takes_precedence_over_generic_400(self):
        error = RuntimeError("Error code: 400 - {'code': 'context_length_exceeded'}")

        self.assertEqual(
            humanize_llm_error(error),
            "OpenAI rejected the request because it exceeds the model's context window. "
            "Reduce the task or context and create a new run."
        )


@patch("services.executor.claim_run_execution", return_value=True)
class ExecutorApiKeyTests(unittest.TestCase):
    @patch("services.executor.run_llm")
    @patch("services.executor.finish_run")
    @patch("services.executor.set_run_context")
    @patch("services.executor.build_run_context")
    @patch("services.executor.get_agent")
    @patch("services.executor.get_run")
    @patch("services.executor.is_configured")
    @patch("services.executor.get_api_key_status")
    def test_placeholder_key_fails_before_llm_call(
        self,
        mock_key_status,
        mock_is_configured,
        mock_get_run,
        mock_get_agent,
        mock_build_context,
        mock_set_context,
        mock_finish_run,
        mock_run_llm,
        mock_claim_run_execution
    ):
        mock_key_status.return_value = {
            "configured": False,
            "reason": "placeholder"
        }
        mock_is_configured.return_value = False

        mock_get_run.return_value = {
            "id": 42,
            "agent_id": 3,
            "task": "Test placeholder key"
        }

        mock_get_agent.return_value = {
            "id": 3,
            "name": "Explorer",
            "role": "Research Agent",
            "goal": "Inspect project state",
            "project": "Officina Lab"
        }

        mock_build_context.return_value = {
            "text": "context",
            "sources": ["context/officina.md"]
        }

        mock_finish_run.return_value = {
            "id": 42,
            "status": "failed"
        }

        result = execute_run(42)

        self.assertEqual(
            result["status"],
            "failed"
        )

        mock_run_llm.assert_not_called()

        mock_finish_run.assert_called_once()

        args = mock_finish_run.call_args.args

        self.assertEqual(args[0], 42)
        self.assertEqual(args[1], "failed")
        self.assertIn(
            "contains a placeholder value",
            args[2]
        )

        mock_set_context.assert_called_once()

    @patch("services.executor.run_llm")
    @patch("services.executor.finish_run")
    @patch("services.executor.set_run_context")
    @patch("services.executor.build_run_context")
    @patch("services.executor.get_agent")
    @patch("services.executor.get_run")
    def test_real_placeholder_environment_blocks_llm(
        self,
        mock_get_run,
        mock_get_agent,
        mock_build_context,
        mock_set_context,
        mock_finish_run,
        mock_run_llm,
        mock_claim_run_execution
    ):
        mock_get_run.return_value = {
            "id": 43,
            "agent_id": 3,
            "task": "Integration-style placeholder key test"
        }

        mock_get_agent.return_value = {
            "id": 3,
            "name": "Explorer",
            "role": "Research Agent",
            "goal": "Inspect project state",
            "project": "Officina Lab"
        }

        mock_build_context.return_value = {
            "text": "context",
            "sources": ["context/officina.md"]
        }

        mock_finish_run.return_value = {
            "id": 43,
            "status": "failed"
        }

        with patch.dict(
            os.environ,
            {"OPENAI_API_KEY": " LA_TUA_CHIAVE "},
            clear=True
        ):
            result = execute_run(43)

        self.assertEqual(
            result["status"],
            "failed"
        )

        mock_run_llm.assert_not_called()

        args = mock_finish_run.call_args.args

        self.assertEqual(args[0], 43)
        self.assertEqual(args[1], "failed")
        self.assertIn(
            "contains a placeholder value",
            args[2]
        )

        mock_set_context.assert_called_once()



if __name__ == "__main__":
    unittest.main()
