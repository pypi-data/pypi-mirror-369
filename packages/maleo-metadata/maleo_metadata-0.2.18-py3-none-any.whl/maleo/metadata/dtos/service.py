from maleo.soma.mixins.general import Order
from maleo.metadata.mixins.service import ServiceType, Category, Key, Name, Secret


class ServiceDataDTO(
    Name,
    Key,
    ServiceType,
    Category,
    Order,
):
    pass


class FullServiceDataDTO(Secret, ServiceDataDTO):
    pass
