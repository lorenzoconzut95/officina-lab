from fastapi import APIRouter

from services.errors import list_errors, list_incidents


router = APIRouter(
    prefix="/api/errors",
    tags=["errors"]
)


@router.get("")
def read_errors(limit: int = 50):
    return list_errors(limit)



@router.get("/incidents")
def read_incidents(limit: int = 50):
    return list_incidents(limit)
