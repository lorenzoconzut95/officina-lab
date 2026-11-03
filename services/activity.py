from repositories.activity import (
    create_activity as repo_create_activity,
    list_activities as repo_list_activities
)


def log_activity(action, task_title, project):
    repo_create_activity(
        action,
        task_title,
        project
    )


def list_activities(limit=20):
    return repo_list_activities(limit)
