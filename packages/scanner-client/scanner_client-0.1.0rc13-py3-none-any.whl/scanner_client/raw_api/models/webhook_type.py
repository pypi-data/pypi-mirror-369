from enum import Enum


class WebhookType(str, Enum):
    OTHER = "Other"
    TORQ = "Torq"

    def __str__(self) -> str:
        return str(self.value)
