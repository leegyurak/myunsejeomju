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