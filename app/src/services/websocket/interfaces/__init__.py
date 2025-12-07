from abc import ABC, abstractmethod
from typing import Tuple, Any, Callable, Awaitable

from fastapi import WebSocket

from src.dataclasses.connected_clients import ConnectedClient


class IConnectionManager(ABC):
    @abstractmethod
    async def connect(self, websocket: WebSocket) -> ConnectedClient: ...

    @abstractmethod
    async def disconnect(self, connection_id: str) -> None: ...

    @property
    @abstractmethod
    def active_connection_count(self) -> int: ...

    @property
    @abstractmethod
    def connection_ids(self) -> Tuple[str, ...]: ...

    @abstractmethod
    async def broadcast_text(self, message: str) -> int: ...

    @abstractmethod
    async def broadcast_json(self, payload: Any) -> int: ...

    @abstractmethod
    async def force_disconnect_all(
        self,
        close_code: int = 1012,
        reason: str | None = "Server shutting down",
    ) -> int: ...

    @abstractmethod
    async def _broadcast(
        self,
        sender: Callable[[WebSocket], Awaitable[None]],
    ) -> int: ...


class INotificationBroadcaster(ABC):
    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def _run(self) -> None: ...


class IGracefulShutdownGuard(ABC):
    @abstractmethod
    async def wait_for_shutdown(self) -> None: ...