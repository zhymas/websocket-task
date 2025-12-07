from dataclasses import dataclass
from fastapi.websockets import WebSocket
from datetime import datetime


@dataclass(slots=True)
class ConnectedClient:
    id: str
    websocket: WebSocket
    connected_at: datetime