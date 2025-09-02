from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.food import Food, FoodCategory


class FoodRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Food]:
        pass
    
    @abstractmethod
    def get_by_id(self, food_id: int) -> Optional[Food]:
        pass
    
    @abstractmethod
    def get_by_category(self, category: FoodCategory) -> List[Food]:
        pass
    
    @abstractmethod
    def create(self, food: Food) -> Food:
        pass
    
    @abstractmethod
    def update(self, food: Food) -> Food:
        pass
    
    @abstractmethod
    def delete(self, food_id: int) -> bool:
        pass
    
    @abstractmethod
    def get_by_ids_for_update(self, food_ids: List[int]) -> List[Food]:
        """
        주문 생성 시 동시성 이슈 방지를 위해 select_for_update로 음식들을 조회합니다.
        트랜잭션 내에서만 호출되어야 합니다.
        """
        pass