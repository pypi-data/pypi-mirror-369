from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import Order
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.organization_type import OrganizationTypeDataDTO
from maleo.metadata.enums.organization_type import IdentifierType
from maleo.metadata.mixins.organization_type import Name
from maleo.metadata.types.base.organization_type import IdentifierValueType


class CreateParameter(OrganizationTypeDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(Name, Order):
    pass


class UpdateParameter(
    UpdateBody,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass


class StatusUpdateParameter(
    StatusUpdateAction,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
