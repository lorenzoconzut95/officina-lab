from repositories.approvals import (
    list_approvals as repo_list_approvals,
    create_approval as repo_create_approval,
    get_approval as repo_get_approval,
    resolve_approval as repo_resolve_approval
)

from services.tasks import (
    create_task,
    update_task
)


def list_approvals(status=None):
    return repo_list_approvals(
        status=status
    )


def create_approval(
    action,
    payload,
    agent_name,
    run_id
):
    return repo_create_approval(
        action,
        payload,
        agent_name,
        run_id
    )


def approve(approval_id):
    approval = repo_get_approval(
        approval_id
    )

    if approval is None:
        return None

    if approval["status"] != "pending":
        return approval

    if approval["action"] == "create_task":
        payload = approval["payload"]

        create_task(
            payload["title"],
            payload.get(
                "priority",
                "medium"
            ),
            payload.get(
                "project",
                "Officina Lab"
            )
        )

    if approval["action"] == "update_task_status":
        payload = approval["payload"]

        update_task(
            payload["task_id"],
            status=payload["status"]
        )

    return repo_resolve_approval(
        approval_id,
        "approved"
    )


def reject(approval_id):
    approval = repo_get_approval(
        approval_id
    )

    if approval is None:
        return None

    if approval["status"] != "pending":
        return approval

    return repo_resolve_approval(
        approval_id,
        "rejected"
    )
