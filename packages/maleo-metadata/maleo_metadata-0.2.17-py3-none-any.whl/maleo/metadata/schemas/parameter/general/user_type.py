from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import Order
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.user_type import UserTypeDataDTO
from maleo.metadata.enums.user_type import IdentifierType
from maleo.metadata.mixins.user_type import Name
from maleo.metadata.types.base.user_type import IdentifierValueType


class CreateParameter(UserTypeDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(
    Name,
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
