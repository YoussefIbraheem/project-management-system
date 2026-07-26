from . import NotificationContent, TaskNotificationContext


def task_update_template(ctx: TaskNotificationContext):
    return NotificationContent(
        recipient_email=ctx.recipient_email,
        subject=f"Task {ctx.task_title} updated",
        body=(
            f"Hi {ctx.username},\n\n"
            f"{ctx.actor_username} has made changes to the task '{ctx.task_title}'.\n\n"
            f"Please check your task updates.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )
