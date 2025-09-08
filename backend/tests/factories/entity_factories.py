"""
Factory classes for creating domain entity instances.
"""
import factory
from datetime import datetime
from django.utils import timezone
import uuid

from domain.entities.food import Food, FoodCategory
from domain.entities.table import Table
from domain.entities.order import Order, OrderItem, MinusOrderItem


class FoodFactory(factory.Factory):
    """Factory for creating Food entity instances."""
    
    class Meta:
        model = Food
    
    id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: f"음식{n}")
    price = factory.Faker('random_int', min=5000, max=25000)
    category = factory.LazyFunction(lambda: FoodCategory.MAIN)
    description = factory.Faker('sentence', nb_words=5)
    image = factory.Faker('url')
    sold_out = False


class SoldOutFoodFactory(FoodFactory):
    """Factory for creating sold out Food entity instances."""
    sold_out = True


class DrinkFoodFactory(FoodFactory):
    """Factory for creating drink Food entity instances."""
    category = factory.LazyFunction(lambda: FoodCategory.SIDE)
    name = factory.Sequence(lambda n: f"음료{n}")


class TableFactory(factory.Factory):
    """Factory for creating Table entity instances."""
    
    class Meta:
        model = Table
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"테이블{n}")
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class OrderItemFactory(factory.Factory):
    """Factory for creating OrderItem entity instances."""
    
    class Meta:
        model = OrderItem
    
    food = factory.SubFactory(FoodFactory)
    quantity = factory.Faker('random_int', min=1, max=5)
    price = factory.LazyAttribute(lambda obj: obj.food.price)


class MinusOrderItemFactory(factory.Factory):
    """Factory for creating MinusOrderItem entity instances."""
    
    class Meta:
        model = MinusOrderItem
    
    food = factory.SubFactory(FoodFactory)
    quantity = factory.Faker('random_int', min=-5, max=-1)
    price = factory.LazyAttribute(lambda obj: obj.food.price)
    reason = factory.Faker('random_element', elements=['sold_out', 'unavailable', 'damaged'])


class OrderFactory(factory.Factory):
    """Factory for creating Order entity instances."""
    
    class Meta:
        model = Order
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    table = factory.SubFactory(TableFactory)
    order_date = factory.LazyFunction(timezone.now)
    items = factory.LazyFunction(lambda: [OrderItemFactory()])
    payer_name = None
    status = 'completed'
    pre_order_amount = None
    minus_items = None
    is_visible = True
    discord_notified = False


class PreOrderFactory(OrderFactory):
    """Factory for creating pre-order Order entity instances."""
    status = 'pre_order'
    payer_name = factory.Faker('name')
    pre_order_amount = factory.Faker('random_int', min=10000, max=50000)