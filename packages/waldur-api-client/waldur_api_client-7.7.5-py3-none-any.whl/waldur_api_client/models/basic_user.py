from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="BasicUser")


@_attrs_define
class BasicUser:
    """
    Attributes:
        url (str):
        uuid (UUID):
        username (str): Required. 128 characters or fewer. Lowercase letters, numbers and @/./+/-/_ characters
        full_name (str):
        native_name (Union[Unset, str]):
        email (Union[Unset, str]):
        image (Union[None, Unset, str]):
    """

    url: str
    uuid: UUID
    username: str
    full_name: str
    native_name: Union[Unset, str] = UNSET
    email: Union[Unset, str] = UNSET
    image: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        url = self.url

        uuid = str(self.uuid)

        username = self.username

        full_name = self.full_name

        native_name = self.native_name

        email = self.email

        image: Union[None, Unset, str]
        if isinstance(self.image, Unset):
            image = UNSET
        else:
            image = self.image

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "username": username,
                "full_name": full_name,
            }
        )
        if native_name is not UNSET:
            field_dict["native_name"] = native_name
        if email is not UNSET:
            field_dict["email"] = email
        if image is not UNSET:
            field_dict["image"] = image

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        username = d.pop("username")

        full_name = d.pop("full_name")

        native_name = d.pop("native_name", UNSET)

        email = d.pop("email", UNSET)

        def _parse_image(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        image = _parse_image(d.pop("image", UNSET))

        basic_user = cls(
            url=url,
            uuid=uuid,
            username=username,
            full_name=full_name,
            native_name=native_name,
            email=email,
            image=image,
        )

        basic_user.additional_properties = d
        return basic_user

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
