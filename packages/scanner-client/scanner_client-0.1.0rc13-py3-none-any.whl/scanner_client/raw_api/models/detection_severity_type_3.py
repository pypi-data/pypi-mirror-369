from enum import Enum


class DetectionSeverityType3(str, Enum):
    MEDIUM = "Medium"

    def __str__(self) -> str:
        return str(self.value)
