import json
import os

from openai import OpenAI

from services.tools import (
    TOOL_DEFINITIONS,
    execute_tool_json
)


DEFAULT_MODEL = os.getenv(
    "OFFICINA_OPENAI_MODEL",
    "gpt-6-luna"
)

INPUT_COST_PER_M = float(
    os.getenv(
        "OFFICINA_INPUT_COST_PER_M",
        "0.05"
    )
)

OUTPUT_COST_PER_M = float(
    os.getenv(
        "OFFICINA_OUTPUT_COST_PER_M",
        "0.25"
    )
)


def get_api_key_status():
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        return {
            "configured": False,
            "reason": "missing"
        }

    normalized = key.strip().lower()

    placeholder_markers = [
        "la_tua_chiave",
        "your_key",
        "incolla_qui",
        "paste_here",
        "sk-your",
        "sk-xxx"
    ]

    if any(marker in normalized for marker in placeholder_markers):
        return {
            "configured": False,
            "reason": "placeholder"
        }

    return {
        "configured": True,
        "reason": "ok"
    }


def is_configured():
    return get_api_key_status()["configured"]


def usage_numbers(response):
    usage = response.usage

    if usage is None:
        return 0, 0

    return (
        usage.input_tokens or 0,
        usage.output_tokens or 0
    )


def calculate_cost(tokens_in, tokens_out):
    return (
        tokens_in / 1_000_000
        * INPUT_COST_PER_M
    ) + (
        tokens_out / 1_000_000
        * OUTPUT_COST_PER_M
    )


def tools_after_calls(tools_used):
    if "inspect_project_state" not in tools_used:
        return TOOL_DEFINITIONS

    redundant = {
        "list_tasks",
        "list_memories",
        "list_recent_runs",
        "list_recent_errors"
    }

    return [
        tool for tool in TOOL_DEFINITIONS
        if tool["name"] not in redundant
    ]


def role_instructions(agent):
    identity = (
        agent["name"] + " " + agent["role"]
    ).lower()

    if (
        "builder" in identity
        or "software engineer" in identity
    ):
        return (
            "BUILDER PROPOSAL MODE: "
            "When proposing the next action, return exactly these labeled sections, "
            "each on its own line: ACTION_TYPE:, TARGET:, RATIONALE:, CHANGE:, "
            "TEST:, RISK:, APPROVAL_NEEDED:. "
            "ACTION_TYPE must be one of code_change, operational, no_action. "
            "APPROVAL_NEEDED must be yes or no. "
            "Verify current code before proposing a code change. "
            "Prefer the smallest safe intervention. "
            "Do not claim implementation unless it actually happened. "
        )

    if (
        "bug hunter" in identity
        or "debug" in identity
        or "qa" in identity
    ):
        return (
            "BUG HUNTER MODE: "
            "Prefer list_recent_errors when investigating failures. "
            "When asked whether a fix or regression test is implemented, "
            "use list_project_files and read_project_file to inspect evidence. "
            "Separate observed evidence from hypotheses. "
            "Do not claim a root cause unless evidence supports it. "
            "For each relevant failure, return exactly these labeled sections, "
            "each on its own line: SYMPTOM:, EVIDENCE:, ROOT_CAUSE:, "
            "CONFIDENCE:, MINIMAL_TEST:, SMALLEST_FIX:. "
            "Use concise plain text after each label. "
            "If evidence is insufficient, say that explicitly instead of guessing. "
            "Do not modify protected data without approval. "
        )

    return ""


def task_instructions(task):
    normalized = (task or "").strip().upper()

    if normalized.startswith(
        "VERIFY INCIDENT AFTER APPROVED BUILDER PROPOSAL"
    ):
        return (
            "VERIFICATION MODE OVERRIDE: "
            "For this task, ignore the normal Bug Hunter output labels. "
            "Return exactly these labeled sections, each on its own line: "
            "VERDICT:, EVIDENCE:, TEST_PERFORMED:, RESIDUAL_RISK:, NEXT_ACTION:. "
            "VERDICT must be exactly verified or not_verified. "
            "Use verified only when current evidence supports closure. "
            "Do not assume the approved proposal was implemented. "
        )

    return ""


def run_llm(agent, task, context_package):
    client = OpenAI()

    instructions = (
        "You are an agent inside Officina Lab. "
        "Act according to the assigned role. "
        "Be concise, practical, and structured. "
        "Use tools when current Officina data or an action is needed. "
        "For project-wide inspection, prefer inspect_project_state. "
        "If inspect_project_state is used, do not request list_tasks, "
        "list_memories, or list_recent_runs afterward because that data "
        "is already included. "
        "Write tools are protected by human approval. "
        "If a write tool returns approval_required, clearly tell the user "
        "that the action is only proposed and has NOT happened yet. "
        "Never claim you used a tool if you did not call it. "
        "Return a useful result and a clear next action. "
        + role_instructions(agent)
        + task_instructions(task)
        + "\n\n"
        + context_package["text"]
    )

    input_items = [
        {
            "role": "user",
            "content": task
        }
    ]

    response = client.responses.create(
        model=DEFAULT_MODEL,
        instructions=instructions,
        input=input_items,
        tools=TOOL_DEFINITIONS
    )

    total_input, total_output = usage_numbers(
        response
    )

    tools_used = []

    for _ in range(4):
        function_calls = [
            item
            for item in response.output
            if item.type == "function_call"
        ]

        if not function_calls:
            break

        input_items.extend(
            response.output
        )

        for call in function_calls:
            result = execute_tool_json(
                call.name,
                call.arguments,
                agent_name=agent["name"],
                run_id=context_package.get("run_id")
            )

            tools_used.append(
                call.name
            )

            input_items.append({
                "type": "function_call_output",
                "call_id": call.call_id,
                "output": json.dumps(
                    result,
                    ensure_ascii=False
                )
            })

        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=input_items,
            tools=tools_after_calls(
                tools_used
            )
        )

        tokens_in, tokens_out = usage_numbers(
            response
        )

        total_input += tokens_in
        total_output += tokens_out

    return {
        "output": response.output_text,
        "tokens_in": total_input,
        "tokens_out": total_output,
        "cost_usd": calculate_cost(
            total_input,
            total_output
        ),
        "model": DEFAULT_MODEL,
        "tools_used": sorted(
            set(tools_used)
        )
    }
