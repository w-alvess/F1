from typing import Any

import pytest

from f1.domain.models import Driver, Lap


@pytest.fixture(scope="module")
def meeting_payload() -> dict[str, Any]:
    return {
        "meeting_key": 1219,
        "meeting_name": "Singapore Grand Prix",
        "country_name": "Singapore",
        "circuit_short_name": "Singapore",
        "location": "Marina Bay",
        "date_start": "2023-09-15T09:30:00+00:00",
        "year": 2023,
        "gmt_offset": "08:00:00",
    }


@pytest.fixture(scope="module")
def session_payload() -> dict[str, Any]:
    return {
        "session_key": 9161,
        "meeting_key": 1219,
        "session_name": "Race",
        "session_type": "Race",
        "date_start": "2023-09-17T12:00:00+00:00",
        "date_end": "2023-09-17T14:00:00+00:00",
        "country_name": "Singapore",
        "year": 2023,
    }


@pytest.fixture(scope="module")
def driver_payload() -> dict[str, Any]:
    return {
        "broadcast_name": "M VERSTAPPEN",
        "driver_number": 1,
        "full_name": "Max VERSTAPPEN",
        "name_acronym": "VER",
        "team_name": "Red Bull Racing",
        "team_colour": "3671C6",
        "headshot_url": "https://example.org/ver.png",
        "session_key": 9158,
    }


@pytest.fixture(scope="module")
def lap_payload() -> dict[str, Any]:
    return {
        "date_start": "2023-09-16T13:59:07.606000+00:00",
        "driver_number": 63,
        "duration_sector_1": 26.966,
        "duration_sector_2": 38.657,
        "duration_sector_3": 26.12,
        "i1_speed": 307,
        "i2_speed": 277,
        "is_pit_out_lap": False,
        "lap_duration": 91.743,
        "lap_number": 8,
        "segments_sector_1": [2049, 2049, 2049, 2051],
        "st_speed": 298,
        "session_key": 9161,
    }


@pytest.fixture
def drivers() -> list[Driver]:
    return [
        Driver(
            driver_number=1,
            full_name="Max VERSTAPPEN",
            name_acronym="VER",
            team_name="Red Bull Racing",
            team_colour="3671C6",
        ),
        Driver(
            driver_number=44,
            full_name="Lewis HAMILTON",
            name_acronym="HAM",
            team_name="Mercedes",
            team_colour="27F4D2",
        ),
        Driver(
            driver_number=16,
            full_name="Charles LECLERC",
            name_acronym="LEC",
            team_name="Ferrari",
            team_colour="E8002D",
        ),
    ]


@pytest.fixture
def laps() -> list[Lap]:
    return [
        Lap(driver_number=1, lap_number=1, lap_duration=None),
        Lap(driver_number=1, lap_number=2, lap_duration=92.5),
        Lap(driver_number=1, lap_number=3, lap_duration=91.2),
        Lap(driver_number=44, lap_number=1, lap_duration=95.0, is_pit_out_lap=True),
        Lap(driver_number=44, lap_number=2, lap_duration=91.8),
        Lap(driver_number=16, lap_number=2, lap_duration=91.5),
        Lap(driver_number=16, lap_number=3, lap_duration=90.0, is_pit_out_lap=True),
    ]
