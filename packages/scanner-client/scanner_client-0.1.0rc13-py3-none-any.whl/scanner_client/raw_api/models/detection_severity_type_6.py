from enum import Enum


class DetectionSeverityType6(str, Enum):
    FATAL = "Fatal"

    def __str__(self) -> str:
        return str(self.value)
