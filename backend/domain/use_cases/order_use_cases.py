from typing import List
from datetime import datetime
import uuid

from ..entities.order import Order, OrderItem
from ..entities.food import FoodCategory
from ..repositories.order_repository import OrderRepository
from ..repositories.food_repository import FoodRepository
from ..repositories.table_repository import TableRepository
from ..services.order_service import TransactionManager


class CreateOrderUseCase:
    def __init__(self, order_repository: OrderRepository, food_repository: FoodRepository, 
                 table_repository: TableRepository, transaction_manager: TransactionManager):
        self.order_repository = order_repository
        self.food_repository = food_repository
        self.table_repository = table_repository
        self.transaction_manager = transaction_manager

    def execute(self, table_id: str, items_data: List[dict]) -> Order:
        # Validate table exists
        table = self.table_repository.get_by_id(table_id)
        if not table:
            raise ValueError(f"Table with id {table_id} not found")
        
        # 트랜잭션 내에서 실행할 함수 정의
        def create_order_with_validation():
            order_items = []
            
            # 주문할 음식 ID들 수집
            food_ids = [item_data['food_id'] for item_data in items_data]
            
            # select_for_update로 음식들을 조회 (동시성 제어)
            foods = self.food_repository.get_by_ids_for_update(food_ids)
            food_dict = {food.id: food for food in foods}
            
            # 테이블의 가시 주문 수 확인
            existing_orders = self.order_repository.get_by_table_id(table_id)
            visible_orders_count = len(existing_orders)
            
            # 가시 주문이 0개인 경우, 메인 메뉴가 반드시 포함되어야 함
            if visible_orders_count == 0:
                has_main_menu = False
                for item_data in items_data:
                    food = food_dict.get(item_data['food_id'])
                    if food and food.category == FoodCategory.MAIN:
                        has_main_menu = True
                        break
                
                if not has_main_menu:
                    raise ValueError("첫 주문에는 반드시 메인 메뉴가 하나 이상 포함되어야 합니다.")
            
            # 품절 체크 및 주문 아이템 생성
            for item_data in items_data:
                food = food_dict.get(item_data['food_id'])
                if not food:
                    raise ValueError(f"Food with id {item_data['food_id']} not found")
                
                if food.sold_out:
                    raise ValueError(f"음식 '{food.name}'이(가) 품절되었습니다")
                
                order_item = OrderItem(
                    food=food,
                    quantity=item_data['quantity'],
                    price=food.price
                )
                order_items.append(order_item)
            
            # 주문 생성
            order = Order(
                id=str(uuid.uuid4()),
                table=table,
                order_date=datetime.now(),
                items=order_items
            )
            
            return self.order_repository.create(order)
        
        # 트랜잭션 내에서 주문 생성 실행
        return self.transaction_manager.execute_in_transaction(create_order_with_validation)


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
        
        # 테이블의 가시 주문 수 확인
        existing_orders = self.order_repository.get_by_table_id(table_id)
        visible_orders_count = len(existing_orders)
        
        # 가시 주문이 0개인 경우, 메인 메뉴가 반드시 포함되어야 함
        if visible_orders_count == 0:
            has_main_menu = False
            for item_data in items_data:
                food = self.food_repository.get_by_id(item_data['food_id'])
                if food and food.category == FoodCategory.MAIN:
                    has_main_menu = True
                    break
            
            if not has_main_menu:
                raise ValueError("첫 주문에는 반드시 메인 메뉴가 하나 이상 포함되어야 합니다.")
        
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