from fastapi import APIRouter

from services.activity import list_activities


router = APIRouter(
    prefix="/api/activity",
    tags=["activity"]
)


@router.get("")
def read_activity(limit: int = 20):
    return list_activities(limit)
