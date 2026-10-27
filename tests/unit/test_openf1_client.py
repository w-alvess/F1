import logging
from typing import Any

import httpx
import pytest

from f1.ingestion.http_client import HttpClient
from f1.ingestion.openf1_client import (
    OpenF1DriverRepository,
    OpenF1LapRepository,
    OpenF1MeetingRepository,
    OpenF1SessionRepository,
)


class FakeApi:
    """Transporte fake que registra as queries e devolve payloads por endpoint."""

    def __init__(self, payloads: dict[str, list[dict[str, Any]]]) -> None:
        self.payloads = payloads
        self.requests: list[httpx.URL] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request.url)
        endpoint = request.url.path.rsplit("/", 1)[-1]
        return httpx.Response(200, json=self.payloads.get(endpoint, []))

    def client(self) -> HttpClient:
        return HttpClient(
            base_url="https://api.test/v1", transport=httpx.MockTransport(self)
        )


def test_meeting_repository(meeting_payload: dict[str, Any]) -> None:
    api = FakeApi({"meetings": [meeting_payload]})

    meetings = OpenF1MeetingRepository(api.client()).list(2023, country="Singapore")

    assert [m.meeting_key for m in meetings] == [1219]
    assert dict(api.requests[0].params) == {"year": "2023", "country_name": "Singapore"}


def test_meeting_repository_without_country(meeting_payload: dict[str, Any]) -> None:
    api = FakeApi({"meetings": [meeting_payload]})

    OpenF1MeetingRepository(api.client()).list(2023)

    assert dict(api.requests[0].params) == {"year": "2023"}


def test_session_repository(session_payload: dict[str, Any]) -> None:
    api = FakeApi({"sessions": [session_payload]})

    sessions = OpenF1SessionRepository(api.client()).list(1219)

    assert sessions[0].session_name == "Race"
    assert dict(api.requests[0].params) == {"meeting_key": "1219"}


def test_driver_repository(driver_payload: dict[str, Any]) -> None:
    api = FakeApi({"drivers": [driver_payload]})

    drivers = OpenF1DriverRepository(api.client()).list("latest")

    assert drivers[0].name_acronym == "VER"
    assert dict(api.requests[0].params) == {"session_key": "latest"}


def test_lap_repository_with_driver_filter(lap_payload: dict[str, Any]) -> None:
    api = FakeApi({"laps": [lap_payload]})

    laps = OpenF1LapRepository(api.client()).list(9161, driver_number=63)

    assert laps[0].lap_number == 8
    assert dict(api.requests[0].params) == {
        "session_key": "9161",
        "driver_number": "63",
    }


def test_invalid_items_are_skipped_and_logged(
    lap_payload: dict[str, Any], caplog: pytest.LogCaptureFixture
) -> None:
    broken = {k: v for k, v in lap_payload.items() if k != "lap_number"}
    api = FakeApi({"laps": [lap_payload, broken, {"driver_number": "abc"}]})
    logger_name = "f1.ingestion.openf1_client"
    logging.getLogger(logger_name).propagate = True
    try:
        with caplog.at_level(logging.WARNING, logger=logger_name):
            laps = OpenF1LapRepository(api.client()).list(9161)
    finally:
        logging.getLogger(logger_name).propagate = False

    assert len(laps) == 1
    assert "2 item(ns) invalido(s)" in caplog.text
