from collections.abc import Mapping
from typing import Any

from pydantic import BaseModel, ValidationError

from f1.domain.models import Driver, Lap, Meeting, Session
from f1.domain.repositories import (
    DriverRepository,
    LapRepository,
    MeetingKey,
    MeetingRepository,
    SessionKey,
    SessionRepository,
)
from f1.ingestion.http_client import HttpClient, QueryValue
from f1.utils.logger import get_logger

logger = get_logger(__name__)


def fetch_models[ModelT: BaseModel](
    http_client: HttpClient,
    endpoint: str,
    model: type[ModelT],
    params: Mapping[str, QueryValue | None],
) -> list[ModelT]:
    """Busca um endpoint e valida cada item, ignorando (e logando) os invalidos."""
    items: list[ModelT] = []
    invalid = 0
    for raw in http_client.get(endpoint, params=params):
        item = _validate(model, raw)
        if item is None:
            invalid += 1
        else:
            items.append(item)

    if invalid:
        logger.warning(
            "%s: %d item(ns) invalido(s) ignorado(s) de %d",
            endpoint,
            invalid,
            invalid + len(items),
        )
    return items


def _validate[ModelT: BaseModel](
    model: type[ModelT], raw: dict[str, Any]
) -> ModelT | None:
    try:
        return model.model_validate(raw)
    except ValidationError as exc:
        logger.debug("Payload invalido para %s: %s", model.__name__, exc)
        return None


class OpenF1MeetingRepository(MeetingRepository):
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def list(self, year: int, country: str | None = None) -> list[Meeting]:
        params = {"year": year, "country_name": country}
        return fetch_models(self._http, "meetings", Meeting, params)


class OpenF1SessionRepository(SessionRepository):
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def list(self, meeting_key: MeetingKey) -> list[Session]:
        params = {"meeting_key": meeting_key}
        return fetch_models(self._http, "sessions", Session, params)


class OpenF1DriverRepository(DriverRepository):
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def list(self, session_key: SessionKey) -> list[Driver]:
        params = {"session_key": session_key}
        return fetch_models(self._http, "drivers", Driver, params)


class OpenF1LapRepository(LapRepository):
    def __init__(self, http_client: HttpClient) -> None:
        self._http = http_client

    def list(
        self, session_key: SessionKey, driver_number: int | None = None
    ) -> list[Lap]:
        params = {"session_key": session_key, "driver_number": driver_number}
        return fetch_models(self._http, "laps", Lap, params)
