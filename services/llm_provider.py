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


def is_configured():
    return bool(
        os.getenv("OPENAI_API_KEY")
    )


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


def run_llm(agent, task, context_package):
    client = OpenAI()

    instructions = (
        "You are an agent inside Officina Lab. "
        "Act according to the assigned role. "
        "Be concise, practical, and structured. "
        "Use read-only tools when current Officina data is needed. "
        "Never claim you used a tool if you did not call it. "
        "Return a useful result and a clear next action.\n\n"
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
                call.arguments
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
            tools=TOOL_DEFINITIONS
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
