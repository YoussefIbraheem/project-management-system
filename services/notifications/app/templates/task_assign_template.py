from . import NotificationContent, NotificationContext


def task_assign_template(ctx: NotificationContext):
    return NotificationContent(
        recipient_email=ctx.recipient_email,
        subject=f"Task {ctx.task_title} assigned",
        body=(
            f"Hi {ctx.username},\n\n"
            f"{ctx.actor_username} has assigned you to the task '{ctx.task_title}'.\n\n"
            f"Please check your task updates.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )
