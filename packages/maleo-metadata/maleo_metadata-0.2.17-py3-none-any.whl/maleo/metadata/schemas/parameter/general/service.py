from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import Order
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.service import ServiceDataDTO
from maleo.metadata.enums.service import IdentifierType
from maleo.metadata.mixins.service import ServiceType, Category, Name
from maleo.metadata.types.base.service import IdentifierValueType


class CreateParameter(ServiceDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(
    Name,
    ServiceType,
    Category,
    Order,
):
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
