from fastapi import APIRouter, HTTPException

from models import AgentCreate, AgentStatusUpdate
from services.agents import (
    list_agents,
    create_agent,
    update_agent_status
)


router = APIRouter(
    prefix="/api/agents",
    tags=["agents"]
)


@router.get("")
def read_agents():
    return list_agents()


@router.post("", status_code=201)
def create_new_agent(agent: AgentCreate):
    return create_agent(
        agent.name,
        agent.role,
        agent.goal,
        agent.project
    )


@router.patch("/{agent_id}/status")
def update_status(
    agent_id: int,
    update: AgentStatusUpdate
):
    agent = update_agent_status(
        agent_id,
        update.status
    )

    if agent is None:
        raise HTTPException(
            status_code=404,
            detail="Agent not found"
        )

    return agent
