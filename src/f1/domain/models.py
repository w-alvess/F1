from datetime import datetime

from pydantic import BaseModel, ConfigDict

DEFAULT_TEAM_COLOUR = "#888888"


class OpenF1Model(BaseModel):
    """Base dos payloads OpenF1: imutavel e tolerante a campos novos da API."""

    model_config = ConfigDict(frozen=True, extra="ignore")


class Meeting(OpenF1Model):
    meeting_key: int
    meeting_name: str
    country_name: str | None = None
    circuit_short_name: str | None = None
    location: str | None = None
    year: int
    date_start: datetime | None = None


class Session(OpenF1Model):
    session_key: int
    meeting_key: int | None = None
    session_name: str
    session_type: str | None = None
    date_start: datetime | None = None
    date_end: datetime | None = None
    country_name: str | None = None
    year: int | None = None


class Driver(OpenF1Model):
    driver_number: int
    full_name: str | None = None
    broadcast_name: str | None = None
    name_acronym: str | None = None
    team_name: str | None = None
    team_colour: str | None = None
    headshot_url: str | None = None

    @property
    def team_colour_hex(self) -> str:
        if not self.team_colour:
            return DEFAULT_TEAM_COLOUR
        colour = self.team_colour.lstrip("#")
        return f"#{colour}"

    @property
    def display_name(self) -> str:
        return self.full_name or self.broadcast_name or f"#{self.driver_number}"


class Lap(OpenF1Model):
    driver_number: int
    lap_number: int
    lap_duration: float | None = None
    duration_sector_1: float | None = None
    duration_sector_2: float | None = None
    duration_sector_3: float | None = None
    i1_speed: int | None = None
    i2_speed: int | None = None
    st_speed: int | None = None
    is_pit_out_lap: bool = False


class Stint(OpenF1Model):
    driver_number: int
    stint_number: int | None = None
    compound: str | None = None
    lap_start: int | None = None
    lap_end: int | None = None
    tyre_age_at_start: int | None = None


class Weather(OpenF1Model):
    date: datetime
    air_temperature: float | None = None
    track_temperature: float | None = None
    humidity: float | None = None
    wind_speed: float | None = None
    wind_direction: int | None = None
    rainfall: int | None = None
    pressure: float | None = None


class FastestLapEntry(OpenF1Model):
    """Projecao pos-processamento: melhor volta de um piloto na sessao."""

    position: int
    driver_number: int
    driver_name: str
    name_acronym: str
    team_name: str
    team_colour: str
    lap_number: int
    lap_duration: float
    gap_to_fastest: float
    duration_sector_1: float | None = None
    duration_sector_2: float | None = None
    duration_sector_3: float | None = None
    st_speed: int | None = None


class SessionOverview(OpenF1Model):
    session_key: int | str
    drivers: list[Driver]
    top_laps: list[FastestLapEntry]
    total_laps: int
    valid_laps: int
    average_lap_duration: float | None = None

    @property
    def fastest_lap(self) -> FastestLapEntry | None:
        return self.top_laps[0] if self.top_laps else None
