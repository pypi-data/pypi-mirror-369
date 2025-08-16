from enum import Enum


class DetectionSeverityType5(str, Enum):
    CRITICAL = "Critical"

    def __str__(self) -> str:
        return str(self.value)
