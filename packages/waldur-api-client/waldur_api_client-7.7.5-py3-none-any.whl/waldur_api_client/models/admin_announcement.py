import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.admin_announcement_type_enum import AdminAnnouncementTypeEnum
from ..types import UNSET, Unset

T = TypeVar("T", bound="AdminAnnouncement")


@_attrs_define
class AdminAnnouncement:
    """
    Attributes:
        uuid (Union[Unset, UUID]):
        description (Union[Unset, str]):
        active_from (Union[Unset, datetime.datetime]):
        active_to (Union[Unset, datetime.datetime]):
        is_active (Union[Unset, bool]):
        type_ (Union[Unset, AdminAnnouncementTypeEnum]):
        created (Union[Unset, datetime.datetime]):
    """

    uuid: Union[Unset, UUID] = UNSET
    description: Union[Unset, str] = UNSET
    active_from: Union[Unset, datetime.datetime] = UNSET
    active_to: Union[Unset, datetime.datetime] = UNSET
    is_active: Union[Unset, bool] = UNSET
    type_: Union[Unset, AdminAnnouncementTypeEnum] = UNSET
    created: Union[Unset, datetime.datetime] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        uuid: Union[Unset, str] = UNSET
        if not isinstance(self.uuid, Unset):
            uuid = str(self.uuid)

        description = self.description

        active_from: Union[Unset, str] = UNSET
        if not isinstance(self.active_from, Unset):
            active_from = self.active_from.isoformat()

        active_to: Union[Unset, str] = UNSET
        if not isinstance(self.active_to, Unset):
            active_to = self.active_to.isoformat()

        is_active = self.is_active

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        created: Union[Unset, str] = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if uuid is not UNSET:
            field_dict["uuid"] = uuid
        if description is not UNSET:
            field_dict["description"] = description
        if active_from is not UNSET:
            field_dict["active_from"] = active_from
        if active_to is not UNSET:
            field_dict["active_to"] = active_to
        if is_active is not UNSET:
            field_dict["is_active"] = is_active
        if type_ is not UNSET:
            field_dict["type"] = type_
        if created is not UNSET:
            field_dict["created"] = created

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        _uuid = d.pop("uuid", UNSET)
        uuid: Union[Unset, UUID]
        if isinstance(_uuid, Unset):
            uuid = UNSET
        else:
            uuid = UUID(_uuid)

        description = d.pop("description", UNSET)

        _active_from = d.pop("active_from", UNSET)
        active_from: Union[Unset, datetime.datetime]
        if isinstance(_active_from, Unset):
            active_from = UNSET
        else:
            active_from = isoparse(_active_from)

        _active_to = d.pop("active_to", UNSET)
        active_to: Union[Unset, datetime.datetime]
        if isinstance(_active_to, Unset):
            active_to = UNSET
        else:
            active_to = isoparse(_active_to)

        is_active = d.pop("is_active", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, AdminAnnouncementTypeEnum]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = AdminAnnouncementTypeEnum(_type_)

        _created = d.pop("created", UNSET)
        created: Union[Unset, datetime.datetime]
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = isoparse(_created)

        admin_announcement = cls(
            uuid=uuid,
            description=description,
            active_from=active_from,
            active_to=active_to,
            is_active=is_active,
            type_=type_,
            created=created,
        )

        admin_announcement.additional_properties = d
        return admin_announcement

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
