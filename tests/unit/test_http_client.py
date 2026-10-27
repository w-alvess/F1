from collections.abc import Callable

import httpx
import pytest

from f1.ingestion.http_client import Filter, HttpClient, OpenF1Error, build_query

BASE_URL = "https://api.test/v1"

Handler = Callable[[httpx.Request], httpx.Response]


def make_client(handler: Handler, sleeps: list[float] | None = None) -> HttpClient:
    recorded = sleeps if sleeps is not None else []
    return HttpClient(
        base_url=BASE_URL,
        transport=httpx.MockTransport(handler),
        sleep=recorded.append,
    )


def test_build_query_keeps_operators_and_skips_none() -> None:
    query = build_query(
        {"session_key": 9161, "driver_number": None, "csv": False},
        [Filter("speed", ">=", 315), Filter("lap_duration", "<", 90.5)],
    )

    assert query == "session_key=9161&csv=false&speed>=315&lap_duration<90.5"


def test_build_query_encodes_values() -> None:
    query = build_query({"session_name": "Sprint Qualifying"})

    assert query == "session_name=Sprint%20Qualifying"


def test_get_returns_payload_and_sends_query() -> None:
    seen: list[httpx.URL] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request.url)
        return httpx.Response(200, json=[{"driver_number": 1}])

    result = make_client(handler).get("drivers", params={"session_key": "latest"})

    assert result == [{"driver_number": 1}]
    assert seen[0].path == "/v1/drivers"
    assert seen[0].params["session_key"] == "latest"


def test_get_without_params() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.query == b""
        return httpx.Response(200, json=[])

    assert make_client(handler).get("/meetings") == []


def test_retries_on_5xx_then_succeeds() -> None:
    responses = iter(
        [httpx.Response(503), httpx.Response(502), httpx.Response(200, json=[])]
    )
    sleeps: list[float] = []

    client = make_client(lambda _: next(responses), sleeps)

    assert client.get("laps") == []
    assert sleeps == [0.5, 1.0]


def test_retries_on_timeout_then_succeeds() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        if calls["count"] == 1:
            raise httpx.ReadTimeout("timeout", request=request)
        return httpx.Response(200, json=[{"ok": True}])

    assert make_client(handler).get("laps") == [{"ok": True}]
    assert calls["count"] == 2


def test_raises_after_exhausting_retries() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        raise httpx.ConnectError("boom", request=request)

    with pytest.raises(OpenF1Error, match="ConnectError"):
        make_client(handler).get("laps")
    assert calls["count"] == 3


def test_retries_on_rate_limit() -> None:
    responses = iter([httpx.Response(429), httpx.Response(200, json=[])])

    assert make_client(lambda _: next(responses)).get("laps") == []


def test_404_means_no_results() -> None:
    client = make_client(
        lambda _: httpx.Response(404, json={"detail": "No results found."})
    )

    assert client.get("laps") == []


def test_4xx_raises_without_retry() -> None:
    calls = {"count": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["count"] += 1
        return httpx.Response(422, text="bad filter")

    with pytest.raises(OpenF1Error, match="422"):
        make_client(handler).get("laps")
    assert calls["count"] == 1


def test_non_json_response_raises() -> None:
    client = make_client(lambda _: httpx.Response(200, text="<html>"))

    with pytest.raises(OpenF1Error, match="nao-JSON"):
        client.get("laps")


def test_non_list_payload_raises() -> None:
    client = make_client(lambda _: httpx.Response(200, json={"detail": "x"}))

    with pytest.raises(OpenF1Error, match="esperado lista"):
        client.get("laps")


def test_invalid_max_retries() -> None:
    with pytest.raises(ValueError):
        HttpClient(base_url=BASE_URL, max_retries=0)


def test_close() -> None:
    client = make_client(lambda _: httpx.Response(200, json=[]))
    client.close()

    with pytest.raises(RuntimeError):
        client.get("laps")
