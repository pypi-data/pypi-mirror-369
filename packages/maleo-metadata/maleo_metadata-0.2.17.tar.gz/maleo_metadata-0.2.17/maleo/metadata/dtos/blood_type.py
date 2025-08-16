from maleo.soma.mixins.general import Order
from maleo.metadata.mixins.blood_type import Key, Name


class BloodTypeDataDTO(
    Name,
    Key,
    Order,
):
    pass
