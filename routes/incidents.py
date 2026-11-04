from fastapi import APIRouter, HTTPException

from services.incidents import (
    list_incidents,
    update_incident_status,
    link_analysis_run,
    get_incident_report,
    build_incident_case_study
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
