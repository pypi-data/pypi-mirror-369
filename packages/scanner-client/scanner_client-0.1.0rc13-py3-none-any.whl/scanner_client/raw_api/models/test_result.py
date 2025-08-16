from enum import Enum


class TestResult(str, Enum):
    FAILED = "Failed"
    PASSED = "Passed"

    def __str__(self) -> str:
        return str(self.value)
