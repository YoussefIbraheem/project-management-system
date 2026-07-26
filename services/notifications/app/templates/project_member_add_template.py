from . import NotificationContent, ProjectNotificationContext


def project_member_add_template(ctx: ProjectNotificationContext):
    return NotificationContent(
        recipient_email=ctx.recipient_email,
        subject=f"User {ctx.username} Added to Project {ctx.project_name}",
        body=(
            f"Hi {ctx.username},\n\n"
            f"{ctx.actor_username} has added you to the project '{ctx.project_name}'.\n\n"
            f"Please check your updates.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )