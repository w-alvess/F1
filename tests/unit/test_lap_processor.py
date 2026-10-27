import pytest

from f1.domain.models import DEFAULT_TEAM_COLOUR, Driver, Lap
from f1.processing.lap_processor import (
    average_lap_duration,
    best_lap_per_driver,
    build_driver_index,
    compute_top_n_laps,
    filter_valid_laps,
    format_lap_time,
)


def test_filter_valid_laps_removes_missing_duration_and_pit_out(
    laps: list[Lap],
) -> None:
    valid = filter_valid_laps(laps)

    assert [(lap.driver_number, lap.lap_number) for lap in valid] == [
        (1, 2),
        (1, 3),
        (44, 2),
        (16, 2),
    ]


def test_filter_valid_laps_removes_non_positive_duration() -> None:
    laps = [Lap(driver_number=1, lap_number=1, lap_duration=0.0)]

    assert filter_valid_laps(laps) == []


def test_build_driver_index_maps_by_number(drivers: list[Driver]) -> None:
    index = build_driver_index(drivers)

    assert set(index) == {1, 44, 16}
    assert index[44].name_acronym == "HAM"


def test_best_lap_per_driver_keeps_fastest_lap(laps: list[Lap]) -> None:
    best = {lap.driver_number: lap for lap in best_lap_per_driver(laps)}

    assert best[1].lap_number == 3
    assert best[16].lap_duration == 90.0


def test_compute_top_n_laps_ranks_one_lap_per_driver(
    laps: list[Lap], drivers: list[Driver]
) -> None:
    entries = compute_top_n_laps(
        filter_valid_laps(laps), build_driver_index(drivers), 10
    )

    assert [e.name_acronym for e in entries] == ["VER", "LEC", "HAM"]
    assert [e.position for e in entries] == [1, 2, 3]
    assert entries[0].gap_to_fastest == 0.0
    assert entries[1].gap_to_fastest == pytest.approx(0.3)
    assert entries[0].team_colour == "#3671C6"


def test_compute_top_n_laps_limits_to_n(laps: list[Lap], drivers: list[Driver]) -> None:
    entries = compute_top_n_laps(
        filter_valid_laps(laps), build_driver_index(drivers), 2
    )

    assert len(entries) == 2


def test_compute_top_n_laps_handles_unknown_driver() -> None:
    laps = [Lap(driver_number=99, lap_number=5, lap_duration=88.0)]

    [entry] = compute_top_n_laps(laps, {}, 10)

    assert entry.driver_name == "#99"
    assert entry.name_acronym == "99"
    assert entry.team_name == "Desconhecida"
    assert entry.team_colour == DEFAULT_TEAM_COLOUR


def test_compute_top_n_laps_empty() -> None:
    assert compute_top_n_laps([], {}, 10) == []


def test_average_lap_duration(laps: list[Lap]) -> None:
    valid = filter_valid_laps(laps)

    assert average_lap_duration(valid) == pytest.approx((92.5 + 91.2 + 91.8 + 91.5) / 4)


def test_average_lap_duration_empty() -> None:
    assert average_lap_duration([]) is None


@pytest.mark.parametrize(
    ("seconds", "expected"),
    [
        (83.456, "1:23.456"),
        (91.0, "1:31.000"),
        (26.966, "26.966"),
        (59.9996, "1:00.000"),
        (None, "-"),
    ],
)
def test_format_lap_time(seconds: float | None, expected: str) -> None:
    assert format_lap_time(seconds) == expected
