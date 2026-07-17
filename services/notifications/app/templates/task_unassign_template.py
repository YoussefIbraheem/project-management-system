from . import NotificationContext, NotificationContent


def task_unassign_template(ctx: NotificationContext):
    return NotificationContent(
        recipient_email=ctx.recipient_email,
        subject=f"Task {ctx.task_title} unassigned",
        body=(
            f"Hi {ctx.username},\n\n"
            f"{ctx.actor_username} has unassigned you from the task '{ctx.task_title}'.\n\n"
            f"Please check your task updates.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )
