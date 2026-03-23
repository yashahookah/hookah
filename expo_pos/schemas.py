from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from models import OrderStatus


class ProductOut(BaseModel):
    id: int
    name: str
    code: str
    price: float
    quantity: int
    display_name_en: Optional[str] = None
    search_ru: Optional[str] = None
    description: Optional[str] = None

    class Config:
        orm_mode = True


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    items: List[OrderItemCreate]
    session_id: Optional[int] = None


class OrderItemOut(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float
    line_amount: float


class OrderOut(BaseModel):
    id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    items: List[OrderItemOut]


class OrderStatusUpdate(BaseModel):
    status: OrderStatus

