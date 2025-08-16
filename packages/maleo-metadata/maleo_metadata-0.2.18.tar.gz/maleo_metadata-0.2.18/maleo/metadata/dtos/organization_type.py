from maleo.soma.mixins.general import Order
from maleo.metadata.mixins.organization_type import Key, Name


class OrganizationTypeDataDTO(
    Name,
    Key,
    Order,
):
    pass
