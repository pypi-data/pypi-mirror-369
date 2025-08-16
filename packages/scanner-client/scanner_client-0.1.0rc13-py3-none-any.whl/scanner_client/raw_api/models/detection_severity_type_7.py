from enum import Enum


class DetectionSeverityType7(str, Enum):
    OTHER = "Other"

    def __str__(self) -> str:
        return str(self.value)
