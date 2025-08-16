from enum import Enum


class DetectionSeverityType2(str, Enum):
    LOW = "Low"

    def __str__(self) -> str:
        return str(self.value)
