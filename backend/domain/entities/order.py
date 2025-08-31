from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .food import Food
from .table import Table


@dataclass
class OrderItem:
    food: Food
    quantity: int
    price: int  # 주문 당시 가격
    
    @property
    def total_price(self) -> int:
        return self.price * self.quantity


@dataclass
class MinusOrderItem:
    food: Food
    quantity: int  # 음수 값
    price: int
    reason: str  # 'sold_out', 'unavailable', 'damaged'
    
    @property
    def total_price(self) -> int:
        return self.price * self.quantity


@dataclass
class Order:
    id: str
    table: Table
    order_date: datetime
    items: List[OrderItem]
    payer_name: Optional[str] = None
    status: str = 'completed'
    minus_items: Optional[List[MinusOrderItem]] = None
    pre_order_amount: Optional[int] = None  # pre-order용 총 금액
    is_visible: bool = True
    discord_notified: bool = False
    
    @property
    def total_amount(self) -> int:
        # pre_order_amount가 있는 경우 (pre-order에서 completed로 변경된 주문 포함) 사용
        if self.pre_order_amount is not None:
            return self.pre_order_amount
        
        # 일반 주문인 경우 items 기반 계산
        items_total = sum(item.total_price for item in self.items)
        minus_total = sum(minus_item.total_price for minus_item in (self.minus_items or []))
        return items_total + minus_total  # minus_total은 이미 음수