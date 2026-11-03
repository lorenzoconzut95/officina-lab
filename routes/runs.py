from fastapi import APIRouter, HTTPException

from models import RunCreate, RunFinish
from services.runs import (
    list_runs,
    create_run,
    finish_run,
    create_builder_handoff
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



@router.post("/{run_id}/handoff-builder", status_code=201)
def handoff_to_builder(run_id: int):
    run = create_builder_handoff(run_id)

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Source run not found"
        )

    if run.get("error") == "builder_not_found":
        raise HTTPException(
            status_code=404,
            detail="Builder agent not found"
        )

    if run.get("error") == "handoff_requires_explorer":
        raise HTTPException(
            status_code=400,
            detail="Only Explorer runs can be handed off to Builder"
        )

    return run
