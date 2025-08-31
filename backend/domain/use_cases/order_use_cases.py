from typing import List
from datetime import datetime
import uuid

from ..entities.order import Order, OrderItem
from ..entities.food import Food
from ..entities.table import Table
from ..repositories.order_repository import OrderRepository
from ..repositories.food_repository import FoodRepository
from ..repositories.table_repository import TableRepository


class CreateOrderUseCase:
    def __init__(self, order_repository: OrderRepository, food_repository: FoodRepository, table_repository: TableRepository):
        self.order_repository = order_repository
        self.food_repository = food_repository
        self.table_repository = table_repository
    
    def execute(self, table_id: str, items_data: List[dict]) -> Order:
        # Validate table exists
        table = self.table_repository.get_by_id(table_id)
        if not table:
            raise ValueError(f"Table with id {table_id} not found")
        
        order_items = []
        
        for item_data in items_data:
            food = self.food_repository.get_by_id(item_data['food_id'])
            if not food:
                raise ValueError(f"Food with id {item_data['food_id']} not found")
            
            if food.sold_out:
                raise ValueError(f"Food {food.name} is sold out")
            
            order_item = OrderItem(
                food=food,
                quantity=item_data['quantity'],
                price=food.price
            )
            order_items.append(order_item)
        
        order = Order(
            id=str(uuid.uuid4()),
            table=table,
            order_date=datetime.now(),
            items=order_items
        )
        
        return self.order_repository.create(order)


class GetAllOrdersUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self) -> List[Order]:
        return self.order_repository.get_all()


class GetOrdersByTableUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, table_id: str) -> List[Order]:
        return self.order_repository.get_by_table_id(table_id)


class CreatePreOrderUseCase:
    def __init__(self, order_repository: OrderRepository, table_repository: TableRepository, food_repository: FoodRepository):
        self.order_repository = order_repository
        self.table_repository = table_repository
        self.food_repository = food_repository
    
    def execute(self, table_id: str, payer_name: str, total_amount: int, items_data: List[dict]) -> Order:
        # Validate table exists
        table = self.table_repository.get_by_id(table_id)
        if not table:
            raise ValueError(f"Table with id {table_id} not found")
        
        order_items = []
        
        for item_data in items_data:
            food = self.food_repository.get_by_id(item_data['food_id'])
            if not food:
                raise ValueError(f"Food with id {item_data['food_id']} not found")
            
            if food.sold_out:
                raise ValueError(f"Food {food.name} is sold out")
            
            order_item = OrderItem(
                food=food,
                quantity=item_data['quantity'],
                price=food.price
            )
            order_items.append(order_item)
        
        order = Order(
            id=str(uuid.uuid4()),
            table=table,
            order_date=datetime.now(),
            items=order_items,
            payer_name=payer_name,
            status='pre_order',
            pre_order_amount=total_amount
        )
        
        return self.order_repository.create(order)


class UpdateOrderStatusUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, order_id: str, status: str) -> Order:
        order = self.order_repository.get_by_id(order_id)
        if not order:
            raise ValueError(f"Order with id {order_id} not found")
        
        order.status = status
        return self.order_repository.update(order)


class GetPreOrderByPaymentInfoUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, transaction_name: str, amount: int) -> Order:
        orders = self.order_repository.get_all_including_hidden()
        
        # pre_order 상태이면서 조건에 맞는 주문들을 찾아서 가장 최근 것을 반환
        matching_orders = []
        for order in orders:
            if (order.status == 'pre_order' and 
                order.payer_name == transaction_name and 
                order.pre_order_amount == amount):
                matching_orders.append(order)
        
        if matching_orders:
            # 가장 최근에 생성된 주문 반환 (order_date 기준 내림차순 정렬)
            matching_orders.sort(key=lambda x: x.order_date, reverse=True)
            return matching_orders[0]
        
        return None


class ResetOrdersByTableUseCase:
    def __init__(self, order_repository: OrderRepository):
        self.order_repository = order_repository
    
    def execute(self, table_id: str) -> bool:
        """특정 테이블의 모든 주문을 숨김 처리합니다."""
        # is_visible=False인 주문들도 포함하여 모든 주문을 가져와야 함
        all_orders = self.order_repository.get_all_including_hidden_by_table_id(table_id)
        
        for order in all_orders:
            order.is_visible = False
            self.order_repository.update(order)
        
        return True