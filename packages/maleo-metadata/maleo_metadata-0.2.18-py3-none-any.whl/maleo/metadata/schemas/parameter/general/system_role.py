from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import Order
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.system_role import SystemRoleDataDTO
from maleo.metadata.enums.system_role import IdentifierType
from maleo.metadata.mixins.system_role import Name
from maleo.metadata.types.base.system_role import IdentifierValueType


class CreateParameter(SystemRoleDataDTO):
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
