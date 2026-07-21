import pytest

from app.templates import NotificationContext
from app.templates.task_assign_template import task_assign_template
from app.templates.task_create_template import task_create_template
from app.templates.task_unassign_template import task_unassign_template
from app.templates.task_update_template import task_update_template


@pytest.mark.parametrize(
    ("builder", "subject", "body_snippet"),
    [
        (
            task_create_template,
            "Task Build API created",
            "has created the task 'Build API'",
        ),
        (
            task_update_template,
            "Task Build API updated",
            "has made changes to the task 'Build API'",
        ),
        (
            task_assign_template,
            "Task Build API assigned",
            "has assigned you to the task 'Build API'",
        ),
        (
            task_unassign_template,
            "Task Build API unassigned",
            "has unassigned you from the task 'Build API'",
        ),
    ],
)
def test_task_notification_templates_format_content(builder, subject, body_snippet):
    ctx = NotificationContext(
        recipient_email="user@example.com",
        username="alice",
        actor_username="bob",
        task_title="Build API",
        project_name="Platform",
    )

    content = builder(ctx)

    assert content.recipient_email == ctx.recipient_email
    assert content.subject == subject
    assert body_snippet in content.body
    assert "Project Management System Team" in content.body
