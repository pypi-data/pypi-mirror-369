from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import Order
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.enums.gender import IdentifierType
from maleo.metadata.mixins.gender import Name
from maleo.metadata.types.base.gender import IdentifierValueType


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(
    Order,
    Name,
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
