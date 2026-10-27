from collections.abc import Iterator

import pytest

from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)
from f1.utils.config import load_settings

pytestmark = pytest.mark.integration


@pytest.fixture(scope="module")
def http_client() -> Iterator[HttpClient]:
    settings = load_settings()
    client = HttpClient(base_url=settings.base_url, timeout=settings.timeout)
    yield client
    client.close()


def test_meetings_2023(http_client: HttpClient) -> None:
    meetings = OpenF1MeetingRepository(http_client).list(2023)

    assert meetings
    assert all(m.year == 2023 for m in meetings)


def test_sessions_latest_meeting(http_client: HttpClient) -> None:
    sessions = OpenF1SessionRepository(http_client).list("latest")

    assert sessions


def test_drivers_latest_session(http_client: HttpClient) -> None:
    drivers = OpenF1DriverRepository(http_client).list("latest")

    assert drivers
    assert all(d.driver_number > 0 for d in drivers)


def test_session_overview_latest(http_client: HttpClient) -> None:
    service = F1DashboardService(
        meeting_repository=OpenF1MeetingRepository(http_client),
        session_repository=OpenF1SessionRepository(http_client),
        driver_repository=OpenF1DriverRepository(http_client),
        lap_repository=OpenF1LapRepository(http_client),
    )

    overview = service.get_session_overview("latest", n=10)

    assert overview.total_laps >= overview.valid_laps
    assert len(overview.top_laps) <= 10
    durations = [entry.lap_duration for entry in overview.top_laps]
    assert durations == sorted(durations)
