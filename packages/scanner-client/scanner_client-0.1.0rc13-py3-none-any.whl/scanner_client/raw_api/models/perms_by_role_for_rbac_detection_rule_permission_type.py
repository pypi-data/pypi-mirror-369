from typing import TYPE_CHECKING, Any, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.perms_by_role_for_rbac_detection_rule_permission_type_permissions_by_role import (
        PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole,
    )


T = TypeVar("T", bound="PermsByRoleForRbacDetectionRulePermissionType")


@_attrs_define
class PermsByRoleForRbacDetectionRulePermissionType:
    """Permissions to assign to newly-created resources

    Attributes:
        permissions_by_role (PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole):
    """

    permissions_by_role: "PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole"
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        permissions_by_role = self.permissions_by_role.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "permissions_by_role": permissions_by_role,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: dict[str, Any]) -> T:
        from ..models.perms_by_role_for_rbac_detection_rule_permission_type_permissions_by_role import (
            PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole,
        )

        d = src_dict.copy()
        permissions_by_role = PermsByRoleForRbacDetectionRulePermissionTypePermissionsByRole.from_dict(
            d.pop("permissions_by_role")
        )

        perms_by_role_for_rbac_detection_rule_permission_type = cls(
            permissions_by_role=permissions_by_role,
        )

        perms_by_role_for_rbac_detection_rule_permission_type.additional_properties = d
        return perms_by_role_for_rbac_detection_rule_permission_type

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
