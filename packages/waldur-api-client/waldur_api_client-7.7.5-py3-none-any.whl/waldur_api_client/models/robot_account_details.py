import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast
from uuid import UUID

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.robot_account_states import RobotAccountStates
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.basic_user import BasicUser
    from ..models.fingerprint import Fingerprint
    from ..models.merged_plugin_options import MergedPluginOptions
    from ..models.ssh_key import SshKey


T = TypeVar("T", bound="RobotAccountDetails")


@_attrs_define
class RobotAccountDetails:
    """
    Attributes:
        url (str):
        uuid (UUID):
        created (datetime.datetime):
        modified (datetime.datetime):
        resource (str):
        type_ (str): Type of the robot account.
        users (list['BasicUser']):
        backend_id (str):
        fingerprints (list['Fingerprint']):
        responsible_user (Union['BasicUser', None]):
        user_keys (list['SshKey']):
        resource_name (str):
        resource_uuid (UUID):
        project_name (str):
        project_uuid (UUID):
        customer_uuid (UUID):
        customer_name (str):
        offering_customer_uuid (UUID):
        offering_plugin_options (MergedPluginOptions):
        username (Union[Unset, str]):
        description (Union[Unset, str]):
        error_message (Union[Unset, str]):
        error_traceback (Union[Unset, str]):
        keys (Union[Unset, Any]):
        state (Union[Unset, RobotAccountStates]):
    """

    url: str
    uuid: UUID
    created: datetime.datetime
    modified: datetime.datetime
    resource: str
    type_: str
    users: list["BasicUser"]
    backend_id: str
    fingerprints: list["Fingerprint"]
    responsible_user: Union["BasicUser", None]
    user_keys: list["SshKey"]
    resource_name: str
    resource_uuid: UUID
    project_name: str
    project_uuid: UUID
    customer_uuid: UUID
    customer_name: str
    offering_customer_uuid: UUID
    offering_plugin_options: "MergedPluginOptions"
    username: Union[Unset, str] = UNSET
    description: Union[Unset, str] = UNSET
    error_message: Union[Unset, str] = UNSET
    error_traceback: Union[Unset, str] = UNSET
    keys: Union[Unset, Any] = UNSET
    state: Union[Unset, RobotAccountStates] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        from ..models.basic_user import BasicUser

        url = self.url

        uuid = str(self.uuid)

        created = self.created.isoformat()

        modified = self.modified.isoformat()

        resource = self.resource

        type_ = self.type_

        users = []
        for users_item_data in self.users:
            users_item = users_item_data.to_dict()
            users.append(users_item)

        backend_id = self.backend_id

        fingerprints = []
        for fingerprints_item_data in self.fingerprints:
            fingerprints_item = fingerprints_item_data.to_dict()
            fingerprints.append(fingerprints_item)

        responsible_user: Union[None, dict[str, Any]]
        if isinstance(self.responsible_user, BasicUser):
            responsible_user = self.responsible_user.to_dict()
        else:
            responsible_user = self.responsible_user

        user_keys = []
        for user_keys_item_data in self.user_keys:
            user_keys_item = user_keys_item_data.to_dict()
            user_keys.append(user_keys_item)

        resource_name = self.resource_name

        resource_uuid = str(self.resource_uuid)

        project_name = self.project_name

        project_uuid = str(self.project_uuid)

        customer_uuid = str(self.customer_uuid)

        customer_name = self.customer_name

        offering_customer_uuid = str(self.offering_customer_uuid)

        offering_plugin_options = self.offering_plugin_options.to_dict()

        username = self.username

        description = self.description

        error_message = self.error_message

        error_traceback = self.error_traceback

        keys = self.keys

        state: Union[Unset, int] = UNSET
        if not isinstance(self.state, Unset):
            state = self.state.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "url": url,
                "uuid": uuid,
                "created": created,
                "modified": modified,
                "resource": resource,
                "type": type_,
                "users": users,
                "backend_id": backend_id,
                "fingerprints": fingerprints,
                "responsible_user": responsible_user,
                "user_keys": user_keys,
                "resource_name": resource_name,
                "resource_uuid": resource_uuid,
                "project_name": project_name,
                "project_uuid": project_uuid,
                "customer_uuid": customer_uuid,
                "customer_name": customer_name,
                "offering_customer_uuid": offering_customer_uuid,
                "offering_plugin_options": offering_plugin_options,
            }
        )
        if username is not UNSET:
            field_dict["username"] = username
        if description is not UNSET:
            field_dict["description"] = description
        if error_message is not UNSET:
            field_dict["error_message"] = error_message
        if error_traceback is not UNSET:
            field_dict["error_traceback"] = error_traceback
        if keys is not UNSET:
            field_dict["keys"] = keys
        if state is not UNSET:
            field_dict["state"] = state

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.basic_user import BasicUser
        from ..models.fingerprint import Fingerprint
        from ..models.merged_plugin_options import MergedPluginOptions
        from ..models.ssh_key import SshKey

        d = dict(src_dict)
        url = d.pop("url")

        uuid = UUID(d.pop("uuid"))

        created = isoparse(d.pop("created"))

        modified = isoparse(d.pop("modified"))

        resource = d.pop("resource")

        type_ = d.pop("type")

        users = []
        _users = d.pop("users")
        for users_item_data in _users:
            users_item = BasicUser.from_dict(users_item_data)

            users.append(users_item)

        backend_id = d.pop("backend_id")

        fingerprints = []
        _fingerprints = d.pop("fingerprints")
        for fingerprints_item_data in _fingerprints:
            fingerprints_item = Fingerprint.from_dict(fingerprints_item_data)

            fingerprints.append(fingerprints_item)

        def _parse_responsible_user(data: object) -> Union["BasicUser", None]:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                responsible_user_type_1 = BasicUser.from_dict(data)

                return responsible_user_type_1
            except:  # noqa: E722
                pass
            return cast(Union["BasicUser", None], data)

        responsible_user = _parse_responsible_user(d.pop("responsible_user"))

        user_keys = []
        _user_keys = d.pop("user_keys")
        for user_keys_item_data in _user_keys:
            user_keys_item = SshKey.from_dict(user_keys_item_data)

            user_keys.append(user_keys_item)

        resource_name = d.pop("resource_name")

        resource_uuid = UUID(d.pop("resource_uuid"))

        project_name = d.pop("project_name")

        project_uuid = UUID(d.pop("project_uuid"))

        customer_uuid = UUID(d.pop("customer_uuid"))

        customer_name = d.pop("customer_name")

        offering_customer_uuid = UUID(d.pop("offering_customer_uuid"))

        offering_plugin_options = MergedPluginOptions.from_dict(d.pop("offering_plugin_options"))

        username = d.pop("username", UNSET)

        description = d.pop("description", UNSET)

        error_message = d.pop("error_message", UNSET)

        error_traceback = d.pop("error_traceback", UNSET)

        keys = d.pop("keys", UNSET)

        _state = d.pop("state", UNSET)
        state: Union[Unset, RobotAccountStates]
        if isinstance(_state, Unset):
            state = UNSET
        else:
            state = RobotAccountStates(_state)

        robot_account_details = cls(
            url=url,
            uuid=uuid,
            created=created,
            modified=modified,
            resource=resource,
            type_=type_,
            users=users,
            backend_id=backend_id,
            fingerprints=fingerprints,
            responsible_user=responsible_user,
            user_keys=user_keys,
            resource_name=resource_name,
            resource_uuid=resource_uuid,
            project_name=project_name,
            project_uuid=project_uuid,
            customer_uuid=customer_uuid,
            customer_name=customer_name,
            offering_customer_uuid=offering_customer_uuid,
            offering_plugin_options=offering_plugin_options,
            username=username,
            description=description,
            error_message=error_message,
            error_traceback=error_traceback,
            keys=keys,
            state=state,
        )

        robot_account_details.additional_properties = d
        return robot_account_details

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
