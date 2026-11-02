from repositories.tasks import (
    list_tasks as repo_list_tasks,
    get_task as repo_get_task,
    create_task as repo_create_task,
    update_task as repo_update_task,
    delete_task as repo_delete_task
)


def list_tasks():
    return repo_list_tasks()


def get_task(task_id):
    return repo_get_task(task_id)


def create_task(title, priority, project):
    return repo_create_task(
        title,
        priority,
        project
    )


def update_task(
    task_id,
    title=None,
    status=None,
    priority=None,
    project=None
):
    existing_task = repo_get_task(task_id)

    if existing_task is None:
        return None

    return repo_update_task(
        task_id,
        title if title is not None else existing_task["title"],
        status if status is not None else existing_task["status"],
        priority if priority is not None else existing_task["priority"],
        project if project is not None else existing_task["project"]
    )


def delete_task(task_id):
    return repo_delete_task(task_id)