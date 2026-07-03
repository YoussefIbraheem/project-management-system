from unittest.mock import MagicMock, Mock, patch

import pytest
from app.schemas.board_column_schema import (
    BoardColumnCreate,
    BoardColumnDetailsResponse,
)
from app.schemas.board_schema import BoardCreate, BoardResponse, BoardUpdate
from app.security.actor import Actor
from app.services.board_service import (
    create_board,
    create_column,
    delete_board,
    delete_column,
    get_board_by_id,
    get_board_by_project,
    get_column,
    get_columns,
    update_board,
)
from shared.exceptions import NotFoundException


@pytest.fixture
def mock_actor():
    actor = Mock(spec=Actor)
    actor.user_id = 1
    return actor


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_board():
    board = Mock()
    board.id = 1
    board.name = "Test Board"
    board.description = "Test Description"
    board.project_id = 1
    board.columns = []
    board.created_at = "2024-01-01T00:00:00"
    board.updated_at = None
    return board


@pytest.fixture
def mock_member():
    member = Mock()
    member.id = 1
    member.user_id = 1
    member.project_id = 1
    return member


@pytest.fixture
def board_create_data():
    return BoardCreate(
        name="New Board",
        description="New Board Description",
        project_id=1,
        default_columns=False,
    )


@pytest.fixture
def board_update_data():
    return BoardUpdate(name="Updated Board", description="Updated Description")


class TestGetBoardByProject:
    def test_get_board_by_project_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )
        mock_db_session.query.return_value.filter.return_value.limit.return_value.offset.return_value.all.return_value = [
            mock_board
        ]

        with patch(
            "app.services.board_service.get_member_or_404", return_value=mock_member
        ):
            with patch("app.services.board_service.can_view_boards"):
                with patch(
                    "app.services.board_service.BoardResponse.model_validate",
                    return_value=mock_board,
                ):
                    result = get_board_by_project(
                        mock_actor, project_id=1, limit=10, offset=0
                    )

        assert len(result) == 1
        assert result[0].name == "Test Board"

    def test_get_board_by_project_with_pagination(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )
        mock_db_session.query.return_value.filter.return_value.limit.return_value.offset.return_value.all.return_value = [
            mock_board
        ]

        with patch(
            "app.services.board_service.get_member_or_404", return_value=mock_member
        ):
            with patch("app.services.board_service.can_view_boards"):
                with patch(
                    "app.services.board_service.BoardResponse.model_validate",
                    return_value=mock_board,
                ):
                    result = get_board_by_project(
                        mock_actor, project_id=1, limit=5, offset=10
                    )

        assert mock_db_session.query.return_value.filter.return_value.limit.called
        assert mock_db_session.query.return_value.filter.return_value.limit.return_value.offset.called


class TestGetBoardById:
    def test_get_board_by_id_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_view_board"):
                    with patch(
                        "app.services.board_service.BoardResponse.model_validate",
                        return_value=mock_board,
                    ):
                        result = get_board_by_id(mock_actor, board_id=1)

        assert result.name == "Test Board"
        assert result.id == 1

    def test_get_board_by_id_not_found(self, mock_actor, mock_db_session, monkeypatch):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404",
            side_effect=NotFoundException("Board not found"),
        ):
            with pytest.raises(NotFoundException):
                get_board_by_id(mock_actor, board_id=999)


class TestCreateBoard:
    def test_create_board_success(
        self,
        mock_actor,
        mock_db_session,
        mock_board,
        mock_member,
        board_create_data,
        monkeypatch,
    ):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_project_or_404", return_value=Mock(id=1)
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_create_board"):
                    with patch(
                        "app.services.board_service.BoardResponse.model_validate",
                        return_value=mock_board,
                    ):
                        result = create_board(mock_actor, board_create_data)

        assert result.name == "Test Board"
        assert mock_db_session.add.called
        assert mock_db_session.flush.called

    def test_create_board_with_default_columns(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        board_data = BoardCreate(
            name="Board with Columns",
            description="Test",
            project_id=1,
            default_columns=True,
        )
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_project_or_404", return_value=Mock(id=1)
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_create_board"):
                    with patch(
                        "app.services.board_service.create_default_columns"
                    ) as mock_create_cols:
                        with patch(
                            "app.services.board_service.BoardResponse.model_validate",
                            return_value=mock_board,
                        ):
                            result = create_board(mock_actor, board_data)

        assert mock_create_cols.called


class TestUpdateBoard:
    def test_update_board_success(
        self,
        mock_actor,
        mock_db_session,
        mock_board,
        mock_member,
        board_update_data,
        monkeypatch,
    ):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_update_board"):
                    with patch(
                        "app.services.board_service.BoardResponse.model_validate",
                        return_value=mock_board,
                    ):
                        result = update_board(
                            mock_actor, board_id=1, board_data=board_update_data
                        )

        assert result.name == "Updated Board"
        assert mock_db_session.flush.called
        assert mock_db_session.refresh.called

    def test_update_board_partial(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        partial_update = BoardUpdate(name="New Name", description=None)
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_update_board"):
                    with patch(
                        "app.services.board_service.BoardResponse.model_validate",
                        return_value=mock_board,
                    ):
                        result = update_board(
                            mock_actor, board_id=1, board_data=partial_update
                        )

        assert mock_db_session.flush.called


class TestDeleteBoard:
    def test_delete_board_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_delete_board"):
                    result = delete_board(mock_actor, board_id=1)

        assert result is True
        assert mock_db_session.delete.called
        assert mock_db_session.flush.called

    def test_delete_board_not_found(self, mock_actor, mock_db_session, monkeypatch):
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404",
            side_effect=NotFoundException("Board not found"),
        ):
            with pytest.raises(NotFoundException):
                delete_board(mock_actor, board_id=999)


class TestGetColumns:
    def test_get_columns_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        mock_column = Mock()
        mock_column.id = 1
        mock_column.label = "To Do"
        mock_column.board_id = 1

        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )
        mock_db_session.query.return_value.filter.return_value.all.return_value = [
            mock_column
        ]

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_view_board_columns"):
                    with patch(
                        "app.services.board_service.BoardColumnDetailsResponse.model_validate",
                        return_value=mock_column,
                    ):
                        result = get_columns(mock_actor, board_id=1)

        assert len(result) == 1
        assert result[0].label == "To Do"


class TestGetColumn:
    def test_get_column_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        mock_column = Mock()
        mock_column.id = 1
        mock_column.label = "In Progress"

        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_view_board_column"):
                    with patch(
                        "app.services.board_service.get_column_or_404",
                        return_value=mock_column,
                    ):
                        with patch(
                            "app.services.board_service.BoardColumnDetailsResponse.model_validate",
                            return_value=mock_column,
                        ):
                            result = get_column(mock_actor, board_id=1, column_id=1)

        assert result.label == "In Progress"


class TestCreateColumn:
    def test_create_column_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        mock_column = Mock()
        mock_column.id = 1
        mock_column.label = "Done"
        mock_column.board_id = 1
        mock_column.status_group = "done"

        column_data = BoardColumnCreate(label="Done", status_group="done")
        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_member_or_404", return_value=mock_member
            ):
                with patch("app.services.board_service.can_create_board_column"):
                    with patch(
                        "app.services.board_service.ensure_column_not_duplicate"
                    ):
                        with patch(
                            "app.services.board_service.BoardColumnDetailsResponse.model_validate",
                            return_value=mock_column,
                        ):
                            result = create_column(
                                mock_actor, board_id=1, board_column_data=column_data
                            )

        assert result.label == "Done"
        assert mock_db_session.add.called
        assert mock_db_session.commit.called


class TestDeleteColumn:
    def test_delete_column_success(
        self, mock_actor, mock_db_session, mock_board, mock_member, monkeypatch
    ):
        mock_column = Mock()
        mock_column.id = 1
        mock_column.label = "Archive"

        monkeypatch.setattr(
            "app.services.board_service.get_db_session",
            lambda: MagicMock(
                __enter__=lambda s: mock_db_session, __exit__=lambda s, *args: None
            ),
        )

        with patch(
            "app.services.board_service.get_board_or_404", return_value=mock_board
        ):
            with patch(
                "app.services.board_service.get_column_or_404", return_value=mock_column
            ):
                with patch(
                    "app.services.board_service.get_member_or_404",
                    return_value=mock_member,
                ):
                    with patch("app.services.board_service.can_create_board_column"):
                        result = delete_column(mock_actor, board_id=1, column_id=1)

        assert result is True
        assert mock_db_session.delete.called
        assert mock_db_session.commit.called
