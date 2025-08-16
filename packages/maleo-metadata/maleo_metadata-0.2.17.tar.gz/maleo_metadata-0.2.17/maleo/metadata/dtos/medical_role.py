from maleo.soma.mixins.general import Order, OptionalParentId
from maleo.metadata.mixins.medical_role import Code, Key, Name


class MedicalRoleDataDTO(
    Name,
    Key,
    Code,
    Order,
    OptionalParentId,
):
    pass
