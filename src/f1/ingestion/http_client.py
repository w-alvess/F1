import time
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal
from urllib.parse import quote

import httpx

from f1.utils.logger import get_logger

logger = get_logger(__name__)

DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_FACTOR = 0.5
RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

Operator = Literal["=", ">=", "<=", ">", "<"]
QueryValue = str | int | float | bool


class OpenF1Error(Exception):
    """Falha definitiva ao consultar a OpenF1 (apos esgotar retries)."""


@dataclass(frozen=True)
class Filter:
    """Filtro de query string no formato OpenF1, ex.: Filter("speed", ">=", 300)."""

    field: str
    operator: Operator
    value: QueryValue

    def render(self) -> str:
        return f"{quote(self.field)}{self.operator}{quote(_stringify(self.value))}"


def build_query(
    params: Mapping[str, QueryValue | None] | None = None,
    filters: Sequence[Filter] = (),
) -> str:
    """Monta a query string preservando os operadores de comparacao da OpenF1.

    O httpx codificaria `>=` dentro da chave; por isso a query e montada aqui.
    Parametros com valor `None` sao omitidos.
    """
    equalities = [
        Filter(key, "=", value)
        for key, value in (params or {}).items()
        if value is not None
    ]
    return "&".join(item.render() for item in [*equalities, *filters])


class HttpClient:
    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
        transport: httpx.BaseTransport | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        if max_retries < 1:
            raise ValueError("max_retries deve ser >= 1")
        self._client = httpx.Client(
            base_url=base_url.rstrip("/") + "/",
            timeout=timeout,
            transport=transport,
            headers={"Accept": "application/json"},
        )
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._sleep = sleep

    def get(
        self,
        path: str,
        params: Mapping[str, QueryValue | None] | None = None,
        filters: Sequence[Filter] = (),
    ) -> list[dict[str, Any]]:
        query = build_query(params, filters)
        url = f"{path.lstrip('/')}?{query}" if query else path.lstrip("/")

        for attempt in range(1, self._max_retries + 1):
            try:
                response = self._client.get(url)
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                self._handle_retry(url, attempt, f"{type(exc).__name__}: {exc}")
                continue

            if response.status_code in RETRYABLE_STATUS_CODES:
                self._handle_retry(url, attempt, f"HTTP {response.status_code}")
                continue

            return self._parse(url, response)

        raise OpenF1Error(f"Falha inesperada em {url}")  # pragma: no cover

    def close(self) -> None:
        self._client.close()

    def _handle_retry(self, url: str, attempt: int, reason: str) -> None:
        if attempt >= self._max_retries:
            logger.error(
                "Falha definitiva em %s apos %d tentativas: %s", url, attempt, reason
            )
            raise OpenF1Error(f"Falha ao consultar {url}: {reason}")
        delay = self._backoff_factor * (2 ** (attempt - 1))
        logger.warning(
            "Tentativa %d/%d falhou em %s (%s); nova tentativa em %.2fs",
            attempt,
            self._max_retries,
            url,
            reason,
            delay,
        )
        self._sleep(delay)

    @staticmethod
    def _parse(url: str, response: httpx.Response) -> list[dict[str, Any]]:
        # A OpenF1 responde 404 quando o filtro nao encontra registros.
        if response.status_code == 404:
            logger.info("Nenhum resultado para %s", url)
            return []
        if response.is_error:
            raise OpenF1Error(f"HTTP {response.status_code} em {url}: {response.text}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise OpenF1Error(f"Resposta nao-JSON em {url}") from exc

        if not isinstance(payload, list):
            raise OpenF1Error(f"Resposta inesperada em {url}: esperado lista")
        return payload


def _stringify(value: QueryValue) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    return str(value)
