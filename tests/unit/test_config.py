import pytest

from f1.utils.config import DEFAULT_BASE_URL, load_settings
from f1.utils.logger import get_logger

ENV_VARS = ("OPENF1_BASE_URL", "OPENF1_TIMEOUT", "ENVIRONMENT", "LOG_LEVEL")


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for var in ENV_VARS:
        monkeypatch.delenv(var, raising=False)
    # Isola os testes de um .env local do desenvolvedor.
    monkeypatch.setattr("f1.utils.config.load_dotenv", lambda: False)


def test_defaults() -> None:
    settings = load_settings()

    assert settings.base_url == DEFAULT_BASE_URL
    assert settings.timeout == 10.0
    assert settings.environment == "development"
    assert settings.log_level == "INFO"


def test_reads_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OPENF1_BASE_URL", "https://example.org/v1/")
    monkeypatch.setenv("OPENF1_TIMEOUT", "2.5")
    monkeypatch.setenv("ENVIRONMENT", "Production")
    monkeypatch.setenv("LOG_LEVEL", "debug")

    settings = load_settings()

    assert settings.base_url == "https://example.org/v1"
    assert settings.timeout == 2.5
    assert settings.environment == "production"
    assert settings.log_level == "DEBUG"


@pytest.mark.parametrize(
    ("var", "value"),
    [("ENVIRONMENT", "qa"), ("OPENF1_TIMEOUT", "abc"), ("OPENF1_TIMEOUT", "0")],
)
def test_invalid_values_raise(
    monkeypatch: pytest.MonkeyPatch, var: str, value: str
) -> None:
    monkeypatch.setenv(var, value)

    with pytest.raises(ValueError):
        load_settings()


def test_get_logger_is_idempotent() -> None:
    logger = get_logger("f1.tests.logger")

    assert get_logger("f1.tests.logger") is logger
    assert len(logger.handlers) == 1
