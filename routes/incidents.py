from fastapi import APIRouter, HTTPException

from services.incidents import (
    list_incidents,
    update_incident_status
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
