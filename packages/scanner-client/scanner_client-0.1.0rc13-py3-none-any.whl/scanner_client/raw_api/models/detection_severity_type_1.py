from enum import Enum


class DetectionSeverityType1(str, Enum):
    INFORMATIONAL = "Informational"

    def __str__(self) -> str:
        return str(self.value)
