from repositories.incidents import (
    list_incidents as repo_list_incidents,
    get_incident,
    get_incident_by_key,
    create_incident,
    refresh_incident,
    update_incident_status as repo_update_incident_status
)
from services.errors import list_incidents as derive_incidents


ALLOWED_STATUSES = {
    "open",
    "investigating",
    "resolved"
}


def sync_incidents(limit=50):
    derived = derive_incidents(limit)

    for item in derived:
        existing = get_incident_by_key(
            item["key"]
        )

        if existing is None:
            create_incident(
                item["key"],
                item["severity"],
                item["count"],
                item["latest_run_id"],
                item["latest_agent_name"],
                item["latest_task"],
                item["latest_error_message"]
            )
            continue

        refresh_incident(
            existing["id"],
            item["severity"],
            item["count"],
            item["latest_run_id"],
            item["latest_agent_name"],
            item["latest_task"],
            item["latest_error_message"]
        )

    return repo_list_incidents()


def list_incidents(limit=50):
    sync_incidents(limit)
    return repo_list_incidents()


def update_incident_status(incident_id, status):
    if status not in ALLOWED_STATUSES:
        raise ValueError("Invalid incident status")

    incident = get_incident(
        incident_id
    )

    if incident is None:
        return None

    return repo_update_incident_status(
        incident_id,
        status
    )
