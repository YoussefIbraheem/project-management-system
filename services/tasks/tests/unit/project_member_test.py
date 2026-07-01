"""Test cases for project member service functions."""

import pytest
from app.db.database import get_db_session
from app.models import Project, ProjectMember
from app.security.actor import Actor
from app.security.roles import MemberRole
from app.schemas.project_member_schema import ProjectMemberCreate
from app.services.project_service import (
    create_member,
    delete_member,
    get_member,
    get_members,
    update_member_role,
)
from utils.exceptions import NotFoundException


def _seed_project_members():
    """Seed database with test data."""
    with get_db_session() as db:
        project = Project(name="Test Project", description="Project for testing members")
        db.add(project)
        db.flush()

        owner = ProjectMember(
            project_id=project.id, user_id="1", role=MemberRole.OWNER.db_value
        )
        member1 = ProjectMember(
            project_id=project.id, user_id="2", role=MemberRole.MEMBER.db_value
        )
        member2 = ProjectMember(
            project_id=project.id, user_id="3", role=MemberRole.MEMBER.db_value
        )
        db.add_all([owner, member1, member2])
        db.commit()

        return {
            "project_id": project.id,
            "owner_id": "1",
            "member_1_id": "2",
            "member_2_id": "3",
        }


def test_get_members_returns_all_members():
    """Test get_members returns all members in a project."""
    seeded = _seed_project_members()

    members = get_members(seeded["project_id"])

    assert len(members) == 3
    assert any(m.user_id == "1" for m in members)
    assert any(m.user_id == "2" for m in members)
    assert any(m.user_id == "3" for m in members)


def test_get_members_empty_returns_empty_list():
    """Test get_members returns empty list when project has no members."""
    with get_db_session() as db:
        project = Project(name="Empty Project", description="No members")
        db.add(project)
        db.commit()
        project_id = project.id

    members = get_members(project_id) #type: ignore

    assert len(members) == 0


def test_get_members_project_not_found_raises_404():
    """Test get_members raises NotFoundException when project doesn't exist."""
    with pytest.raises(NotFoundException):
        get_members(999)


def test_get_member_returns_specific_member():
    """Test get_member returns a specific member by user ID."""
    seeded = _seed_project_members()

    member = get_member(seeded["project_id"], seeded["member_1_id"])

    assert member.user_id == "2"
    assert member.project_id == seeded["project_id"]
    assert member.role == MemberRole.MEMBER.db_value


def test_get_member_user_not_in_project_raises_404():
    """Test get_member raises NotFoundException when user is not in project."""
    seeded = _seed_project_members()

    with pytest.raises(NotFoundException):
        get_member(seeded["project_id"], "nonexistent-user")


def test_get_member_project_not_found_raises_404():
    """Test get_member raises NotFoundException when project doesn't exist."""
    with pytest.raises(NotFoundException):
        get_member(999, "some-user")


def test_create_member_adds_new_member():
    """Test create_member adds a new member to project."""
    seeded = _seed_project_members()
    actor = Actor(user_id="1")

    new_member = create_member(
        actor,
        seeded["project_id"],
        ProjectMemberCreate(user_id="4", role=MemberRole.MEMBER.db_value),
    )

    assert new_member.user_id == "4"
    assert new_member.project_id == seeded["project_id"]
    assert new_member.role == MemberRole.MEMBER.db_value

    members = get_members(seeded["project_id"])
    assert len(members) == 4


def test_create_member_project_not_found_raises_404():
    """Test create_member raises NotFoundException when project doesn't exist."""
    actor = Actor(user_id="1")

    with pytest.raises(NotFoundException):
        create_member(
            actor,
            999,
            ProjectMemberCreate(user_id="new-member", role=MemberRole.MEMBER.db_value),
        )


def test_update_member_role_changes_role():
    """Test update_member_role changes a member's role."""
    seeded = _seed_project_members()
    actor = Actor(user_id="1")

    updated_member = update_member_role(
        actor,
        seeded["project_id"],
        MemberRole.MANAGER.db_value,
        seeded["member_1_id"],
    )

    assert updated_member.role == MemberRole.MANAGER.db_value
    assert updated_member.user_id == seeded["member_1_id"]


def test_update_member_role_member_not_found_raises_404():
    """Test update_member_role raises NotFoundException when member doesn't exist."""
    seeded = _seed_project_members()
    actor = Actor(user_id="1")

    with pytest.raises(NotFoundException):
        update_member_role(
            actor,
            seeded["project_id"],
            MemberRole.MANAGER.db_value,
            "nonexistent-user",
        )


def test_update_member_role_project_not_found_raises_404():
    """Test update_member_role raises NotFoundException when project doesn't exist."""
    actor = Actor(user_id="1")

    with pytest.raises(NotFoundException):
        update_member_role(
            actor,
            999,
            MemberRole.MANAGER.db_value,
            "some-user",
        )


def test_delete_member_removes_member():
    """Test delete_member removes a member from project."""
    seeded = _seed_project_members()
    actor = Actor(user_id="1")

    result = delete_member(actor, seeded["project_id"], seeded["member_1_id"])

    assert result is True

    members = get_members(seeded["project_id"])
    assert len(members) == 2
    assert not any(m.user_id == "2" for m in members)


def test_delete_member_member_not_found_raises_404():
    """Test delete_member raises NotFoundException when member doesn't exist."""
    seeded = _seed_project_members()
    actor = Actor(user_id="1")

    with pytest.raises(NotFoundException):
        delete_member(actor, seeded["project_id"], "nonexistent-user")


def test_delete_member_project_not_found_raises_404():
    """Test delete_member raises NotFoundException when project doesn't exist."""
    actor = Actor(user_id="1")

    with pytest.raises(NotFoundException):
        delete_member(actor, 999, "some-user")
