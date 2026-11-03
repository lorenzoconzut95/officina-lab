from repositories.approvals import (
    list_approvals as repo_list_approvals,
    create_approval as repo_create_approval,
    get_approval as repo_get_approval,
    resolve_approval as repo_resolve_approval
)

from services.tasks import (
    create_task,
    get_task,
    update_task
)

from services.memories import create_memory


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


def remember_approved_action(
    approval,
    project,
    description
):
    create_memory(
        (
            "Approved agent action: "
            + description
            + ". Proposed by "
            + approval["agent_name"]
            + (
                " in run #"
                + str(approval["run_id"])
                if approval["run_id"]
                else ""
            )
            + "."
        ),
        project,
        "decision"
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

        task = create_task(
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

        remember_approved_action(
            approval,
            task["project"],
            (
                "created task #"
                + str(task["id"])
                + " \""
                + task["title"]
                + "\" with priority "
                + task["priority"]
            )
        )

    if approval["action"] == "update_task_status":
        payload = approval["payload"]

        existing_task = get_task(
            payload["task_id"]
        )

        if existing_task is not None:
            updated_task = update_task(
                payload["task_id"],
                status=payload["status"]
            )

            remember_approved_action(
                approval,
                updated_task["project"],
                (
                    "changed task #"
                    + str(updated_task["id"])
                    + " \""
                    + updated_task["title"]
                    + "\" status from "
                    + existing_task["status"]
                    + " to "
                    + updated_task["status"]
                )
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
