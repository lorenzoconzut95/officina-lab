import os

from openai import OpenAI

from services.context import load_officina_context


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


def run_llm(agent, task):
    client = OpenAI()

    system_context = load_officina_context()

    instructions = (
        "You are an agent inside Officina Lab. "
        "Act according to the assigned role. "
        "Be concise, practical, and structured. "
        "Return a useful result and a clear next action.\n\n"
        "AGENT IDENTITY\n"
        "Agent name: " + agent["name"] + "\n"
        "Role: " + agent["role"] + "\n"
        "Project: " + agent["project"] + "\n\n"
        "OFFICINA SYSTEM CONTEXT\n"
        + system_context
    )

    response = client.responses.create(
        model=DEFAULT_MODEL,
        instructions=instructions,
        input=task
    )

    usage = response.usage

    tokens_in = (
        usage.input_tokens
        if usage is not None
        else 0
    )

    tokens_out = (
        usage.output_tokens
        if usage is not None
        else 0
    )

    cost_usd = (
        tokens_in / 1_000_000
        * INPUT_COST_PER_M
    ) + (
        tokens_out / 1_000_000
        * OUTPUT_COST_PER_M
    )

    return {
        "output": response.output_text,
        "tokens_in": tokens_in,
        "tokens_out": tokens_out,
        "cost_usd": cost_usd,
        "model": DEFAULT_MODEL
    }
