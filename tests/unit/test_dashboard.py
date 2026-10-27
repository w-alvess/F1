from datetime import UTC, datetime

from f1.dashboard import latest_started_index, top_laps_to_dataframe
from f1.domain.models import Driver, Lap, Meeting
from f1.processing.lap_processor import (
    build_driver_index,
    compute_top_n_laps,
    filter_valid_laps,
)


def test_top_laps_to_dataframe(laps: list[Lap], drivers: list[Driver]) -> None:
    entries = compute_top_n_laps(
        filter_valid_laps(laps), build_driver_index(drivers), 10
    )

    table = top_laps_to_dataframe(entries)

    assert list(table["Pos"]) == [1, 2, 3]
    assert list(table["Piloto"]) == [
        "Max VERSTAPPEN",
        "Charles LECLERC",
        "Lewis HAMILTON",
    ]
    assert list(table["Gap"]) == ["-", "+0.300", "+0.600"]
    assert table.loc[0, "Tempo"] == "1:31.200"
    assert table.loc[0, "Cor"] == "#3671C6"


def test_latest_started_index() -> None:
    meetings = [
        Meeting(
            meeting_key=1,
            meeting_name="A",
            year=2024,
            date_start=datetime(2024, 3, 1, tzinfo=UTC),
        ),
        Meeting(
            meeting_key=2,
            meeting_name="B",
            year=2024,
            date_start=datetime(2024, 5, 1, tzinfo=UTC),
        ),
        Meeting(
            meeting_key=3,
            meeting_name="C",
            year=2024,
            date_start=datetime(2024, 9, 1, tzinfo=UTC),
        ),
        Meeting(meeting_key=4, meeting_name="D", year=2024),
    ]

    assert latest_started_index(meetings, datetime(2024, 6, 1, tzinfo=UTC)) == 1
    assert latest_started_index(meetings, datetime(2024, 1, 1, tzinfo=UTC)) == 0
    assert latest_started_index([], datetime(2024, 1, 1, tzinfo=UTC)) == 0
