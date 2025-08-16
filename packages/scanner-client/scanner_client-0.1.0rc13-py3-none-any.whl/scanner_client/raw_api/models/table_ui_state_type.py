from enum import Enum


class TableUiStateType(str, Enum):
    GENERICTABLE = "GenericTable"
    GROUPBY = "GroupBy"
    LOGSEARCH = "LogSearch"

    def __str__(self) -> str:
        return str(self.value)
