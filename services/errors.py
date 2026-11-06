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



def _incident_key(error_message):
    text = (error_message or "").strip().lower()

    if text.startswith(("model request blocked locally before sending to openai.",
                        "model request is ")):
        return "model_request_too_large"

    if "invalid_api_key" in text or "api key" in text:
        return "openai_api_key"

    if "test error log" in text:
        return "test_error_log"

    first_line = text.split("\n", 1)[0]
    return first_line[:120] or "unknown_error"


def list_incidents(limit=50):
    errors = repo_list_errors(limit)

    grouped = {}

    for item in errors:
        key = _incident_key(
            item["error_message"]
        )

        if key not in grouped:
            grouped[key] = {
                "key": key,
                "count": 0,
                "latest_run_id": item["run_id"],
                "latest_agent_name": item["agent_name"],
                "latest_task": item["task"],
                "latest_error_message": item["error_message"],
                "latest_created_at": item["created_at"]
            }

        grouped[key]["count"] += 1

    incidents = list(
        grouped.values()
    )

    incidents.sort(
        key=lambda item: (
            item["count"],
            item["latest_created_at"]
        ),
        reverse=True
    )

    for item in incidents:
        if item["count"] >= 3:
            item["severity"] = "high"
        elif item["count"] == 2:
            item["severity"] = "medium"
        else:
            item["severity"] = "low"

    return incidents
