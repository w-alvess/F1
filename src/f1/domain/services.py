from datetime import datetime

from f1.domain.models import FastestLapEntry, Meeting, Session, SessionOverview
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingKey,
    MeetingRepository,
    SessionKey,
    SessionRepository,
)
from f1.processing.lap_processor import (
    average_lap_duration,
    build_driver_index,
    compute_top_n_laps,
    filter_valid_laps,
)

DEFAULT_TOP_N = 10


def _sort_key(start: datetime | None) -> float:
    return start.timestamp() if start else float("inf")


class F1DashboardService:
    def __init__(
        self,
        meeting_repository: MeetingRepository,
        session_repository: SessionRepository,
        driver_repository: DriverRepository,
        lap_repository: LapRepository,
    ) -> None:
        self._meetings = meeting_repository
        self._sessions = session_repository
        self._drivers = driver_repository
        self._laps = lap_repository

    def list_meetings(self, year: int) -> list[Meeting]:
        meetings = self._meetings.list(year=year)
        return sorted(meetings, key=lambda m: _sort_key(m.date_start))

    def list_sessions(self, meeting_key: MeetingKey) -> list[Session]:
        sessions = self._sessions.list(meeting_key=meeting_key)
        return sorted(sessions, key=lambda s: _sort_key(s.date_start))

    def get_top_n_fastest_laps(
        self, session_key: SessionKey, n: int = DEFAULT_TOP_N
    ) -> list[FastestLapEntry]:
        _validate_n(n)
        drivers_index = build_driver_index(self._drivers.list(session_key=session_key))
        valid_laps = filter_valid_laps(self._laps.list(session_key=session_key))
        return compute_top_n_laps(valid_laps, drivers_index, n)

    def get_session_overview(
        self, session_key: SessionKey, n: int = DEFAULT_TOP_N
    ) -> SessionOverview:
        _validate_n(n)
        drivers = self._drivers.list(session_key=session_key)
        laps = self._laps.list(session_key=session_key)
        valid_laps = filter_valid_laps(laps)
        return SessionOverview(
            session_key=session_key,
            drivers=sorted(drivers, key=lambda d: d.driver_number),
            top_laps=compute_top_n_laps(valid_laps, build_driver_index(drivers), n),
            total_laps=len(laps),
            valid_laps=len(valid_laps),
            average_lap_duration=average_lap_duration(valid_laps),
        )


def _validate_n(n: int) -> None:
    if n <= 0:
        raise ValueError("n deve ser maior que zero")
