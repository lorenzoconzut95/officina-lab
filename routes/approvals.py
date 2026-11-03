from fastapi import APIRouter, HTTPException

from services.approvals import (
    list_approvals,
    approve,
    reject
)


router = APIRouter(
    prefix="/api/approvals",
    tags=["approvals"]
)


@router.get("")
def read_approvals(status: str = None):
    return list_approvals(
        status=status
    )


@router.post("/{approval_id}/approve")
def approve_request(approval_id: int):
    approval = approve(
        approval_id
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    return approval


@router.post("/{approval_id}/reject")
def reject_request(approval_id: int):
    approval = reject(
        approval_id
    )

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval not found"
        )

    return approval
