from __future__ import annotations
from typing import Self
from uuid import uuid4
import asyncio
import os
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, Tuple

from fastapi import WebSocket

from src.dataclasses.connected_clients import ConnectedClient
from src.services.websocket.interfaces import IConnectionManager
from src.logs import logger


class ConnectionManager(IConnectionManager):
    """Tracks active WebSocket connections and supports broadcasting."""

    _instance: Self | None = None

    def __new__(cls, *args: Any, **kwargs: Any) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        self._clients: Dict[str, ConnectedClient] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> ConnectedClient:
        await websocket.accept()
        client = ConnectedClient(
            id=str(uuid4()),
            websocket=websocket,
            connected_at=datetime.now(timezone.utc),
        )
        async with self._lock:
            self._clients[client.id] = client
            active = len(self._clients)
        logger.info(
            f"Client {client.id} connected (pid={os.getpid()})."
            f" Active connections={active}"
        )
        return client

    async def disconnect(self, connection_id: str) -> None:
        async with self._lock:
            client = self._clients.pop(connection_id, None)
            active = len(self._clients)
        if client:
            try:
                await client.websocket.close()
            except RuntimeError:
                # Already closed by the client.
                pass
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.debug(f"Error while closing websocket {connection_id}: {exc}")
            logger.info(
                f"Client {connection_id} disconnected (pid={os.getpid()})."
                f" Active connections={active}"
            )

    @property
    def active_connection_count(self) -> int:
        return len(self._clients)

    @property
    def connection_ids(self) -> Tuple[str, ...]:
        return tuple(self._clients.keys())

    async def broadcast_text(self, message: str) -> int:
        return await self._broadcast(lambda ws: ws.send_text(message))

    async def broadcast_json(self, payload: Any) -> int:
        return await self._broadcast(lambda ws: ws.send_json(payload))

    async def force_disconnect_all(
        self,
        close_code: int = 1012,
        reason: str | None = "Server shutting down",
    ) -> int:
        async with self._lock:
            clients = list(self._clients.items())
            self._clients.clear()
        for connection_id, client in clients:
            try:
                await client.websocket.close(code=close_code, reason=reason)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.debug(
                    f"Error while force closing websocket {connection_id}: {exc}"
                )
        logger.info(
            f"Force closed {len(clients)} connection(s) (pid={os.getpid()})."
        )
        return len(clients)

    async def _broadcast(
        self,
        sender: Callable[[WebSocket], Awaitable[None]],
    ) -> int:
        async with self._lock:
            clients = list(self._clients.items())
        stale: list[str] = []
        for connection_id, client in clients:
            try:
                await sender(client.websocket)
            except Exception as exc:
                logger.warning(
                    f"Dropping connection {connection_id} after broadcast failure: {exc}"
                )
                stale.append(connection_id)
        for connection_id in stale:
            await self.disconnect(connection_id)
        return len(clients) - len(stale)


connection_manager = ConnectionManager()