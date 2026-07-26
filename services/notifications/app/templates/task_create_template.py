from . import NotificationContent, TaskNotificationContext


def task_create_template(ctx: TaskNotificationContext) -> NotificationContent:

    return NotificationContent(
        recipient_email=ctx.recipient_email,
        subject=f"Task {ctx.task_title} created",
        body=(
            f"Hi {ctx.username},\n\n"
            f"{ctx.actor_username} has created the task '{ctx.task_title}'.\n\n"
            f"Please check your tasks.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )
