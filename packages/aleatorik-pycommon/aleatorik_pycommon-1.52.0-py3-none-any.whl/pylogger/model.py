from typing import Any

from pydantic import BaseModel, Field


class LogEntry(BaseModel):
    level: str
    message: str
    logCategory: str | None = None  # noqa: N815
    component: str | None = None
    system: str | None = None
    method: str | None = None
    traceId: str | None = None  # noqa: N815
    tenantInfo: dict[str, Any] | None = None  # noqa: N815
    requestPath: str | None = None  # noqa: N815
    timestamp: str | None = None
    userId: str | None = None  # noqa: N815
    properties: dict[str, Any] | None = Field(
        None, description="Additional custom properties or contextual data."
    )
