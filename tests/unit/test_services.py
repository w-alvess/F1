from datetime import UTC, datetime
from unittest.mock import MagicMock

import pytest

from f1.domain.models import Driver, Lap, Meeting, Session
from f1.domain.services import F1DashboardService


@pytest.fixture
def repos(drivers: list[Driver], laps: list[Lap]) -> dict[str, MagicMock]:
    meetings = MagicMock()
    meetings.list.return_value = [
        Meeting(
            meeting_key=2,
            meeting_name="Monaco Grand Prix",
            year=2024,
            date_start=datetime(2024, 5, 24, tzinfo=UTC),
        ),
        Meeting(meeting_key=3, meeting_name="Pre-Season Testing", year=2024),
        Meeting(
            meeting_key=1,
            meeting_name="Bahrain Grand Prix",
            year=2024,
            date_start=datetime(2024, 2, 29, tzinfo=UTC),
        ),
    ]
    sessions = MagicMock()
    sessions.list.return_value = [
        Session(
            session_key=20,
            session_name="Race",
            date_start=datetime(2024, 5, 26, tzinfo=UTC),
        ),
        Session(
            session_key=10,
            session_name="Practice 1",
            date_start=datetime(2024, 5, 24, tzinfo=UTC),
        ),
    ]
    driver_repo = MagicMock()
    driver_repo.list.return_value = drivers
    lap_repo = MagicMock()
    lap_repo.list.return_value = laps
    return {
        "meeting_repository": meetings,
        "session_repository": sessions,
        "driver_repository": driver_repo,
        "lap_repository": lap_repo,
    }


@pytest.fixture
def service(repos: dict[str, MagicMock]) -> F1DashboardService:
    return F1DashboardService(**repos)


def test_list_meetings_sorted_by_date_with_undated_last(
    service: F1DashboardService, repos: dict[str, MagicMock]
) -> None:
    meetings = service.list_meetings(2024)

    assert [m.meeting_key for m in meetings] == [1, 2, 3]
    repos["meeting_repository"].list.assert_called_once_with(year=2024)


def test_list_sessions_sorted_by_date(
    service: F1DashboardService, repos: dict[str, MagicMock]
) -> None:
    sessions = service.list_sessions(1229)

    assert [s.session_name for s in sessions] == ["Practice 1", "Race"]
    repos["session_repository"].list.assert_called_once_with(meeting_key=1229)


def test_get_top_n_fastest_laps(
    service: F1DashboardService, repos: dict[str, MagicMock]
) -> None:
    top = service.get_top_n_fastest_laps(9161, n=2)

    assert [e.name_acronym for e in top] == ["VER", "LEC"]
    repos["driver_repository"].list.assert_called_once_with(session_key=9161)
    repos["lap_repository"].list.assert_called_once_with(session_key=9161)


def test_get_session_overview(service: F1DashboardService) -> None:
    overview = service.get_session_overview("latest", n=10)

    assert overview.session_key == "latest"
    assert overview.total_laps == 7
    assert overview.valid_laps == 4
    assert [d.driver_number for d in overview.drivers] == [1, 16, 44]
    assert overview.fastest_lap is not None
    assert overview.fastest_lap.name_acronym == "VER"
    assert overview.average_lap_duration == pytest.approx(91.75)


def test_get_session_overview_without_laps(
    service: F1DashboardService, repos: dict[str, MagicMock]
) -> None:
    repos["lap_repository"].list.return_value = []

    overview = service.get_session_overview(9161)

    assert overview.top_laps == []
    assert overview.average_lap_duration is None


@pytest.mark.parametrize("n", [0, -1])
def test_invalid_n_raises(service: F1DashboardService, n: int) -> None:
    with pytest.raises(ValueError):
        service.get_top_n_fastest_laps(9161, n=n)
    with pytest.raises(ValueError):
        service.get_session_overview(9161, n=n)
