from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.request_types import RequestTypes
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.order_create_request_limits import OrderCreateRequestLimits


T = TypeVar("T", bound="OrderCreateRequest")


@_attrs_define
class OrderCreateRequest:
    """
    Attributes:
        offering (str):
        project (str):
        plan (Union[Unset, str]):
        attributes (Union[Unset, Any]):
        limits (Union[Unset, OrderCreateRequestLimits]):
        type_ (Union[Unset, RequestTypes]):  Default: RequestTypes.CREATE.
        accepting_terms_of_service (Union[Unset, bool]):
        callback_url (Union[None, Unset, str]):
    """

    offering: str
    project: str
    plan: Union[Unset, str] = UNSET
    attributes: Union[Unset, Any] = UNSET
    limits: Union[Unset, "OrderCreateRequestLimits"] = UNSET
    type_: Union[Unset, RequestTypes] = RequestTypes.CREATE
    accepting_terms_of_service: Union[Unset, bool] = UNSET
    callback_url: Union[None, Unset, str] = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        offering = self.offering

        project = self.project

        plan = self.plan

        attributes = self.attributes

        limits: Union[Unset, dict[str, Any]] = UNSET
        if not isinstance(self.limits, Unset):
            limits = self.limits.to_dict()

        type_: Union[Unset, str] = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        accepting_terms_of_service = self.accepting_terms_of_service

        callback_url: Union[None, Unset, str]
        if isinstance(self.callback_url, Unset):
            callback_url = UNSET
        else:
            callback_url = self.callback_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "offering": offering,
                "project": project,
            }
        )
        if plan is not UNSET:
            field_dict["plan"] = plan
        if attributes is not UNSET:
            field_dict["attributes"] = attributes
        if limits is not UNSET:
            field_dict["limits"] = limits
        if type_ is not UNSET:
            field_dict["type"] = type_
        if accepting_terms_of_service is not UNSET:
            field_dict["accepting_terms_of_service"] = accepting_terms_of_service
        if callback_url is not UNSET:
            field_dict["callback_url"] = callback_url

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.order_create_request_limits import OrderCreateRequestLimits

        d = dict(src_dict)
        offering = d.pop("offering")

        project = d.pop("project")

        plan = d.pop("plan", UNSET)

        attributes = d.pop("attributes", UNSET)

        _limits = d.pop("limits", UNSET)
        limits: Union[Unset, OrderCreateRequestLimits]
        if isinstance(_limits, Unset):
            limits = UNSET
        else:
            limits = OrderCreateRequestLimits.from_dict(_limits)

        _type_ = d.pop("type", UNSET)
        type_: Union[Unset, RequestTypes]
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = RequestTypes(_type_)

        accepting_terms_of_service = d.pop("accepting_terms_of_service", UNSET)

        def _parse_callback_url(data: object) -> Union[None, Unset, str]:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(Union[None, Unset, str], data)

        callback_url = _parse_callback_url(d.pop("callback_url", UNSET))

        order_create_request = cls(
            offering=offering,
            project=project,
            plan=plan,
            attributes=attributes,
            limits=limits,
            type_=type_,
            accepting_terms_of_service=accepting_terms_of_service,
            callback_url=callback_url,
        )

        order_create_request.additional_properties = d
        return order_create_request

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
