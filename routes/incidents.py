from fastapi import APIRouter, HTTPException

from services.incidents import (
    list_incidents,
    update_incident_status,
    link_analysis_run,
    get_incident_report,
    build_incident_case_study,
    create_builder_handoff_for_incident,
    create_incident_proposal_approval,
    create_incident_verification_run
)


router = APIRouter(
    prefix="/api/incidents",
    tags=["incidents"]
)


@router.get("")
def read_incidents(limit: int = 50):
    return list_incidents(limit)


@router.patch("/{incident_id}/status")
def change_incident_status(
    incident_id: int,
    status: str
):
    try:
        incident = update_incident_status(
            incident_id,
            status
        )
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid incident status"
        )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident



@router.patch("/{incident_id}/analysis-run")
def attach_analysis_run(
    incident_id: int,
    run_id: int
):
    incident = link_analysis_run(
        incident_id,
        run_id
    )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return incident



@router.get("/{incident_id}/report")
def read_incident_report(incident_id: int):
    report = get_incident_report(
        incident_id
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return report



@router.get("/{incident_id}/case-study")
def read_incident_case_study(incident_id: int):
    case_study = build_incident_case_study(
        incident_id
    )

    if case_study is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    return case_study



@router.post("/{incident_id}/handoff-builder", status_code=201)
def handoff_incident_to_builder(incident_id: int):
    run = create_builder_handoff_for_incident(
        incident_id
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found"
        )

    if run.get("error") == "analysis_not_completed":
        raise HTTPException(
            status_code=400,
            detail="Bug Hunter analysis must be completed before handoff"
        )

    if run.get("error") == "builder_not_found":
        raise HTTPException(
            status_code=404,
            detail="Builder agent not found"
        )

    return run



@router.post("/{incident_id}/proposal-approval", status_code=201)
def request_incident_proposal_approval(incident_id: int):
    approval = create_incident_proposal_approval(incident_id)

    if approval is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    if approval.get("error") == "builder_not_completed":
        raise HTTPException(
            status_code=400,
            detail="Builder run must be completed before approval"
        )

    if approval.get("error") == "proposal_not_structured":
        raise HTTPException(
            status_code=400,
            detail="Builder proposal is not structured"
        )

    return approval


@router.post("/{incident_id}/verify", status_code=201)
def verify_incident(incident_id: int):
    run = create_incident_verification_run(incident_id)

    if run is None:
        raise HTTPException(status_code=404, detail="Incident not found")

    if run.get("error") == "approval_required":
        raise HTTPException(
            status_code=400,
            detail="Approved Builder proposal required before verification"
        )

    if run.get("error") == "bug_hunter_not_found":
        raise HTTPException(
            status_code=404,
            detail="Bug Hunter agent not found"
        )

    return run
