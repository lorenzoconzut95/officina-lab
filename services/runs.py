import json

from repositories.runs import (
    list_runs as repo_list_runs,
    create_run as repo_create_run,
    get_run as repo_get_run,
    finish_run as repo_finish_run
)

from services.agents import update_agent_status, list_agents
from services.errors import log_run_error
from services.project_state import build_project_state


def list_runs():
    return repo_list_runs()


def create_run(agent_id, task):
    run = repo_create_run(
        agent_id,
        task
    )

    update_agent_status(
        agent_id,
        "working"
    )

    return run


def finish_run(
    run_id,
    status,
    output,
    tokens_in,
    tokens_out,
    cost_usd
):
    run = repo_get_run(run_id)

    if run is None:
        return None

    finished = repo_finish_run(
        run_id,
        status,
        output,
        tokens_in,
        tokens_out,
        cost_usd
    )

    update_agent_status(
        run["agent_id"],
        "idle"
    )

    if status == "failed":
        log_run_error(
            run_id,
            run["agent_name"],
            run["task"],
            output
        )

    return finished



def create_builder_handoff(run_id):
    source_run = repo_get_run(run_id)

    if source_run is None:
        return None

    builders = [
        agent for agent in list_agents()
        if agent["name"].lower() == "builder"
    ]

    if not builders:
        return {
            "error": "builder_not_found"
        }

    builder = builders[0]

    fresh_state = build_project_state(
        project=builder["project"],
        limit=6
    )

    handoff_task = (
        "HANDOFF FROM RUN #" + str(source_run["id"]) + "\n\n"
        "Original task:\n" + source_run["task"] + "\n\n"
        "Explorer output:\n" + (source_run["output"] or "") + "\n\n"
        "CURRENT PROJECT STATE SNAPSHOT (fresh at handoff time):\n"
        + json.dumps(
            fresh_state,
            ensure_ascii=False,
            indent=2
        )
        + "\n\n"
        "Builder instruction:\n"
        "Use the fresh project snapshot as the source of truth. "
        "Do not propose work that the snapshot shows as already implemented. "
        "Choose the next smallest useful technical intervention. "
        "Do not modify protected data without approval."
    )

    return create_run(
        builder["id"],
        handoff_task
    )
