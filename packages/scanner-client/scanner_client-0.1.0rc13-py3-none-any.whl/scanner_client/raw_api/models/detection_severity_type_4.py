from enum import Enum


class DetectionSeverityType4(str, Enum):
    HIGH = "High"

    def __str__(self) -> str:
        return str(self.value)
