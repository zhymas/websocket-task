from dataclasses import dataclass
from datetime import datetime

from fastapi.websockets import WebSocket


@dataclass(slots=True)
class ConnectedClient:
    id: str
    websocket: WebSocket
    connected_at: datetime