from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

try:
    from .models import OrderStatus
except ImportError:  # pragma: no cover
    from models import OrderStatus


class ProductOut(BaseModel):
    id: int
    name: str
    code: str
    price: float
    quantity: int
    in_stock: bool = True
    description: Optional[str] = None

    class Config:
        from_attributes = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    session_id: Optional[int] = None
    payment_method: Optional[str] = "cash"


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    line_amount: float


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    payment_method: Optional[str] = "cash"
    total_amount: float
    created_at: datetime
    items: List[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

