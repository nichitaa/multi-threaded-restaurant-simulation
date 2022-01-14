from pydantic import BaseModel
from typing import List, Any


class OrderDto(BaseModel):
    restaurant_id: int
    items: List[int]
    max_wait: float
    priority: int
    time_start: Any


class ClientOrderDto(BaseModel):
    client_id: str
    orders: List[OrderDto]
    created_time: Any
