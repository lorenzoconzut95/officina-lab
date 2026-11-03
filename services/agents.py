from repositories.agents import (
    list_agents as repo_list_agents,
    create_agent as repo_create_agent,
    get_agent as repo_get_agent,
    update_agent_status as repo_update_agent_status
)


def list_agents():
    return repo_list_agents()


def create_agent(name, role, goal, project):
    return repo_create_agent(
        name,
        role,
        goal,
        project
    )


def update_agent_status(agent_id, status):
    existing_agent = repo_get_agent(agent_id)

    if existing_agent is None:
        return None

    return repo_update_agent_status(
        agent_id,
        status
    )
