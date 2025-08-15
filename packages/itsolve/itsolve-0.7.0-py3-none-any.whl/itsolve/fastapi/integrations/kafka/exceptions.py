from typing import Any

from fastapi import status
from src.itsolve.fastapi.core import GlobalAppError


class KafkaSendMessageAppException(GlobalAppError):
    STATUS_CODE: int = status.HTTP_400_BAD_REQUEST
    ERROR: str = "kafka_send_message_error"
    DESCRIPTION: str | None = "Failed to send message to Kafka"
    CTX_EXAMPLE_STRUCTURE: dict[str, Any] = {
        "topic": "string",
        "value": "dict[Any, Any] | str | list[Any] | int",
        "key": "str | int | None",
        "partition": "int | None",
        "timestamp_ms": "int | None",
        "headers": "list[tuple[str, bytes]] | None",
    }
