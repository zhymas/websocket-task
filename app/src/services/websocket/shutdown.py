from __future__ import annotations
import asyncio
import os
from datetime import datetime, timedelta, timezone

from src.services.websocket.interfaces import IConnectionManager
from src.services.websocket.interfaces import IGracefulShutdownGuard
from src.logs import logger


class GracefulShutdownGuard(IGracefulShutdownGuard):

    def __init__(
        self,
        manager: IConnectionManager,
        max_wait_minutes: int = 30,
        poll_interval_seconds: int = 5,
    ) -> None:
        self._manager = manager
        self._max_wait = timedelta(minutes=max_wait_minutes)
        self._poll_interval = poll_interval_seconds

    async def wait_for_shutdown(self) -> None:
        start = datetime.now(timezone.utc)
        deadline = start + self._max_wait
        logger.info(
            f"Shutdown signal received (pid={os.getpid()}). Waiting for WebSocket clients to drain."
        )
        while True:
            active = self._manager.active_connection_count
            logger.info(f"Active connections: {active}")
            now = datetime.now(timezone.utc)
            remaining = max((deadline - now).total_seconds(), 0)
            if active == 0:
                logger.info(
                    f"All WebSocket connections drained after {((now - start).total_seconds())} seconds."
                )
                break
            if remaining <= 0:
                logger.warning(
                    f"Shutdown deadline reached with {active} connection(s) still open. "
                    f"Force closing remaining clients."
                )
                await self._manager.force_disconnect_all()
                break
            logger.info(
                f"Shutdown paused — {active} connection(s) active; {remaining} seconds remaining."
            )
            await asyncio.sleep(min(self._poll_interval, remaining))

