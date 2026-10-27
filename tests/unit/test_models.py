from datetime import UTC, datetime
from typing import Any

import pytest
from pydantic import ValidationError

from f1.domain.models import (
    DEFAULT_TEAM_COLOUR,
    Driver,
    FastestLapEntry,
    Lap,
    Meeting,
    Session,
    SessionOverview,
    Stint,
    Weather,
)


def test_meeting_parses_payload_and_ignores_extra_fields(
    meeting_payload: dict[str, Any],
) -> None:
    meeting = Meeting.model_validate(meeting_payload)

    assert meeting.meeting_key == 1219
    assert meeting.date_start == datetime(2023, 9, 15, 9, 30, tzinfo=UTC)
    assert not hasattr(meeting, "gmt_offset")


def test_session_parses_payload(session_payload: dict[str, Any]) -> None:
    session = Session.model_validate(session_payload)

    assert session.session_key == 9161
    assert session.session_type == "Race"
    assert session.date_end is not None


def test_driver_parses_payload(driver_payload: dict[str, Any]) -> None:
    driver = Driver.model_validate(driver_payload)

    assert driver.name_acronym == "VER"
    assert driver.team_colour_hex == "#3671C6"
    assert driver.display_name == "Max VERSTAPPEN"


@pytest.mark.parametrize(
    ("colour", "expected"),
    [("#E8002D", "#E8002D"), (None, DEFAULT_TEAM_COLOUR), ("", DEFAULT_TEAM_COLOUR)],
)
def test_driver_team_colour_hex(colour: str | None, expected: str) -> None:
    assert Driver(driver_number=1, team_colour=colour).team_colour_hex == expected


def test_driver_display_name_fallbacks() -> None:
    assert Driver(driver_number=7, broadcast_name="K RAIKKONEN").display_name == (
        "K RAIKKONEN"
    )
    assert Driver(driver_number=7).display_name == "#7"


def test_lap_parses_payload(lap_payload: dict[str, Any]) -> None:
    lap = Lap.model_validate(lap_payload)

    assert lap.lap_duration == 91.743
    assert lap.st_speed == 298
    assert lap.is_pit_out_lap is False


def test_lap_accepts_null_duration(lap_payload: dict[str, Any]) -> None:
    lap = Lap.model_validate({**lap_payload, "lap_duration": None, "i1_speed": None})

    assert lap.lap_duration is None


def test_lap_rejects_missing_required_field(lap_payload: dict[str, Any]) -> None:
    payload = {k: v for k, v in lap_payload.items() if k != "driver_number"}

    with pytest.raises(ValidationError):
        Lap.model_validate(payload)


def test_models_are_immutable(lap_payload: dict[str, Any]) -> None:
    lap = Lap.model_validate(lap_payload)

    with pytest.raises(ValidationError):
        lap.lap_number = 99  # type: ignore[misc]


def test_stint_and_weather_parse() -> None:
    stint = Stint.model_validate(
        {"driver_number": 1, "compound": "SOFT", "lap_start": 1, "lap_end": 12}
    )
    weather = Weather.model_validate(
        {"date": "2023-09-17T12:00:00+00:00", "air_temperature": 30.1, "rainfall": 0}
    )

    assert stint.compound == "SOFT"
    assert weather.air_temperature == 30.1


def test_session_overview_fastest_lap() -> None:
    entry = FastestLapEntry(
        position=1,
        driver_number=1,
        driver_name="Max VERSTAPPEN",
        name_acronym="VER",
        team_name="Red Bull Racing",
        team_colour="#3671C6",
        lap_number=3,
        lap_duration=91.2,
        gap_to_fastest=0.0,
    )
    overview = SessionOverview(
        session_key=9161, drivers=[], top_laps=[entry], total_laps=1, valid_laps=1
    )
    empty = SessionOverview(
        session_key=9161, drivers=[], top_laps=[], total_laps=0, valid_laps=0
    )

    assert overview.fastest_lap == entry
    assert empty.fastest_lap is None
