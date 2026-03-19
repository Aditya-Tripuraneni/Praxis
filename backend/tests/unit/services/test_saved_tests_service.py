"""Unit tests for SavedTestsService.

All Supabase calls are mocked -- no external connections needed.
Tests cover save, list, get, rename, delete, and limit enforcement.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.services.saved_tests import SavedTestLimitError, SavedTestsService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

USER_ID = "test-user-id-123"
TEST_ID = "saved-test-uuid-456"


def _mock_supabase_response(data):
    """Create a mock Supabase .execute() response."""
    resp = MagicMock()
    resp.data = data
    return resp


def _make_select_eq_chain(data):
    """Build mock chain: table().select().eq().execute() -> data."""
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_eq.execute.return_value = _mock_supabase_response(data)
    mock_select.eq.return_value = mock_eq
    mock_table.select.return_value = mock_select
    return mock_table


def _make_select_eq_order_chain(data):
    """Build mock chain: table().select().eq().order().execute() -> data."""
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_order = MagicMock()
    mock_order.execute.return_value = _mock_supabase_response(data)
    mock_eq.order.return_value = mock_order
    mock_select.eq.return_value = mock_eq
    mock_table.select.return_value = mock_select
    return mock_table


def _make_select_eq_eq_chain(data):
    """Build mock chain: table().select().eq().eq().execute() -> data."""
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_eq1 = MagicMock()
    mock_eq2 = MagicMock()
    mock_eq2.execute.return_value = _mock_supabase_response(data)
    mock_eq1.eq.return_value = mock_eq2
    mock_select.eq.return_value = mock_eq1
    mock_table.select.return_value = mock_select
    return mock_table


def _make_insert_chain(data):
    """Build mock chain: table().insert().execute() -> data."""
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_insert.execute.return_value = _mock_supabase_response(data)
    mock_table.insert.return_value = mock_insert
    return mock_table


def _make_update_eq_eq_chain(data):
    """Build mock chain: table().update().eq().eq().execute() -> data."""
    mock_table = MagicMock()
    mock_update = MagicMock()
    mock_eq1 = MagicMock()
    mock_eq2 = MagicMock()
    mock_eq2.execute.return_value = _mock_supabase_response(data)
    mock_eq1.eq.return_value = mock_eq2
    mock_update.eq.return_value = mock_eq1
    mock_table.update.return_value = mock_update
    return mock_table


def _make_delete_eq_eq_chain(data):
    """Build mock chain: table().delete().eq().eq().execute() -> data."""
    mock_table = MagicMock()
    mock_delete = MagicMock()
    mock_eq1 = MagicMock()
    mock_eq2 = MagicMock()
    mock_eq2.execute.return_value = _mock_supabase_response(data)
    mock_eq1.eq.return_value = mock_eq2
    mock_delete.eq.return_value = mock_eq1
    mock_table.delete.return_value = mock_delete
    return mock_table


@pytest.fixture
def service():
    """Create a SavedTestsService with mocked Supabase client."""
    with patch(
        "app.services.saved_tests._create_service_client",
        return_value=MagicMock(),
    ):
        svc = SavedTestsService()
        svc._supabase = MagicMock()
        yield svc


# =========================================================================
# save_test
# =========================================================================


SAMPLE_CONFIG = {"topics": ["algebra"], "num_questions": 10, "difficulty": "medium"}
SAMPLE_QUESTIONS = [
    {"id": 1, "text": "Solve x + 2 = 5", "answer": "x = 3"},
    {"id": 2, "text": "Solve 2x = 8", "answer": "x = 4"},
    {"id": 3, "text": "Solve x - 1 = 6", "answer": "x = 7"},
]
SAMPLE_SEED = 42


class TestSavedTestsService:
    """Tests for SavedTestsService CRUD operations."""

    async def test_save_test_creates_row(self, service):
        """Insert returns a row; returned dict has question_count = len(questions)."""
        inserted_row = {
            "id": TEST_ID,
            "test_name": "My Algebra Test",
            "config": SAMPLE_CONFIG,
            "seed": SAMPLE_SEED,
            "created_at": "2026-03-18T10:00:00Z",
        }

        # First call: _count_user_tests -> select().eq().execute()
        count_chain = _make_select_eq_chain([{"id": "a"}, {"id": "b"}])  # 2 existing
        # Second call: insert().execute()
        insert_chain = _make_insert_chain([inserted_row])

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return count_chain
            return insert_chain

        service._supabase.table.side_effect = table_side_effect

        result = await service.save_test(
            user_id=USER_ID,
            test_name="My Algebra Test",
            config=SAMPLE_CONFIG,
            seed=SAMPLE_SEED,
            questions=SAMPLE_QUESTIONS,
        )

        assert result["id"] == TEST_ID
        assert result["test_name"] == "My Algebra Test"
        assert result["config"] == SAMPLE_CONFIG
        assert result["seed"] == SAMPLE_SEED
        assert result["question_count"] == len(SAMPLE_QUESTIONS)
        assert result["created_at"] == "2026-03-18T10:00:00Z"
        # Verify insert was called
        insert_chain.insert.assert_called_once()

    async def test_save_test_limit_enforced(self, service):
        """When user has MAX_SAVED_TESTS, SavedTestLimitError is raised."""
        # _count_user_tests returns 100 rows
        count_data = [{"id": f"test-{i}"} for i in range(100)]
        count_chain = _make_select_eq_chain(count_data)
        service._supabase.table.return_value = count_chain

        with pytest.raises(SavedTestLimitError, match="Maximum of 100"):
            await service.save_test(
                user_id=USER_ID,
                test_name="Over Limit",
                config=SAMPLE_CONFIG,
                seed=SAMPLE_SEED,
                questions=SAMPLE_QUESTIONS,
            )

    # =====================================================================
    # list_tests
    # =====================================================================

    async def test_list_tests_returns_summaries_without_questions(self, service):
        """Returned dicts have question_count but NOT the questions field."""
        rows = [
            {
                "id": "test-1",
                "test_name": "Test One",
                "config": SAMPLE_CONFIG,
                "seed": 1,
                "questions": [{"q": 1}, {"q": 2}],
                "created_at": "2026-03-18T10:00:00Z",
            },
            {
                "id": "test-2",
                "test_name": "Test Two",
                "config": SAMPLE_CONFIG,
                "seed": 2,
                "questions": [{"q": 1}],
                "created_at": "2026-03-18T09:00:00Z",
            },
        ]
        list_chain = _make_select_eq_order_chain(rows)
        service._supabase.table.return_value = list_chain

        result = await service.list_tests(USER_ID)

        assert len(result) == 2
        # First test has 2 questions
        assert result[0]["question_count"] == 2
        assert result[0]["test_name"] == "Test One"
        assert "questions" not in result[0]
        # Second test has 1 question
        assert result[1]["question_count"] == 1
        assert result[1]["test_name"] == "Test Two"
        assert "questions" not in result[1]

    # =====================================================================
    # get_test
    # =====================================================================

    async def test_get_test_returns_full_data(self, service):
        """Full row including questions is returned."""
        full_row = {
            "id": TEST_ID,
            "user_id": USER_ID,
            "test_name": "My Test",
            "config": SAMPLE_CONFIG,
            "seed": SAMPLE_SEED,
            "questions": SAMPLE_QUESTIONS,
            "created_at": "2026-03-18T10:00:00Z",
        }
        get_chain = _make_select_eq_eq_chain([full_row])
        service._supabase.table.return_value = get_chain

        result = await service.get_test(TEST_ID, USER_ID)

        assert result is not None
        assert result["id"] == TEST_ID
        assert result["questions"] == SAMPLE_QUESTIONS
        assert result["test_name"] == "My Test"

    async def test_get_test_wrong_user_returns_none(self, service):
        """Empty result (wrong user or non-existent) returns None."""
        get_chain = _make_select_eq_eq_chain([])
        service._supabase.table.return_value = get_chain

        result = await service.get_test(TEST_ID, "wrong-user-id")

        assert result is None

    # =====================================================================
    # rename_test
    # =====================================================================

    async def test_rename_test_updates_name(self, service):
        """Update returns the row with the new name."""
        updated_row = {
            "id": TEST_ID,
            "test_name": "Renamed Test",
            "config": SAMPLE_CONFIG,
            "seed": SAMPLE_SEED,
            "questions": SAMPLE_QUESTIONS,
            "created_at": "2026-03-18T10:00:00Z",
        }
        update_chain = _make_update_eq_eq_chain([updated_row])
        service._supabase.table.return_value = update_chain

        result = await service.rename_test(TEST_ID, USER_ID, "Renamed Test")

        assert result is not None
        assert result["test_name"] == "Renamed Test"
        assert result["id"] == TEST_ID
        assert result["question_count"] == len(SAMPLE_QUESTIONS)
        # Should not include raw questions in summary
        assert "questions" not in result
        # Verify update was called with new name
        update_chain.update.assert_called_once_with({"test_name": "Renamed Test"})

    # =====================================================================
    # delete_test
    # =====================================================================

    async def test_delete_test_removes_row(self, service):
        """Delete returns data (the deleted row) -> True."""
        deleted_row = {
            "id": TEST_ID,
            "user_id": USER_ID,
            "test_name": "Deleted Test",
        }
        delete_chain = _make_delete_eq_eq_chain([deleted_row])
        service._supabase.table.return_value = delete_chain

        result = await service.delete_test(TEST_ID, USER_ID)

        assert result is True

    async def test_delete_test_not_found_returns_false(self, service):
        """Delete returns empty data (not found or wrong user) -> False."""
        delete_chain = _make_delete_eq_eq_chain([])
        service._supabase.table.return_value = delete_chain

        result = await service.delete_test(TEST_ID, USER_ID)

        assert result is False
