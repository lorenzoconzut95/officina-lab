from repositories.errors import (
    create_error as repo_create_error,
    list_errors as repo_list_errors
)


def log_run_error(
    run_id,
    agent_name,
    task,
    error_message
):
    return repo_create_error(
        run_id,
        agent_name,
        task,
        error_message
    )


def list_errors(limit=50):
    return repo_list_errors(limit)
