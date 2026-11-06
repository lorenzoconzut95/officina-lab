import json
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from openai.types.responses import ResponseFunctionToolCall

from services.llm_provider import (
    EmptyModelResponseError,
    MAX_REQUEST_BYTES,
    MAX_TOOL_OUTPUT_BYTES,
    ModelRequestTooLargeError,
    TOTAL_TOOL_OUTPUT_BYTES,
    run_llm,
    serialize_tool_output,
)

AGENT = {"name": "Bug Hunter", "role": "debug"}


class LlmToolBudgetTests(unittest.TestCase):
    @patch("services.llm_provider.OpenAI")
    def test_oversized_initial_request_is_blocked_before_sending(self, client):
        with self.assertRaisesRegex(
            ModelRequestTooLargeError,
            r"blocked locally before sending to OpenAI.*524,288 bytes"
        ):
            run_llm(AGENT, "🌊" * (MAX_REQUEST_BYTES // 4), {"text": ""})

        client.return_value.responses.create.assert_not_called()

    @patch("services.llm_provider.execute_tool_json")
    @patch("services.llm_provider.OpenAI")
    def test_oversized_followup_is_blocked_after_tool_execution(self, client, execute_tool):
        create_response = client.return_value.responses.create
        create_response.return_value = SimpleNamespace(output=[ResponseFunctionToolCall(
            type="function_call", name="list_recent_errors", call_id="call_1", arguments="{}"
        )], usage=None)
        execute_tool.return_value = {"text": "x" * (100 * 1024)}

        with self.assertRaisesRegex(ModelRequestTooLargeError, "524,288 bytes"):
            run_llm(AGENT, "x" * (430 * 1024), {"text": ""})

        execute_tool.assert_called_once()
        create_response.assert_called_once()

    def test_small_tool_output_is_preserved(self):
        result = {"items": ["diagnosi già disponibile"]}
        self.assertEqual(json.loads(serialize_tool_output(result)), result)

    @patch("services.llm_provider.execute_tool_json")
    @patch("services.llm_provider.OpenAI")
    def test_tool_output_budget_is_shared_across_rounds(self, client, execute_tool):
        execute_tool.return_value = {"text": "x" * (100 * 1024)}
        create_response = client.return_value.responses.create
        create_response.side_effect = [
            SimpleNamespace(output=[
                ResponseFunctionToolCall(
                    type="function_call", name="list_recent_errors",
                    call_id=f"call_{round_index}_{index}", arguments="{}"
                )
                for index in range(2)
            ], usage=None)
            for round_index in range(2)
        ] + [SimpleNamespace(output=[], usage=None, output_text="Final diagnosis")]

        run_llm(AGENT, "Investigate", {"text": ""})

        final_request = create_response.call_args.kwargs
        outputs = [item["output"] for item in final_request["input"]
                   if isinstance(item, dict) and item.get("type") == "function_call_output"]
        self.assertEqual(len(outputs), 4)
        self.assertEqual(json.loads(outputs[0]), execute_tool.return_value)
        self.assertTrue(json.loads(outputs[-1])["truncated"])
        self.assertLessEqual(sum(len(output.encode("utf-8")) for output in outputs),
                             TOTAL_TOOL_OUTPUT_BYTES)
        self.assertEqual(final_request["tool_choice"], "none")

    @patch("services.llm_provider.execute_tool_json")
    @patch("services.llm_provider.OpenAI")
    def test_large_tool_output_is_bounded_before_sending(self, client, execute_tool):
        result = {"text": '🌊"\\\n' * MAX_TOOL_OUTPUT_BYTES}
        execute_tool.return_value = result
        create_response = client.return_value.responses.create
        create_response.side_effect = [
            SimpleNamespace(output=[ResponseFunctionToolCall(
                type="function_call", name="list_recent_errors",
                call_id="call_1", arguments="{}"
            )], usage=None),
            SimpleNamespace(output=[], usage=None, output_text="Final diagnosis"),
        ]

        run_llm(AGENT, "Investigate", {"text": ""})

        output = create_response.call_args.kwargs["input"][-1]["output"]
        self.assertLessEqual(len(output.encode("utf-8")), MAX_TOOL_OUTPUT_BYTES)
        envelope = json.loads(output)
        original = json.dumps(result, ensure_ascii=False)
        self.assertTrue(envelope["truncated"])
        self.assertEqual(envelope["original_bytes"], len(original.encode("utf-8")))
        self.assertTrue(envelope["preview"])
        self.assertTrue(original.startswith(envelope["preview"]))

    @patch("services.llm_provider.execute_tool_json", return_value={"ok": True})
    @patch("services.llm_provider.OpenAI")
    def test_final_request_disables_tools_at_budget_limit(self, client, execute_tool):
        create_response = client.return_value.responses.create
        tool_responses = [
            SimpleNamespace(
                output=[ResponseFunctionToolCall(
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
