import json

from repositories.agents import get_agent
from repositories.runs import (
    claim_run_execution,
    get_run,
    mark_execution_started,
    set_run_context
)
from services.runs import finish_run
from services.context import build_run_context
from services.llm_provider import (
    DEFAULT_MODEL,
    EmptyModelResponseError,
    ModelRequestTooLargeError,
    is_configured,
    get_api_key_status,
    run_llm
)


def build_local_output(agent, task):
    role = agent["role"].lower()

    if "research" in role or "explorer" in role:
        return (
            "LOCAL EXECUTOR RESULT\n\n"
            "Agent: " + agent["name"] + "\n"
            "Role: " + agent["role"] + "\n"
            "Task: " + task + "\n\n"
            "Research plan:\n"
            "1. Define the question precisely.\n"
            "2. Identify the evidence or sources needed.\n"
            "3. Collect the relevant facts.\n"
            "4. Compare conflicting signals.\n"
            "5. Produce a short synthesis with next steps."
        )

    if "builder" in role or "engineer" in role:
        return (
            "LOCAL EXECUTOR RESULT\n\n"
            "Agent: " + agent["name"] + "\n"
            "Role: " + agent["role"] + "\n"
            "Task: " + task + "\n\n"
            "Build plan:\n"
            "1. Define the smallest working output.\n"
            "2. Identify required inputs and dependencies.\n"
            "3. Implement the smallest testable version.\n"
            "4. Verify expected behavior.\n"
            "5. Record failures and the next iteration."
        )

    return (
        "LOCAL EXECUTOR RESULT\n\n"
        "Agent: " + agent["name"] + "\n"
        "Role: " + agent["role"] + "\n"
        "Task: " + task + "\n\n"
        "Execution plan:\n"
        "1. Understand the objective.\n"
        "2. Break it into small steps.\n"
        "3. Execute the first useful step.\n"
        "4. Check the result.\n"
        "5. Report the next action."
    )


def humanize_llm_error(error):
    if isinstance(error, ModelRequestTooLargeError):
        return str(error)

    if isinstance(error, EmptyModelResponseError):
        return "The model returned no final answer. Create a new run to retry."

    text = str(error)
    lower = text.lower()

    if "400" in lower or "bad request" in lower:
        return (
            "OpenAI request rejected (400). "
            "The model request was not accepted. "
            "Check model/input/tool configuration and retry."
        )

    if "401" in lower or "invalid_api_key" in lower:
        return (
            "OpenAI authentication failed (401). "
            "Check OPENAI_API_KEY in the server environment."
        )

    if "429" in lower or "rate limit" in lower:
        return (
            "OpenAI rate limit reached (429). "
            "Retry later or reduce request frequency."
        )

    if "timeout" in lower:
        return (
            "OpenAI request timed out. "
            "Retry the run."
        )

    return (
        "OpenAI execution failed. "
        "Open technical details only if you need to debug it."
    )


class RunAlreadyExecuted(Exception):
    pass


def execute_run(run_id):
    run = get_run(run_id)

    if run is None:
        return None

    agent = get_agent(
        run["agent_id"]
    )

    if agent is None:
        return None

    if not claim_run_execution(run_id):
        raise RunAlreadyExecuted(run_id)

    try:
        context_package = build_run_context(agent)
        context_package["run_id"] = run_id

        set_run_context(
            run_id,
            DEFAULT_MODEL if is_configured() else "local-executor",
            json.dumps(
                context_package["sources"]
            ),
            context_package["text"]
        )

        api_key_status = get_api_key_status()

        if not api_key_status["configured"]:
            if api_key_status["reason"] == "placeholder":
                return finish_run(
                    run_id,
                    "failed",
                    (
                        "OpenAI configuration error: OPENAI_API_KEY "
                        "contains a placeholder value. Set a real API key "
                        "in the server terminal before executing this run."
                    ),
                    0,
                    0,
                    0
                )

            output = build_local_output(
                agent,
                run["task"]
            )

            return finish_run(
                run_id,
                "completed",
                output,
                0,
                0,
                0
            )

        mark_execution_started(run_id)
        result = run_llm(
            agent,
            run["task"],
            context_package
        )

        final_sources = list(
            context_package["sources"]
        )

        for tool_name in result.get(
            "tools_used",
            []
        ):
            final_sources.append(
                "tool:" + tool_name
            )

        set_run_context(
            run_id,
            result["model"],
            json.dumps(
                final_sources
            ),
            context_package["text"]
        )

        return finish_run(
            run_id,
            "completed",
            result["output"],
            result["tokens_in"],
            result["tokens_out"],
            result["cost_usd"]
        )

    except Exception as error:
        return finish_run(
            run_id,
            "failed",
            (
                humanize_llm_error(error)
                + "\n\nTECHNICAL_DETAIL:\n"
                + str(error)
            ),
            0,
            0,
            0
        )
