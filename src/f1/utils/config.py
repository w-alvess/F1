import os
from dataclasses import dataclass

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://api.openf1.org/v1"
DEFAULT_TIMEOUT = 10.0
VALID_ENVIRONMENTS = ("development", "staging", "production")


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout: float
    environment: str
    log_level: str


def load_settings() -> Settings:
    load_dotenv()

    environment = os.getenv("ENVIRONMENT", "development").lower()
    if environment not in VALID_ENVIRONMENTS:
        raise ValueError(
            f"ENVIRONMENT invalido: {environment!r}. "
            f"Use um de {', '.join(VALID_ENVIRONMENTS)}."
        )

    timeout_raw = os.getenv("OPENF1_TIMEOUT", str(DEFAULT_TIMEOUT))
    try:
        timeout = float(timeout_raw)
    except ValueError as exc:
        raise ValueError(f"OPENF1_TIMEOUT invalido: {timeout_raw!r}") from exc
    if timeout <= 0:
        raise ValueError("OPENF1_TIMEOUT deve ser maior que zero")

    return Settings(
        base_url=os.getenv("OPENF1_BASE_URL", DEFAULT_BASE_URL).rstrip("/"),
        timeout=timeout,
        environment=environment,
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
    )
