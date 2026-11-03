from fastapi import APIRouter

from services.errors import list_errors


router = APIRouter(
    prefix="/api/errors",
    tags=["errors"]
)


@router.get("")
def read_errors(limit: int = 50):
    return list_errors(limit)
