from fastapi import APIRouter

from services.tool_calls import list_tool_calls


router = APIRouter(
    prefix="/api/tool-calls",
    tags=["tool-calls"]
)


@router.get("")
def read_tool_calls(limit: int = 50):
    return list_tool_calls(limit)
