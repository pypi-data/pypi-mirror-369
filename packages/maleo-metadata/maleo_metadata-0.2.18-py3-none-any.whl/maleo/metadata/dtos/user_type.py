from maleo.soma.mixins.general import Order
from maleo.metadata.mixins.user_type import Key, Name


class UserTypeDataDTO(
    Name,
    Key,
    Order,
):
    pass
