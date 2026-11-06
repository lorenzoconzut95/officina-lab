from fastapi import APIRouter, HTTPException

from models import RunCreate, RunFinish
from repositories.model_requests import list_model_requests
from services.runs import (
    list_runs,
    create_run,
    finish_run,
    create_builder_handoff,
    prepare_retry,
    RunRetryNotAllowed
)

from services.executor import RunAlreadyExecuted, execute_run


router = APIRouter(
    prefix="/api/runs",
    tags=["runs"]
)


@router.get("")
def read_runs():
    return list_runs()


@router.get("/{run_id}/model-requests")
def read_run_model_requests(run_id: int):
    return list_model_requests(run_id)


@router.post("", status_code=201)
def create_new_run(run: RunCreate):
    return create_run(
        run.agent_id,
        run.task
    )


@router.post("/{run_id}/retry", status_code=201)
def prepare_run_retry(run_id: int):
    try:
        retry = prepare_retry(run_id)
    except RunRetryNotAllowed as error:
        raise HTTPException(
            status_code=409,
            detail="Only failed rate-limited runs can prepare a retry."
        ) from error
    if retry is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return retry


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
    try:
        run = execute_run(run_id)
    except RunAlreadyExecuted as error:
        raise HTTPException(
            status_code=409,
            detail="This run has already been started or finished. Create a new run to retry."
        ) from error

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
