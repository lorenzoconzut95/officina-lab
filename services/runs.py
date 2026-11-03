from repositories.runs import (
    list_runs as repo_list_runs,
    create_run as repo_create_run,
    get_run as repo_get_run,
    finish_run as repo_finish_run
)

from services.agents import update_agent_status
from services.errors import log_run_error


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
