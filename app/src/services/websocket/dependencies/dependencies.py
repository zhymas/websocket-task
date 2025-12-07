from src.services.websocket.connection_manager import ConnectionManager, connection_manager
from src.services.websocket.notifications import NotificationBroadcaster
from src.services.websocket.shutdown import GracefulShutdownGuard


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