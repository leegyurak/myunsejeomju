from dataclasses import dataclass
from typing import Optional
from enum import Enum


class FoodCategory(Enum):
    MAIN = 'main'
    SIDE = 'side'


@dataclass
class Food:
    id: int
    name: str
    price: int
    category: FoodCategory
    description: Optional[str] = None
    image: Optional[str] = None
    sold_out: bool = False
    
    def __post_init__(self):
        if isinstance(self.category, str):
            self.category = FoodCategory(self.category)