from repositories.tool_calls import (
    log_tool_call as repo_log_tool_call,
    list_tool_calls as repo_list_tool_calls
)


def log_tool_call(
    run_id,
    agent_name,
    tool_name,
    arguments,
    result
):
    return repo_log_tool_call(
        run_id,
        agent_name,
        tool_name,
        arguments,
        result
    )


def list_tool_calls(limit=50):
    return repo_list_tool_calls(limit)
