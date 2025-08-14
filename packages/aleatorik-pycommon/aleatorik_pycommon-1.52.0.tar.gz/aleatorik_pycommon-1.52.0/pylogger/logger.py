import contextvars
import inspect
import json
from typing import Any
from urllib.parse import urlparse

import loguru
import requests
from loguru import logger
from requests.models import Request, Response

from pylogger.config import get_settings
from pylogger.model import LogEntry
from pylogger.utils.helper import decode_base64_string, get_header_with_fallback
from pylogger.utils.template import LogCategory, LogLevel

# Configuration from service environment variables
FLUENTBIT_URL: str | None = get_settings().FLUENTBIT_URL
COMPONENT_NAME: str | None = get_settings().COMPONENT_NAME
SYSTEM_NAME: str | None = get_settings().SYSTEM_NAME

# Stores log context for each request
log_context_var: contextvars.ContextVar = contextvars.ContextVar(
    "log_context", default=None
)


class PyLogger:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        """Ensure only one instance of PyLogger is created."""
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
            cls._instance.setup_logger()
        return cls._instance

    def __init__(self):
        self.setup_logger()

    def setup_logger(self):
        """Configures logger."""
        logger.remove()
        logger.add(self.custom_sink, format="{message}", serialize=True, level="INFO")

    def bind_base_properties(self, request):
        """Initializes new log context and bind base properties"""
        log_entry: dict[str, Any] = {}

        base_info: dict[str, str] = {
            "component": COMPONENT_NAME.lower() if COMPONENT_NAME else "unknown",
            "system": SYSTEM_NAME.lower() if SYSTEM_NAME else "unknown",
        }
        log_entry.update(base_info)

        required_fields: dict[str, Any] = self._extract_request_fields(request)
        if required_fields:
            log_entry.update(required_fields)

        self.add_to_log(log_entry)
        return None

    def bind_request_properties(self, request: Request) -> dict[str, Any]:
        """Initializes new log context and bind base properties"""
        required_fields: dict[str, Any] = self._extract_request_fields(request)
        if required_fields:
            self.add_to_log(required_fields)
        return required_fields

    def bind_base_info(self):
        """Initializes basic log context with component and system information"""
        base_info: dict[str, str] = {
            "component": COMPONENT_NAME.lower() if COMPONENT_NAME else "unknown",
            "system": SYSTEM_NAME.lower() if SYSTEM_NAME else "unknown",
        }
        self.add_to_log(base_info)

    def add_to_log(self, data: dict[str, Any]) -> None:
        curr_context: loguru.Logger | None = log_context_var.get()

        if curr_context:
            new_context: loguru.Logger = curr_context.bind(**data)
        else:
            new_context: loguru.Logger = logger.bind(**data)

        log_context_var.set(new_context)

    def send_log(self, level: LogLevel, category: LogCategory, message: str) -> None:
        """Extracts logCategory and sourceContext before sending logs to Fluent Bit"""

        curr_context: loguru.Logger | None = log_context_var.get()
        if not curr_context:
            # Initialize basic log context if none exists
            self.bind_base_info()
            curr_context: loguru.Logger | None = log_context_var.get()

        caller = inspect.stack()[1]  # Get the caller's stack frame
        module_name = caller.filename

        data: dict[str, Any] = {
            "logCategory": category.lower(),
            "sourceContext": module_name,
        }
        self.add_to_log(data)

        curr_context: loguru.Logger | None = log_context_var.get()
        # loguru expects upper case log level
        curr_context.log(
            level.upper(),
            self._format_message(level.upper(), category.upper(), message),
        )  # Calls custom sink

    def custom_sink(self, message) -> None:
        """Sends logs to Fluent Bit"""
        try:
            if FLUENTBIT_URL is None:
                print("Fluentbit URL is not set. Skip logging.")
                return

            log_entry = self._parse_before_send(message.record)
            if log_entry == "{}":
                print("Log entry rejected. Log will not be sent.")
                return
            response: Response = requests.post(
                FLUENTBIT_URL,
                data=log_entry,
                headers={"Content-Type": "application/json"},
                timeout=5.0,
            )
            if response.status_code != 201:
                print(f"Failed to send log: {response.status_code} {response.text}")

        except Exception as e:
            print(
                "Error while sending log: %s at %s at line %s",
                str(e),
                message.record.get("name"),
                message.record.get("line"),
            )

    def _parse_before_send(self, record) -> str:
        # Initialize the log entry with required fields using aliases
        print("Record:", record)
        log_entry: dict[str, Any] = {
            "level": record["level"].name,
            "message": record["message"],
            "timestamp": record["time"].isoformat() if "time" in record else "Unknown",
            "component": record["extra"].get("component"),
            "system": record["extra"].get("system"),
            "method": record["extra"].get("method"),
            "traceId": record["extra"].get("traceId"),
            "tenantInfo": record["extra"].get("tenantInfo"),
            "requestPath": record["extra"].get("requestPath"),
            "logCategory": record["extra"].get("logCategory"),
            "userId": record["extra"].get("userId"),
            "properties": {},
        }

        # Populate properties field
        common_fields: dict[str, Any] = {
            "threadId": record["thread"].id,
            "processId": record["process"].id,
            "userAgent": record["extra"].get("userAgent"),
            "sourceContext": record["extra"].get("sourceContext"),
        }
        log_entry["properties"].update(common_fields)

        # Dynamically add service-specific fields from other source code
        for key, value in record.get("extra", {}).items():
            if value is not None and key not in common_fields and key not in log_entry:
                camel_case_key = self._to_camel_case(key)
                log_entry["properties"][camel_case_key] = value

        # Final validation with LogEntry model
        try:
            # Validate using all available fields from log_entry
            validated_entry: LogEntry = LogEntry(**log_entry)
            # Convert back to dict for JSON serialization
            final_log_entry: dict[str, Any] = validated_entry.model_dump(
                exclude_none=True
            )
        except Exception as e:
            # Print detailed error message and reject the log entry
            print(
                f"LogEntry validation failed for {COMPONENT_NAME} and will not be sent: {e}"
            )
            # Return empty JSON to prevent sending invalid log entries
            return "{}"
        print("Parsed log entry:", final_log_entry)
        return json.dumps(final_log_entry)

    def _format_message(self, level: str, category: str, message: str) -> str:
        return f"[{level}] [{category}] - {message}"

    def _to_camel_case(self, unformatted_str: str) -> str:
        """Convert snake_case, kebab-case, or PascalCase to camelCase"""
        if not unformatted_str:
            return unformatted_str

        # Handle kebab-case by replacing hyphens with underscores
        unformatted_str: str = unformatted_str.replace("-", "_")

        # Split on underscores and handle each component
        components: list[str] = unformatted_str.split("_")

        # If there's only one component, check if it's PascalCase and convert
        if len(components) == 1:
            # Convert PascalCase to camelCase (first letter lowercase)
            return components[0][0].lower() + components[0][1:] if components[0] else ""

        # For multiple components, first component stays lowercase, rest become title case
        return components[0].lower() + "".join(word.title() for word in components[1:])

    def _extract_request_fields(self, request: Request) -> dict[str, Any]:
        """Extracts fields from request and headers"""
        headers: dict[str, str] = request.headers
        required_fields: dict[str, Any] = {}

        # Construct tenantInfo field from headers with fallback options
        tenant_id: str | None = decode_base64_string(
            get_header_with_fallback(headers, ["tenant-id", "tenant-Id", "Tenant-Id"])
        )
        tenant_name: str | None = decode_base64_string(
            get_header_with_fallback(
                headers, ["tenant-name", "tenant-Name", "Tenant-Name"]
            )
        )
        project_name: str | None = decode_base64_string(
            get_header_with_fallback(
                headers, ["project-name", "project-Name", "Project-Name"]
            )
        )
        project_id: str | None = decode_base64_string(
            get_header_with_fallback(headers, ["projectID", "ProjectID"])
        )

        # Leave out None values and fields
        tenant_info: dict[str, Any] = {}
        if project_id:
            tenant_info["projectId"] = project_id
        if project_name:
            tenant_info["projectName"] = project_name
        if tenant_id:
            tenant_info["tenantId"] = tenant_id
        if tenant_name:
            tenant_info["tenantName"] = tenant_name

        if tenant_info:
            required_fields["tenantInfo"] = tenant_info

        # Extract the rest from request or headers
        field_mappings = {
            "traceId": headers.get("TraceID"),
            "userId": headers.get("UserID"),
            "userAgent": headers.get("User-Agent"),
            "requestPath": urlparse(str(request.url)).path,
            "method": request.method,
        }

        # Add only non-None values to required_fields
        required_fields.update({k: v for k, v in field_mappings.items() if v})

        return required_fields


# Initialize the global logger instance
logger_instance = PyLogger()
