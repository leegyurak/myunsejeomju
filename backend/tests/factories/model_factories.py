"""
Factory classes for creating test data using Factory Boy.
"""
import factory
from factory.django import DjangoModelFactory
from django.utils import timezone
import uuid

from infrastructure.database.models import (
    FoodModel, 
    TableModel, 
    OrderModel, 
    OrderItemModel,
    MinusOrderItemModel,
    PaymentDepositModel
)


class FoodModelFactory(DjangoModelFactory):
    """Factory for creating FoodModel instances."""
    
    class Meta:
        model = FoodModel
    
    name = factory.Sequence(lambda n: f"음식{n}")
    price = factory.Faker('random_int', min=5000, max=25000)
    category = factory.Faker('random_element', elements=['main', 'side'])
    description = factory.Faker('sentence', nb_words=5)
    image = factory.Faker('url')
    sold_out = False
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class SoldOutFoodModelFactory(FoodModelFactory):
    """Factory for creating sold out FoodModel instances."""
    sold_out = True


class TableModelFactory(DjangoModelFactory):
    """Factory for creating TableModel instances."""
    
    class Meta:
        model = TableModel
    
    id = factory.LazyFunction(uuid.uuid4)
    name = factory.Sequence(lambda n: f"테이블{n}")
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class OrderModelFactory(DjangoModelFactory):
    """Factory for creating OrderModel instances."""
    
    class Meta:
        model = OrderModel
    
    id = factory.LazyFunction(uuid.uuid4)
    table = factory.SubFactory(TableModelFactory)
    payer_name = factory.Faker('name')
    status = 'completed'
    pre_order_amount = None
    order_date = factory.LazyFunction(timezone.now)
    is_visible = True
    discord_notified = False
    created_at = factory.LazyFunction(timezone.now)
    updated_at = factory.LazyFunction(timezone.now)


class PreOrderModelFactory(OrderModelFactory):
    """Factory for creating pre-order OrderModel instances."""
    status = 'pre_order'
    pre_order_amount = factory.Faker('random_int', min=10000, max=50000)


class OrderItemModelFactory(DjangoModelFactory):
    """Factory for creating OrderItemModel instances."""
    
    class Meta:
        model = OrderItemModel
    
    order = factory.SubFactory(OrderModelFactory)
    food = factory.SubFactory(FoodModelFactory)
    quantity = factory.Faker('random_int', min=1, max=5)
    price = factory.LazyAttribute(lambda obj: obj.food.price)


class MinusOrderItemModelFactory(DjangoModelFactory):
    """Factory for creating MinusOrderItemModel instances."""
    
    class Meta:
        model = MinusOrderItemModel
    
    order = factory.SubFactory(OrderModelFactory)
    food = factory.SubFactory(FoodModelFactory)
    quantity = factory.Faker('random_int', min=-5, max=-1)
    price = factory.LazyAttribute(lambda obj: obj.food.price)
    reason = factory.Faker('random_element', elements=['sold_out', 'unavailable', 'damaged'])


class PaymentDepositModelFactory(DjangoModelFactory):
    """Factory for creating PaymentDepositModel instances."""
    
    class Meta:
        model = PaymentDepositModel
    
    id = factory.LazyFunction(uuid.uuid4)
    transaction_name = factory.Faker('name')
    bank_account_number = factory.Faker('numerify', text='###-####-####')
    amount = factory.Faker('random_int', min=10000, max=100000)
    bank_code = factory.Faker('numerify', text='###')
    bank_account_id = factory.Faker('uuid4')
    transaction_date = factory.LazyFunction(timezone.now)
    processing_date = factory.LazyFunction(timezone.now)
    balance = factory.Faker('random_int', min=100000, max=10000000)
    created_at = factory.LazyFunction(timezone.now)