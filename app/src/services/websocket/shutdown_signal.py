import asyncio
from typing import List

import uvicorn
from uvicorn.server import HANDLED_SIGNALS

from src.services.websocket.interfaces import IConnectionManager, IGracefulShutdownGuard
from src.logs import logger


class SignalHandler:
    def __init__(
        self,
        server: uvicorn.Server,
        manager: IConnectionManager,
        graceful_shutdown_guard: IGracefulShutdownGuard,
        queue: List = []
    ):
        self.queue = queue
        self.server = server
        self.manager = manager
        self.graceful_shutdown_guard = graceful_shutdown_guard

    async def handle_exit(self) -> None:
        logger.info("Signal intercepted")

        while len(self.queue) > 0:
            logger.info("Waiting for the queue to be consumed")
            await asyncio.sleep(5)

        logger.info("Queue is empty. Exiting.")

        logger.info("Force disconnecting all connections")
        await self.graceful_shutdown_guard.wait_for_shutdown()

        self.server.should_exit = True

    def signal_handler(self) -> None:
        asyncio.create_task(self.handle_exit())

    def register_signal_handler(self) -> None:
        logger.debug("Registering signal handler")

        loop = asyncio.get_running_loop()
        for sig in HANDLED_SIGNALS:
            loop.add_signal_handler(sig, self.signal_handler)

        logger.debug("Signal handler registered")