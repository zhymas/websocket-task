import uvicorn

from src.services.websocket.connection_manager import ConnectionManager, connection_manager
from src.services.websocket.notifications import NotificationBroadcaster
from src.services.websocket.shutdown import GracefulShutdownGuard
from src.services.websocket.shutdown_signal import SignalHandler


def get_connection_manager() -> ConnectionManager:
    return connection_manager


def get_notification_broadcaster() -> NotificationBroadcaster:
    connection_manager = get_connection_manager()

    return NotificationBroadcaster(
        manager=connection_manager
    )    


def get_shutdown_guard() -> GracefulShutdownGuard:
    connection_manager = get_connection_manager()

    return GracefulShutdownGuard(
        manager=connection_manager
    )    


def get_signal_handler(server: uvicorn.Server) -> SignalHandler:
    connection_manager = get_connection_manager()
    graceful_shutdown_guard = get_shutdown_guard()

    return SignalHandler(
        server=server,
        manager=connection_manager,
        graceful_shutdown_guard=graceful_shutdown_guard
    )    