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


def create_task(title):
    return repo_create_task(title)


def update_task(task_id, title=None, status=None):
    existing_task = repo_get_task(task_id)

    if existing_task is None:
        return None

    new_title = title if title is not None else existing_task["title"]
    new_status = status if status is not None else existing_task["status"]

    return repo_update_task(
        task_id,
        new_title,
        new_status
    )


def delete_task(task_id):
    return repo_delete_task(task_id)