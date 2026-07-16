from . import NotificationContent


def task_create_template(
    username: str,
    task_title: str,
    actor_username: str,
):

    return NotificationContent(
        title=f"Task {task_title} created",
        body=f"{actor_username} has created the task '{task_title}'. Please check your tasks",
        email_subject=f"Task {task_title} created",
        email_body=(
            f"Hi {username},\n\n"
            f"{actor_username} has created the task '{task_title}'.\n\n"
            f"Please check your tasks.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )
