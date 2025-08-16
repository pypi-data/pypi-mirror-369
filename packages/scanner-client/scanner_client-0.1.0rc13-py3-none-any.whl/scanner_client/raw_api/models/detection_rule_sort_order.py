from enum import Enum


class DetectionRuleSortOrder(str, Enum):
    NAME = "Name"

    def __str__(self) -> str:
        return str(self.value)
