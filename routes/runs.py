from fastapi import APIRouter, HTTPException

from models import RunCreate, RunFinish
from services.runs import (
    list_runs,
    create_run,
    finish_run
)

from services.executor import execute_run


router = APIRouter(
    prefix="/api/runs",
    tags=["runs"]
)


@router.get("")
def read_runs():
    return list_runs()


@router.post("", status_code=201)
def create_new_run(run: RunCreate):
    return create_run(
        run.agent_id,
        run.task
    )


@router.patch("/{run_id}/finish")
def finish_existing_run(
    run_id: int,
    update: RunFinish
):
    run = finish_run(
        run_id,
        update.status,
        update.output,
        update.tokens_in,
        update.tokens_out,
        update.cost_usd
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run not found"
        )

    return run


@router.post("/{run_id}/execute")
def execute_existing_run(run_id: int):
    run = execute_run(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Run or agent not found"
        )

    return run
