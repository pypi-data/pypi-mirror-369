from enum import Enum


class RbacDetectionRulePermissionType(str, Enum):
    DELETE = "Delete"
    MANAGE = "Manage"
    READ = "Read"
    UPDATE = "Update"

    def __str__(self) -> str:
        return str(self.value)
