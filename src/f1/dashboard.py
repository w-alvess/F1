"""Composition root do dashboard: `poetry run streamlit run src/f1/dashboard.py`."""

from datetime import UTC, datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from f1.domain.models import FastestLapEntry, Meeting, Session, SessionOverview
from f1.domain.services import F1DashboardService
from f1.ingestion.http_client import HttpClient, OpenF1Error
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)
from f1.processing.lap_processor import format_lap_time
from f1.utils.config import load_settings
from f1.utils.logger import get_logger

logger = get_logger(__name__)

FIRST_SEASON = 2023
LATEST = "latest"
CACHE_TTL_SECONDS = 3600
BAR_COLOUR = "#3b6fd4"


@st.cache_resource
def get_service() -> F1DashboardService:
    settings = load_settings()
    logger.info(
        "Iniciando dashboard (%s) em %s", settings.environment, settings.base_url
    )
    http_client = HttpClient(base_url=settings.base_url, timeout=settings.timeout)
    return F1DashboardService(
        meeting_repository=OpenF1MeetingRepository(http_client),
        session_repository=OpenF1SessionRepository(http_client),
        driver_repository=OpenF1DriverRepository(http_client),
        lap_repository=OpenF1LapRepository(http_client),
    )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_meetings(year: int) -> list[Meeting]:
    return get_service().list_meetings(year)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_sessions(meeting_key: int) -> list[Session]:
    return get_service().list_sessions(meeting_key)


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner=False)
def load_overview(session_key: int | str, n: int) -> SessionOverview:
    return get_service().get_session_overview(session_key, n=n)


def top_laps_to_dataframe(entries: list[FastestLapEntry]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Pos": entry.position,
                "Cor": entry.team_colour,
                "Piloto": entry.driver_name,
                "Equipe": entry.team_name,
                "Volta": entry.lap_number,
                "Tempo": format_lap_time(entry.lap_duration),
                "Gap": f"+{entry.gap_to_fastest:.3f}" if entry.position > 1 else "-",
                "S1": format_lap_time(entry.duration_sector_1),
                "S2": format_lap_time(entry.duration_sector_2),
                "S3": format_lap_time(entry.duration_sector_3),
                "Speed trap (km/h)": entry.st_speed,
            }
            for entry in entries
        ]
    )


def _team_swatch(colour: str) -> str:
    return f"background-color: {colour}; color: {colour};"


def latest_started_index(meetings: list[Meeting], now: datetime) -> int:
    """Indice da etapa mais recente ja iniciada (ou 0 se nenhuma comecou)."""
    started = [
        index
        for index, meeting in enumerate(meetings)
        if meeting.date_start is not None and meeting.date_start <= now
    ]
    return started[-1] if started else 0


def render_sidebar() -> tuple[int | str | None, int]:
    st.sidebar.header("Sessao")
    use_latest = st.sidebar.toggle("Sessao mais recente (latest)", value=False)
    top_n = st.sidebar.slider("Top N voltas", min_value=3, max_value=20, value=10)

    if use_latest:
        return LATEST, top_n

    current_year = datetime.now(UTC).year
    seasons = list(range(current_year, FIRST_SEASON - 1, -1))
    year = st.sidebar.selectbox("Temporada", seasons)

    with st.spinner("Carregando etapas..."):
        meetings = load_meetings(year)
    if not meetings:
        st.sidebar.warning(f"Nenhuma etapa encontrada para {year}.")
        return None, top_n

    meeting = st.sidebar.selectbox(
        "Etapa",
        meetings,
        index=latest_started_index(meetings, datetime.now(UTC)),
        format_func=lambda m: f"{m.meeting_name} ({m.circuit_short_name or '-'})",
    )

    with st.spinner("Carregando sessoes..."):
        sessions = load_sessions(meeting.meeting_key)
    if not sessions:
        st.sidebar.warning("Nenhuma sessao encontrada para esta etapa.")
        return None, top_n

    session = st.sidebar.selectbox(
        "Sessao",
        sessions,
        index=len(sessions) - 1,
        format_func=lambda s: s.session_name,
    )
    return session.session_key, top_n


def render_kpis(overview: SessionOverview) -> None:
    cols = st.columns(4)
    cols[0].metric("Pilotos", len(overview.drivers))
    cols[1].metric("Voltas registradas", overview.total_laps)
    cols[2].metric("Voltas validas", overview.valid_laps)
    cols[3].metric("Media (validas)", format_lap_time(overview.average_lap_duration))


def render_podium_cards(entries: list[FastestLapEntry]) -> None:
    cols = st.columns(min(3, len(entries)))
    for col, entry in zip(cols, entries, strict=False):
        with col, st.container(border=True):
            st.markdown(
                f"<div style='border-left: 6px solid {entry.team_colour}; "
                f"padding-left: 0.6rem'>"
                f"<div style='font-size: 0.85rem; opacity: 0.7'>P{entry.position} "
                f"&middot; {entry.team_name}</div>"
                f"<div style='font-size: 1.15rem; font-weight: 600'>"
                f"{entry.driver_name}</div></div>",
                unsafe_allow_html=True,
            )
            delta = None if entry.position == 1 else f"+{entry.gap_to_fastest:.3f}s"
            st.metric(
                f"Volta {entry.lap_number}",
                format_lap_time(entry.lap_duration),
                delta=delta,
                delta_color="inverse",
            )


def render_gap_chart(entries: list[FastestLapEntry]) -> None:
    figure = go.Figure(
        go.Bar(
            x=[entry.gap_to_fastest for entry in entries],
            y=[entry.name_acronym for entry in entries],
            orientation="h",
            marker={"color": BAR_COLOUR, "cornerradius": 4},
            customdata=[
                [
                    entry.driver_name,
                    entry.team_name,
                    format_lap_time(entry.lap_duration),
                ]
                for entry in entries
            ],
            hovertemplate=(
                "<b>%{customdata[0]}</b> (%{customdata[1]})<br>"
                "Tempo: %{customdata[2]}<br>Gap: +%{x:.3f}s<extra></extra>"
            ),
        )
    )
    figure.update_layout(
        title="Gap para a volta mais rapida (s)",
        height=max(260, 32 * len(entries) + 80),
        bargap=0.45,
        margin={"l": 8, "r": 8, "t": 48, "b": 8},
        yaxis={"autorange": "reversed", "showgrid": False},
        xaxis={
            "ticksuffix": "s",
            "zeroline": True,
            "gridcolor": "rgba(128,128,128,0.18)",
        },
    )
    st.plotly_chart(figure, width="stretch")


def render_top_laps(overview: SessionOverview) -> None:
    entries = overview.top_laps
    if not entries:
        st.info("Nenhuma volta valida registrada para esta sessao.")
        return

    st.subheader(f"Top {len(entries)} voltas mais rapidas")
    render_podium_cards(entries)

    table = top_laps_to_dataframe(entries)
    styled = table.style.map(_team_swatch, subset=["Cor"])
    st.dataframe(
        styled,
        hide_index=True,
        width="stretch",
        column_config={"Cor": st.column_config.TextColumn("", width="small")},
    )
    render_gap_chart(entries)


def main() -> None:
    st.set_page_config(
        page_title="F1 Dashboard", page_icon=":checkered_flag:", layout="wide"
    )
    st.title("F1 Dashboard")
    st.caption("Dados: OpenF1 API (https://openf1.org) - historico a partir de 2023")

    try:
        session_key, top_n = render_sidebar()
        if session_key is None:
            st.info("Selecione uma etapa e uma sessao na barra lateral.")
            return

        with st.spinner("Carregando voltas e pilotos..."):
            overview = load_overview(session_key, top_n)
    except OpenF1Error as exc:
        logger.error("Erro ao consultar a OpenF1: %s", exc)
        st.error(f"Nao foi possivel consultar a OpenF1: {exc}")
        return

    render_kpis(overview)
    render_top_laps(overview)


if __name__ == "__main__":
    main()
