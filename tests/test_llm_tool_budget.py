import unittest
from types import SimpleNamespace
from unittest.mock import patch

from services.llm_provider import EmptyModelResponseError, run_llm

AGENT = {"name": "Bug Hunter", "role": "debug"}


class LlmToolBudgetTests(unittest.TestCase):
    @patch("services.llm_provider.execute_tool_json", return_value={"ok": True})
    @patch("services.llm_provider.OpenAI")
    def test_final_request_disables_tools_at_budget_limit(self, client, execute_tool):
        create_response = client.return_value.responses.create
        tool_responses = [
            SimpleNamespace(
                output=[SimpleNamespace(
                    type="function_call", name="list_recent_errors",
                    call_id=f"call_{index}", arguments="{}"
                )],
                usage=None
            )
            for index in range(4)
        ]
        create_response.side_effect = tool_responses + [
            SimpleNamespace(output=[], usage=None, output_text="Final diagnosis")
        ]

        result = run_llm(AGENT, "Investigate", {"text": ""})

        self.assertEqual(result["output"], "Final diagnosis")
        self.assertEqual(execute_tool.call_count, 4)
        self.assertEqual(create_response.call_count, 5)
        self.assertEqual(create_response.call_args.kwargs["tool_choice"], "none")

    @patch("services.llm_provider.OpenAI")
    def test_whitespace_only_final_response_is_an_error(self, client):
        client.return_value.responses.create.return_value = SimpleNamespace(
            output=[], usage=None, output_text=" \n"
        )

        with self.assertRaises(EmptyModelResponseError):
            run_llm(AGENT, "Investigate", {"text": ""})
