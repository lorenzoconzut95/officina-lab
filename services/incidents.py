from repositories.incidents import (
    list_incidents as repo_list_incidents,
    get_incident,
    get_incident_by_key,
    create_incident,
    refresh_incident,
    update_incident_status as repo_update_incident_status,
    link_analysis_run as repo_link_analysis_run,
    link_builder_run as repo_link_builder_run,
    link_approval as repo_link_approval,
    link_verification_run as repo_link_verification_run
)
from services.errors import list_incidents as derive_incidents
from repositories.runs import get_run as repo_get_run
from services.agents import list_agents
from services.project_state import build_project_state
from services.runs import create_run
from services.approvals import create_approval
from repositories.approvals import get_approval as repo_get_approval


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




BUILDER_PROPOSAL_LABELS = {
    "ACTION_TYPE": "action_type",
    "TARGET": "target",
    "RATIONALE": "rationale",
    "CHANGE": "change",
    "TEST": "test",
    "RISK": "risk",
    "APPROVAL_NEEDED": "approval_needed"
}


def parse_builder_proposal(output):
    result = {
        "action_type": None,
        "target": None,
        "rationale": None,
        "change": None,
        "test": None,
        "risk": None,
        "approval_needed": None
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

        for label, key in BUILDER_PROPOSAL_LABELS.items():
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
    builder_run = None
    approval = None
    verification_run = None

    if incident["analysis_run_id"]:
        analysis_run = repo_get_run(
            incident["analysis_run_id"]
        )

    if incident["builder_run_id"]:
        builder_run = repo_get_run(
            incident["builder_run_id"]
        )

    if incident["approval_id"]:
        approval = repo_get_approval(incident["approval_id"])

    if incident["verification_run_id"]:
        verification_run = repo_get_run(incident["verification_run_id"])

    structured_analysis = parse_structured_analysis(
        analysis_run["output"] if analysis_run else None
    )

    builder_proposal = parse_builder_proposal(
        builder_run["output"] if builder_run else None
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
        "builder_proposal": builder_proposal,
        "approval": approval,
        "verification_run": (
            {
                "run_id": verification_run["id"],
                "status": verification_run["status"],
                "agent_name": verification_run["agent_name"],
                "model": verification_run["model"],
                "output": verification_run["output"],
                "started_at": verification_run["started_at"],
                "ended_at": verification_run["ended_at"]
            }
            if verification_run
            else None
        ),
        "builder_run": (
            {
                "run_id": builder_run["id"],
                "status": builder_run["status"],
                "agent_name": builder_run["agent_name"],
                "model": builder_run["model"],
                "output": builder_run["output"],
                "started_at": builder_run["started_at"],
                "ended_at": builder_run["ended_at"]
            }
            if builder_run
            else None
        ),
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



def build_incident_case_study(incident_id):
    report = get_incident_report(
        incident_id
    )

    if report is None:
        return None

    structured = report["structured_analysis"]
    analysis = report["analysis"]

    def value(name):
        return structured.get(name) or "Not available"

    lines = [
        "# Incident Case Study — " + report["incident_key"],
        "",
        "**Incident ID:** " + str(report["incident_id"]),
        "**Status:** " + report["status"],
        "**Severity:** " + report["severity"],
        "**Occurrences:** " + str(report["occurrences"]),
        "",
        "## Problem",
        "",
        value("symptom"),
        "",
        "## Evidence",
        "",
        value("evidence"),
        "",
        "## Root cause",
        "",
        value("root_cause"),
        "",
        "## Confidence",
        "",
        value("confidence"),
        "",
        "## Minimal test",
        "",
        value("minimal_test"),
        "",
        "## Smallest fix",
        "",
        value("smallest_fix"),
        "",
        "## Latest error",
        "",
        "Run #" + str(report["latest_error"]["run_id"])
        + " · Agent: " + str(report["latest_error"]["agent_name"]),
        "",
        report["latest_error"]["message"],
        "",
        "## Bug Hunter analysis",
        ""
    ]

    if analysis:
        lines.extend([
            "Run #" + str(analysis["run_id"])
            + " · " + str(analysis["status"]),
            "",
            "Model: " + str(analysis["model"] or "n/a"),
            "",
            analysis["output"] or "No output available."
        ])
    else:
        lines.append("No Bug Hunter analysis linked.")

    lines.extend([
        "",
        "## Lifecycle",
        "",
        "Created: " + str(report["created_at"]),
        "Updated: " + str(report["updated_at"]),
        "Resolved: " + str(report["resolved_at"] or "not resolved"),
        ""
    ])

    return {
        "filename": (
            "incident-"
            + str(report["incident_id"])
            + "-"
            + report["incident_key"]
            + ".md"
        ),
        "markdown": "\n".join(lines)
    }



def create_builder_handoff_for_incident(incident_id):
    report = get_incident_report(
        incident_id
    )

    if report is None:
        return None

    analysis = report["analysis"]

    if (
        analysis is None
        or analysis["status"] != "completed"
    ):
        return {
            "error": "analysis_not_completed"
        }

    builders = [
        agent
        for agent in list_agents()
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

    structured = report["structured_analysis"]

    handoff_task = (
        "INCIDENT HANDOFF TO BUILDER\n\n"
        "Incident #" + str(report["incident_id"]) + "\n"
        "Key: " + report["incident_key"] + "\n"
        "Status: " + report["status"] + "\n"
        "Severity: " + report["severity"] + "\n"
        "Occurrences: " + str(report["occurrences"]) + "\n\n"
        "Latest error:\n"
        + report["latest_error"]["message"]
        + "\n\n"
        "Structured Bug Hunter analysis:\n"
        "SYMPTOM: " + str(structured["symptom"] or "n/a") + "\n"
        "EVIDENCE: " + str(structured["evidence"] or "n/a") + "\n"
        "ROOT_CAUSE: " + str(structured["root_cause"] or "n/a") + "\n"
        "CONFIDENCE: " + str(structured["confidence"] or "n/a") + "\n"
        "MINIMAL_TEST: " + str(structured["minimal_test"] or "n/a") + "\n"
        "SMALLEST_FIX: " + str(structured["smallest_fix"] or "n/a") + "\n\n"
        "Full Bug Hunter output:\n"
        + str(analysis["output"] or "")
        + "\n\n"
        "CURRENT PROJECT STATE SNAPSHOT:\n"
        + __import__("json").dumps(
            fresh_state,
            ensure_ascii=False,
            indent=2
        )
        + "\n\n"
        "Builder instruction:\n"
        "Propose the smallest safe technical change that addresses the incident. "
        "Verify current code before proposing anything. "
        "Do not claim a fix is implemented unless evidence supports it. "
        "Do not modify protected data without approval."
    )

    builder_run = create_run(
        builder["id"],
        handoff_task
    )

    repo_link_builder_run(
        incident_id,
        builder_run["id"]
    )

    return builder_run



def create_incident_proposal_approval(incident_id):
    report = get_incident_report(incident_id)

    if report is None:
        return None

    builder_run = report["builder_run"]
    proposal = report["builder_proposal"]

    if builder_run is None or builder_run["status"] != "completed":
        return {"error": "builder_not_completed"}

    if not proposal.get("action_type"):
        return {"error": "proposal_not_structured"}

    if report["approval"] is not None:
        return report["approval"]

    approval = create_approval(
        "incident_builder_proposal",
        {
            "incident_id": report["incident_id"],
            "incident_key": report["incident_key"],
            "action_type": proposal.get("action_type"),
            "target": proposal.get("target"),
            "rationale": proposal.get("rationale"),
            "change": proposal.get("change"),
            "test": proposal.get("test"),
            "risk": proposal.get("risk"),
            "approval_needed": proposal.get("approval_needed")
        },
        builder_run["agent_name"],
        builder_run["run_id"]
    )

    repo_link_approval(
        incident_id,
        approval["id"]
    )

    return approval


def create_incident_verification_run(incident_id):
    report = get_incident_report(incident_id)

    if report is None:
        return None

    approval = report["approval"]

    if approval is None or approval["status"] != "approved":
        return {"error": "approval_required"}

    bug_hunters = [
        agent
        for agent in list_agents()
        if (
            "bug hunter" in agent["name"].lower()
            or "debug" in agent["role"].lower()
        )
    ]

    if not bug_hunters:
        return {"error": "bug_hunter_not_found"}

    bug_hunter = bug_hunters[0]
    proposal = report["builder_proposal"]

    task = (
        "VERIFY INCIDENT AFTER APPROVED BUILDER PROPOSAL\n\n"
        "Incident #" + str(report["incident_id"]) + "\n"
        "Key: " + report["incident_key"] + "\n"
        "Current status: " + report["status"] + "\n\n"
        "Approved proposal:\n"
        "ACTION_TYPE: " + str(proposal.get("action_type") or "n/a") + "\n"
        "TARGET: " + str(proposal.get("target") or "n/a") + "\n"
        "CHANGE: " + str(proposal.get("change") or "n/a") + "\n"
        "TEST: " + str(proposal.get("test") or "n/a") + "\n"
        "RISK: " + str(proposal.get("risk") or "n/a") + "\n\n"
        "Verification instruction:\n"
        "Inspect current Officina evidence and determine whether the approved "
        "proposal has actually been satisfied. Do not assume implementation. "
        "Use project files, recent errors, runs, and state when useful. "
        "Return exactly: SYMPTOM:, EVIDENCE:, ROOT_CAUSE:, CONFIDENCE:, "
        "MINIMAL_TEST:, SMALLEST_FIX:. In SMALLEST_FIX state either VERIFIED "
        "if evidence supports closure, or the smallest remaining action."
    )

    run = create_run(
        bug_hunter["id"],
        task
    )

    repo_link_verification_run(
        incident_id,
        run["id"]
    )

    return run
