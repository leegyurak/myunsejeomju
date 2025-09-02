from typing import List
from abc import ABC, abstractmethod

from ..entities.order import Order
from ..entities.food import Food


class TransactionManager(ABC):
    """트랜잭션 관리 추상화"""
    
    @abstractmethod
    def execute_in_transaction(self, func, *args, **kwargs):
        """트랜잭션 내에서 함수를 실행합니다."""
        pass


class OrderDomainService:
    """주문 관련 도메인 서비스"""
    
    def __init__(self, transaction_manager: TransactionManager):
        self.transaction_manager = transaction_manager
    
    def validate_food_availability(self, foods: List[Food], order_items: List[dict]) -> None:
        """음식 재고 가능성을 검증합니다."""
        food_dict = {food.id: food for food in foods}
        sold_out_foods = []
        
        for item in order_items:
            food = food_dict.get(item['food_id'])
            if not food:
                raise ValueError(f"Food with id {item['food_id']} not found")
            if food.sold_out:
                sold_out_foods.append(food.name)
        
        if sold_out_foods:
            raise ValueError(f"다음 음식들이 품절되었습니다: {', '.join(sold_out_foods)}")
    
    def create_order_with_availability_check(self, create_order_func, *args, **kwargs) -> Order:
        """재고 체크와 함께 주문을 생성합니다."""
        return self.transaction_manager.execute_in_transaction(
            create_order_func, *args, **kwargs
        )