from f1.domain.models import DEFAULT_TEAM_COLOUR, Driver, FastestLapEntry, Lap


def filter_valid_laps(laps: list[Lap]) -> list[Lap]:
    """Remove voltas sem tempo registrado ou de saida dos pits."""
    return [
        lap
        for lap in laps
        if lap.lap_duration is not None
        and lap.lap_duration > 0
        and not lap.is_pit_out_lap
    ]


def build_driver_index(drivers: list[Driver]) -> dict[int, Driver]:
    return {driver.driver_number: driver for driver in drivers}


def best_lap_per_driver(laps: list[Lap]) -> list[Lap]:
    best: dict[int, Lap] = {}
    for lap in laps:
        if lap.lap_duration is None:
            continue
        current = best.get(lap.driver_number)
        current_duration = current.lap_duration if current else None
        if current_duration is None or lap.lap_duration < current_duration:
            best[lap.driver_number] = lap
    return list(best.values())


def compute_top_n_laps(
    laps: list[Lap], drivers_index: dict[int, Driver], n: int
) -> list[FastestLapEntry]:
    """Ranking das melhores voltas, uma por piloto, ordenado pelo tempo."""
    ranked = sorted(best_lap_per_driver(laps), key=lambda lap: lap.lap_duration)[:n]
    if not ranked:
        return []

    fastest = ranked[0].lap_duration
    return [
        _to_entry(position, lap, drivers_index.get(lap.driver_number), fastest)
        for position, lap in enumerate(ranked, start=1)
    ]


def average_lap_duration(laps: list[Lap]) -> float | None:
    durations = [lap.lap_duration for lap in laps if lap.lap_duration is not None]
    if not durations:
        return None
    return sum(durations) / len(durations)


def format_lap_time(seconds: float | None) -> str:
    """Formata segundos como M:SS.mmm (ex.: 83.456 -> 1:23.456)."""
    if seconds is None:
        return "-"
    total_ms = round(seconds * 1000)
    minutes, remainder_ms = divmod(total_ms, 60_000)
    secs, ms = divmod(remainder_ms, 1000)
    if minutes:
        return f"{minutes}:{secs:02d}.{ms:03d}"
    return f"{secs}.{ms:03d}"


def _to_entry(
    position: int, lap: Lap, driver: Driver | None, fastest: float
) -> FastestLapEntry:
    duration = lap.lap_duration or 0.0
    return FastestLapEntry(
        position=position,
        driver_number=lap.driver_number,
        driver_name=driver.display_name if driver else f"#{lap.driver_number}",
        name_acronym=(driver.name_acronym if driver else None)
        or str(lap.driver_number),
        team_name=(driver.team_name if driver else None) or "Desconhecida",
        team_colour=driver.team_colour_hex if driver else DEFAULT_TEAM_COLOUR,
        lap_number=lap.lap_number,
        lap_duration=duration,
        gap_to_fastest=round(duration - fastest, 3),
        duration_sector_1=lap.duration_sector_1,
        duration_sector_2=lap.duration_sector_2,
        duration_sector_3=lap.duration_sector_3,
        st_speed=lap.st_speed,
    )
