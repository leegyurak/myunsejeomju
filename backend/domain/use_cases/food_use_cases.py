from typing import List, Optional

from ..entities.food import Food, FoodCategory
from ..repositories.food_repository import FoodRepository


class GetAllFoodsUseCase:
    def __init__(self, food_repository: FoodRepository):
        self.food_repository = food_repository
    
    def execute(self) -> List[Food]:
        return self.food_repository.get_all()


class GetFoodByIdUseCase:
    def __init__(self, food_repository: FoodRepository):
        self.food_repository = food_repository
    
    def execute(self, food_id: int) -> Optional[Food]:
        return self.food_repository.get_by_id(food_id)


class GetFoodsByCategoryUseCase:
    def __init__(self, food_repository: FoodRepository):
        self.food_repository = food_repository
    
    def execute(self, category: FoodCategory) -> List[Food]:
        return self.food_repository.get_by_category(category)