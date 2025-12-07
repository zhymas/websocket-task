from __future__ import annotations
import asyncio
import os
from datetime import datetime, timezone

from src.services.websocket.interfaces import IConnectionManager
from src.services.websocket.interfaces import INotificationBroadcaster
from src.logs import logger 


class NotificationBroadcaster(INotificationBroadcaster):

    def __init__(self, manager: IConnectionManager, interval_seconds: int = 10) -> None:
        self._manager = manager
        self._interval = interval_seconds
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(
            self._run(),
            name="notification-broadcast-loop",
        )
        logger.info(f"Notification broadcaster started (pid={os.getpid()}).")

    async def stop(self) -> None:
        self._stop_event.set()
        task = self._task
        if task:
            await task
        self._task = None
        logger.info(f"Notification broadcaster stopped (pid={os.getpid()}).")

    async def _run(self) -> None:
        try:
            while not self._stop_event.is_set():
                if self._manager.active_connection_count:
                    payload = {
                        "event": "test-notification",
                        "message": "Hello from the server!",
                        "sent_at": datetime.now(timezone.utc).isoformat(),
                        "active_connections": self._manager.active_connection_count,
                    }
                    await self._manager.broadcast_json(payload)
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(), timeout=self._interval
                    )
                except asyncio.TimeoutError:
                    continue
        finally:
            self._task = None