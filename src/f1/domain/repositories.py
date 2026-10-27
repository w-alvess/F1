from abc import ABC, abstractmethod

from f1.domain.models import Driver, Lap, Meeting, Session

# A OpenF1 aceita a chave literal "latest" alem dos identificadores numericos.
SessionKey = int | str
MeetingKey = int | str


class MeetingRepository(ABC):
    @abstractmethod
    def list(self, year: int, country: str | None = None) -> list[Meeting]: ...


class SessionRepository(ABC):
    @abstractmethod
    def list(self, meeting_key: MeetingKey) -> list[Session]: ...


class DriverRepository(ABC):
    @abstractmethod
    def list(self, session_key: SessionKey) -> list[Driver]: ...


class LapRepository(ABC):
    @abstractmethod
    def list(
        self, session_key: SessionKey, driver_number: int | None = None
    ) -> list[Lap]: ...
