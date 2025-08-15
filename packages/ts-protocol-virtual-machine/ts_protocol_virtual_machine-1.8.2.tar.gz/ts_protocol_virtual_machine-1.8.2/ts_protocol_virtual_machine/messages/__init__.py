from dataclasses import dataclass
from enum import Enum
from typing import Optional


class MessageLevel(Enum):
    WARNING = "warning"
    ERROR = "error"
    INTERNAL = "internal"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.name


@dataclass
class Message:
    level: MessageLevel
    content: str
    source_path: Optional[str] = None
    expression: Optional[str] = None

    def __str__(self):
        source_path = f"[{self.source_path}] " if self.source_path else ""
        expression = f"$({self.expression}) " if self.expression else ""
        return f"{self.level}: {source_path}{expression}{self.content}"


def to_message_level(provided_level: object) -> MessageLevel:
    """
    Coerces a string representation of a message level into a concreate MessageLevel
    :param provided_level: A string representation of a message level
    :return: MessageLevel
    """

    search_value = str(provided_level).lower().strip()
    return next(
        (
            message_level
            for message_level in MessageLevel
            if message_level.value == search_value
        ),
        MessageLevel.INTERNAL,
    )


def to_message(message: object) -> Message:
    if isinstance(message, dict):
        return Message(
            level=to_message_level(message.get("level", None)),
            content=str(message.get("content", None)),
            expression=(
                str(message.get("expression")) if "expression" in message else None
            ),
            source_path=(
                str(message.get("sourcePath")) if "sourcePath" in message else None
            ),
        )
    return Message(level=MessageLevel.INTERNAL, content="Could not parse message")


def to_messages(messages: list[object]) -> list[Message]:
    return list(map(to_message, messages))
