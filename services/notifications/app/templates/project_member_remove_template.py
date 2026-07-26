from . import NotificationContent, ProjectNotificationContext


def project_member_remove_template(ctx: ProjectNotificationContext):
    return NotificationContent(
        recipient_email=ctx.recipient_email,
        subject=f"User {ctx.username} Removed from Project {ctx.project_name}",
        body=(
            f"Hi {ctx.username},\n\n"
            f"{ctx.actor_username} has removed you from the project '{ctx.project_name}'.\n\n"
            f"Please check your updates.\n\n"
            "Best regards,\n"
            "Project Management System Team"
        ),
    )