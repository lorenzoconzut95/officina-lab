from repositories.incidents import (
    list_incidents as repo_list_incidents,
    get_incident,
    get_incident_by_key,
    create_incident,
    refresh_incident,
    update_incident_status as repo_update_incident_status,
    link_analysis_run as repo_link_analysis_run
)
from services.errors import list_incidents as derive_incidents
from repositories.runs import get_run as repo_get_run


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

        if (
            existing["status"] == "resolved"
            and item["count"] > existing["occurrences"]
        ):
            repo_update_incident_status(
                existing["id"],
                "open"
            )

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



def link_analysis_run(incident_id, run_id):
    incident = get_incident(
        incident_id
    )

    if incident is None:
        return None

    return repo_link_analysis_run(
        incident_id,
        run_id
    )





STRUCTURED_ANALYSIS_LABELS = {
    "SYMPTOM": "symptom",
    "EVIDENCE": "evidence",
    "ROOT_CAUSE": "root_cause",
    "CONFIDENCE": "confidence",
    "MINIMAL_TEST": "minimal_test",
    "SMALLEST_FIX": "smallest_fix"
}


def parse_structured_analysis(output):
    result = {
        "symptom": None,
        "evidence": None,
        "root_cause": None,
        "confidence": None,
        "minimal_test": None,
        "smallest_fix": None
    }

    if not output:
        return result

    current_key = None
    buffer = []

    def flush():
        nonlocal buffer

        if current_key is not None:
            value = "\n".join(buffer).strip()
            result[current_key] = value or None

        buffer = []

    for raw_line in output.splitlines():
        line = raw_line.strip()
        matched = False

        for label, key in STRUCTURED_ANALYSIS_LABELS.items():
            prefix = label + ":"

            if line.upper().startswith(prefix):
                flush()
                current_key = key
                buffer = [line[len(prefix):].strip()]
                matched = True
                break

        if not matched and current_key is not None:
            buffer.append(raw_line)

    flush()
    return result


def get_incident_report(incident_id):
    incident = get_incident(
        incident_id
    )

    if incident is None:
        return None

    analysis_run = None

    if incident["analysis_run_id"]:
        analysis_run = repo_get_run(
            incident["analysis_run_id"]
        )

    structured_analysis = parse_structured_analysis(
        analysis_run["output"] if analysis_run else None
    )

    return {
        "incident_id": incident["id"],
        "incident_key": incident["incident_key"],
        "status": incident["status"],
        "severity": incident["severity"],
        "occurrences": incident["occurrences"],
        "latest_error": {
            "run_id": incident["latest_run_id"],
            "agent_name": incident["latest_agent_name"],
            "task": incident["latest_task"],
            "message": incident["latest_error_message"]
        },
        "structured_analysis": structured_analysis,
        "analysis": (
            {
                "run_id": analysis_run["id"],
                "status": analysis_run["status"],
                "agent_name": analysis_run["agent_name"],
                "model": analysis_run["model"],
                "output": analysis_run["output"],
                "started_at": analysis_run["started_at"],
                "ended_at": analysis_run["ended_at"],
                "tokens_in": analysis_run["tokens_in"],
                "tokens_out": analysis_run["tokens_out"],
                "cost_usd": analysis_run["cost_usd"]
            }
            if analysis_run
            else None
        ),
        "created_at": incident["created_at"],
        "updated_at": incident["updated_at"],
        "resolved_at": incident["resolved_at"]
    }
