from enum import Enum


class LogLevel(str, Enum):
    trace: str = "trace"
    debug: str = "debug"
    info: str = "info"
    warning: str = "warning"
    error: str = "error"
    critical: str = "critical"

    @classmethod
    def _missing_(cls, value):
        return cls(value.lower())


class LogCategory(str, Enum):
    request = "request"
    response = "response"
    service = "service"
    outbound = "outbound"
    excel = "excel"
    access = "access"
    query = "query"
    engine = "engine"
    authorize = "authorize"

    @classmethod
    def _missing_(cls, value):
        return cls(value.lower())
