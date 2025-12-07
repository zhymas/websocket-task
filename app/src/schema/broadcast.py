from pydantic import BaseModel, Field
from typing import Any


class BroadcastPayload(BaseModel):
    message: str = Field(..., min_length=1, max_length=2048)
    sender: str | None = Field(
        default=None, description="Optional identifier for the broadcaster."
    )
    metadata: dict[str, Any] | None = Field(
        default=None, description="Optional structured payload."
    )