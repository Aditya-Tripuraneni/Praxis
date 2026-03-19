"""Unit tests for StatsService.

All Supabase calls are mocked -- no external connections needed.
Tests cover record_generation, update_streak, and get_user_stats.
"""

from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

from app.services.stats import StatsService

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

USER_ID = "test-user-id-123"


def _mock_supabase_response(data):
    """Create a mock Supabase .execute() response."""
    resp = MagicMock()
    resp.data = data
    return resp


def _make_select_chain(data):
    """Build mock chain: table().select().eq().execute() -> data."""
    mock_table = MagicMock()
    mock_select = MagicMock()
    mock_eq = MagicMock()
    mock_eq.execute.return_value = _mock_supabase_response(data)
    mock_select.eq.return_value = mock_eq
    mock_table.select.return_value = mock_select
    return mock_table


def _make_insert_chain():
    """Build mock chain: table().insert().execute()."""
    mock_table = MagicMock()
    mock_insert = MagicMock()
    mock_insert.execute.return_value = _mock_supabase_response([])
    mock_table.insert.return_value = mock_insert
    return mock_table


def _make_update_chain():
    """Build mock chain: table().update().eq().execute()."""
    mock_table = MagicMock()
    mock_update = MagicMock()
    mock_eq = MagicMock()
    mock_eq.execute.return_value = _mock_supabase_response([])
    mock_update.eq.return_value = mock_eq
    mock_table.update.return_value = mock_update
    return mock_table


def _make_upsert_chain():
    """Build mock chain: table().upsert().execute()."""
    mock_table = MagicMock()
    mock_upsert = MagicMock()
    mock_upsert.execute.return_value = _mock_supabase_response([])
    mock_table.upsert.return_value = mock_upsert
    return mock_table


@pytest.fixture
def service():
    """Create a StatsService with mocked Supabase client."""
    with patch(
        "app.services.stats._create_service_client",
        return_value=MagicMock(),
    ):
        svc = StatsService()
        svc._supabase = MagicMock()
        yield svc


# =========================================================================
# record_generation
# =========================================================================


class TestRecordGeneration:
    """Tests for StatsService.record_generation()."""

    async def test_creates_row_for_new_user(self, service):
        """First generation inserts a new row."""
        select_chain = _make_select_chain([])
        insert_chain = _make_insert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return insert_chain

        service._supabase.table.side_effect = table_side_effect

        await service.record_generation(USER_ID, 10, {"algebra": 10})

        # Verify insert was called
        insert_chain.insert.assert_called_once()
        insert_args = insert_chain.insert.call_args[0][0]
        assert insert_args["user_id"] == USER_ID
        assert insert_args["tests_generated"] == 1
        assert insert_args["questions_generated"] == 10
        assert insert_args["topic_counts"] == {"algebra": 10}

    async def test_increments_existing_row(self, service):
        """Subsequent generation updates existing row."""
        existing_row = {
            "tests_generated": 5,
            "questions_generated": 100,
            "topic_counts": {"algebra": 50},
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.record_generation(USER_ID, 20, {"algebra": 10, "trig": 10})

        update_chain.update.assert_called_once()
        update_args = update_chain.update.call_args[0][0]
        assert update_args["tests_generated"] == 6
        assert update_args["questions_generated"] == 120

    async def test_merges_topic_counts(self, service):
        """New topics are added, existing topics are incremented."""
        existing_row = {
            "tests_generated": 3,
            "questions_generated": 60,
            "topic_counts": {"algebra": 30},
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.record_generation(USER_ID, 15, {"algebra": 10, "calculus": 5})

        update_args = update_chain.update.call_args[0][0]
        assert update_args["topic_counts"] == {
            "algebra": 40,
            "calculus": 5,
        }

    async def test_handles_none_topic_counts(self, service):
        """Existing row with topic_counts=None merges correctly."""
        existing_row = {
            "tests_generated": 1,
            "questions_generated": 10,
            "topic_counts": None,
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.record_generation(USER_ID, 5, {"trig": 5})

        update_args = update_chain.update.call_args[0][0]
        assert update_args["topic_counts"] == {"trig": 5}

    async def test_error_does_not_raise(self, service):
        """Supabase error is logged, not propagated."""
        service._supabase.table.side_effect = Exception("DB down")

        with patch("app.services.stats.logger") as mock_logger:
            # Should not raise
            await service.record_generation(USER_ID, 10, {"algebra": 10})
            mock_logger.warning.assert_called_once()


# =========================================================================
# update_streak
# =========================================================================


class TestUpdateStreak:
    """Tests for StatsService.update_streak()."""

    async def test_first_practice(self, service):
        """No existing row -- creates with streak=1."""
        select_chain = _make_select_chain([])
        upsert_chain = _make_upsert_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return upsert_chain

        service._supabase.table.side_effect = table_side_effect

        await service.update_streak(USER_ID)

        upsert_chain.upsert.assert_called_once()
        upsert_args = upsert_chain.upsert.call_args[0][0]
        assert upsert_args["streak_current"] == 1
        assert upsert_args["streak_best"] == 1
        assert upsert_args["user_id"] == USER_ID

    async def test_consecutive_day(self, service):
        """Last practice was yesterday -- increments streak."""
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        existing_row = {
            "streak_current": 5,
            "streak_best": 10,
            "last_practice_date": yesterday.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.update_streak(USER_ID)

        update_chain.update.assert_called_once()
        update_args = update_chain.update.call_args[0][0]
        assert update_args["streak_current"] == 6
        assert update_args["streak_best"] == 10

    async def test_same_day_noop(self, service):
        """Already practiced today -- no update."""
        today = datetime.now(timezone.utc).date()

        existing_row = {
            "streak_current": 3,
            "streak_best": 7,
            "last_practice_date": today.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        await service.update_streak(USER_ID)

        # Only one table() call for the select -- no update/upsert
        assert service._supabase.table.call_count == 1

    async def test_gap_resets(self, service):
        """Last practice > 1 day ago -- resets streak to 1."""
        today = datetime.now(timezone.utc).date()
        three_days_ago = today - timedelta(days=3)

        existing_row = {
            "streak_current": 10,
            "streak_best": 15,
            "last_practice_date": three_days_ago.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.update_streak(USER_ID)

        update_args = update_chain.update.call_args[0][0]
        assert update_args["streak_current"] == 1

    async def test_best_preserved(self, service):
        """New streak < best -- best unchanged."""
        today = datetime.now(timezone.utc).date()
        three_days_ago = today - timedelta(days=3)

        existing_row = {
            "streak_current": 10,
            "streak_best": 10,
            "last_practice_date": three_days_ago.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.update_streak(USER_ID)

        update_args = update_chain.update.call_args[0][0]
        # Streak reset to 1, but best stays at 10
        assert update_args["streak_current"] == 1
        assert update_args["streak_best"] == 10

    async def test_new_best(self, service):
        """New streak > best -- best updated."""
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)

        existing_row = {
            "streak_current": 9,
            "streak_best": 9,
            "last_practice_date": yesterday.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.update_streak(USER_ID)

        update_args = update_chain.update.call_args[0][0]
        assert update_args["streak_current"] == 10
        assert update_args["streak_best"] == 10

    async def test_no_last_practice_date(self, service):
        """Row exists but last_practice_date is None -- streak = 1."""
        existing_row = {
            "streak_current": 0,
            "streak_best": 0,
            "last_practice_date": None,
        }
        select_chain = _make_select_chain([existing_row])
        update_chain = _make_update_chain()

        call_count = 0

        def table_side_effect(name):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return select_chain
            return update_chain

        service._supabase.table.side_effect = table_side_effect

        await service.update_streak(USER_ID)

        update_args = update_chain.update.call_args[0][0]
        assert update_args["streak_current"] == 1
        assert update_args["streak_best"] == 1

    async def test_error_does_not_raise(self, service):
        """Supabase error is logged, not propagated."""
        service._supabase.table.side_effect = Exception("DB down")

        with patch("app.services.stats.logger") as mock_logger:
            await service.update_streak(USER_ID)
            mock_logger.warning.assert_called_once()


# =========================================================================
# get_user_stats
# =========================================================================


class TestGetUserStats:
    """Tests for StatsService.get_user_stats()."""

    async def test_returns_defaults_when_no_row(self, service):
        """No row in DB -- returns default dict."""
        select_chain = _make_select_chain([])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["tests_generated"] == 0
        assert result["questions_generated"] == 0
        assert result["topic_counts"] == {}
        assert result["streak_current"] == 0
        assert result["streak_best"] == 0
        assert result["is_active_today"] is False
        assert result["last_test_duration"] is None

    async def test_returns_existing_data(self, service):
        """Row exists -- returns correct data."""
        today = datetime.now(timezone.utc).date()
        existing_row = {
            "tests_generated": 18,
            "questions_generated": 247,
            "topic_counts": {"algebra": 100, "trig": 147},
            "streak_current": 5,
            "streak_best": 12,
            "last_practice_date": today.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["tests_generated"] == 18
        assert result["questions_generated"] == 247
        assert result["topic_counts"] == {
            "algebra": 100,
            "trig": 147,
        }
        assert result["streak_current"] == 5
        assert result["streak_best"] == 12

    async def test_is_active_today_true(self, service):
        """last_practice_date == today -- is_active_today=True."""
        today = datetime.now(timezone.utc).date()
        existing_row = {
            "tests_generated": 1,
            "questions_generated": 10,
            "topic_counts": {},
            "streak_current": 1,
            "streak_best": 1,
            "last_practice_date": today.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["is_active_today"] is True

    async def test_is_active_today_false(self, service):
        """last_practice_date == yesterday -- is_active_today=False."""
        today = datetime.now(timezone.utc).date()
        yesterday = today - timedelta(days=1)
        existing_row = {
            "tests_generated": 5,
            "questions_generated": 50,
            "topic_counts": {},
            "streak_current": 3,
            "streak_best": 7,
            "last_practice_date": yesterday.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["is_active_today"] is False

    async def test_is_active_today_false_no_date(self, service):
        """last_practice_date is None -- is_active_today=False."""
        existing_row = {
            "tests_generated": 2,
            "questions_generated": 20,
            "topic_counts": {},
            "streak_current": 0,
            "streak_best": 0,
            "last_practice_date": None,
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["is_active_today"] is False

    async def test_returns_last_test_duration(self, service):
        """Row with last_test_duration -- returns it."""
        today = datetime.now(timezone.utc).date()
        existing_row = {
            "tests_generated": 5,
            "questions_generated": 50,
            "topic_counts": {},
            "streak_current": 1,
            "streak_best": 3,
            "last_practice_date": today.isoformat(),
            "last_test_duration": 1425,
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["last_test_duration"] == 1425

    async def test_error_returns_defaults(self, service):
        """Supabase error -- returns defaults, doesn't raise."""
        service._supabase.table.side_effect = Exception("DB down")

        result = await service.get_user_stats(USER_ID)

        assert result["tests_generated"] == 0
        assert result["questions_generated"] == 0
        assert result["topic_counts"] == {}
        assert result["streak_current"] == 0
        assert result["streak_best"] == 0
        assert result["is_active_today"] is False
        assert result["last_test_duration"] is None

    async def test_none_topic_counts_returns_empty_dict(self, service):
        """Row with topic_counts=None returns empty dict."""
        today = datetime.now(timezone.utc).date()
        existing_row = {
            "tests_generated": 1,
            "questions_generated": 5,
            "topic_counts": None,
            "streak_current": 1,
            "streak_best": 1,
            "last_practice_date": today.isoformat(),
        }
        select_chain = _make_select_chain([existing_row])
        service._supabase.table.return_value = select_chain

        result = await service.get_user_stats(USER_ID)

        assert result["topic_counts"] == {}


# =========================================================================
# save_timer_duration
# =========================================================================


class TestSaveTimerDuration:
    """Tests for StatsService.save_timer_duration()."""

    async def test_upserts_duration(self, service):
        """Saves duration via upsert."""
        upsert_chain = _make_upsert_chain()
        service._supabase.table.return_value = upsert_chain

        await service.save_timer_duration(USER_ID, 300)

        upsert_chain.upsert.assert_called_once()
        upsert_args = upsert_chain.upsert.call_args[0][0]
        assert upsert_args["user_id"] == USER_ID
        assert upsert_args["last_test_duration"] == 300
        assert "updated_at" in upsert_args


class TestTimerModels:
    """Tests for timer Pydantic models."""

    def test_timer_request_valid(self):
        from app.models.stats import TimerSaveRequest

        req = TimerSaveRequest(duration=300)
        assert req.duration == 300

    def test_timer_request_min_valid(self):
        from app.models.stats import TimerSaveRequest

        req = TimerSaveRequest(duration=1)
        assert req.duration == 1

    def test_timer_request_max_valid(self):
        from app.models.stats import TimerSaveRequest

        req = TimerSaveRequest(duration=86400)
        assert req.duration == 86400

    def test_timer_request_zero_invalid(self):
        from app.models.stats import TimerSaveRequest

        with pytest.raises(Exception):
            TimerSaveRequest(duration=0)

    def test_timer_request_negative_invalid(self):
        from app.models.stats import TimerSaveRequest

        with pytest.raises(Exception):
            TimerSaveRequest(duration=-1)

    def test_timer_request_over_max_invalid(self):
        from app.models.stats import TimerSaveRequest

        with pytest.raises(Exception):
            TimerSaveRequest(duration=86401)
