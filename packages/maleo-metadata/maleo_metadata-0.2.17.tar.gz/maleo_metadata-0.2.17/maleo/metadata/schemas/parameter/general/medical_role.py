from maleo.soma.schemas.parameter.general import ReadSingleParameterSchema
from maleo.soma.mixins.general import OptionalParentId, Order
from maleo.soma.mixins.parameter import (
    IdentifierTypeValue as IdentifierTypeValueMixin,
    StatusUpdateAction,
)
from maleo.metadata.dtos.medical_role import MedicalRoleDataDTO
from maleo.metadata.enums.medical_role import IdentifierType
from maleo.metadata.mixins.medical_role import Code, Name
from maleo.metadata.types.base.medical_role import IdentifierValueType


class CreateParameter(MedicalRoleDataDTO):
    pass


class ReadSingleParameter(
    ReadSingleParameterSchema[IdentifierType, IdentifierValueType]
):
    pass


class UpdateBody(
    Name,
    Code,
    Order,
    OptionalParentId,
):
    pass


class UpdateParameter(
    UpdateBody, IdentifierTypeValueMixin[IdentifierType, IdentifierValueType]
):
    pass


class StatusUpdateParameter(
    StatusUpdateAction,
    IdentifierTypeValueMixin[IdentifierType, IdentifierValueType],
):
    pass
