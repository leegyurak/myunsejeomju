"""
Unit tests for factory classes.
"""
import pytest
from django.test import TestCase

from tests.factories.model_factories import (
    FoodModelFactory,
    SoldOutFoodModelFactory,
    TableModelFactory,
    OrderModelFactory,
    OrderItemModelFactory
)
from tests.factories.entity_factories import (
    FoodFactory,
    SoldOutFoodFactory,
    DrinkFoodFactory,
    TableFactory,
    OrderItemFactory,
    MinusOrderItemFactory,
    OrderFactory,
    PreOrderFactory
)
from infrastructure.database.models import FoodModel, TableModel, OrderModel, OrderItemModel
from domain.entities.food import Food, FoodCategory
from domain.entities.table import Table
from domain.entities.order import Order, OrderItem, MinusOrderItem


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
class TestModelFactories(TestCase):
    """Test cases for Django model factories."""
    
    def test_food_model_factory_creates_valid_food(self):
        """FoodModelFactory가 유효한 음식 모델을 생성한다."""
        # Given & When
        food = FoodModelFactory()
        
        # Then
        assert isinstance(food, FoodModel)
        assert food.id is not None
        assert food.name is not None
        assert food.price > 0
        assert food.category in ['main', 'side']
        assert food.description is not None
        assert food.image is not None
        assert isinstance(food.sold_out, bool)
        
        # 데이터베이스에 저장되었는지 확인
        saved_food = FoodModel.objects.get(id=food.id)
        assert saved_food.name == food.name
    
    def test_sold_out_food_model_factory_creates_sold_out_food(self):
        """SoldOutFoodModelFactory가 품절된 음식을 생성한다."""
        # Given & When
        food = SoldOutFoodModelFactory()
        
        # Then
        assert isinstance(food, FoodModel)
        assert food.sold_out is True
        assert food.name is not None
        assert food.price > 0
    
    def test_food_model_factory_with_custom_attributes(self):
        """FoodModelFactory가 커스텀 속성으로 음식을 생성한다."""
        # Given & When
        food = FoodModelFactory(
            name="커스텀 비빔밥",
            price=15000,
            category=FoodCategory.MAIN.value,
            sold_out=True
        )
        
        # Then
        assert food.name == "커스텀 비빔밥"
        assert food.price == 15000
        assert food.category == "main"
        assert food.sold_out is True
    
    def test_table_model_factory_creates_valid_table(self):
        """TableModelFactory가 유효한 테이블 모델을 생성한다."""
        # Given & When
        table = TableModelFactory()
        
        # Then
        assert isinstance(table, TableModel)
        assert table.id is not None
        assert table.name is not None
        assert table.created_at is not None
        assert table.updated_at is not None
        
        # 데이터베이스에 저장되었는지 확인
        saved_table = TableModel.objects.get(id=table.id)
        assert saved_table.name == table.name
    
    def test_table_model_factory_with_custom_name(self):
        """TableModelFactory가 커스텀 이름으로 테이블을 생성한다."""
        # Given & When
        table = TableModelFactory(name="VIP 테이블")
        
        # Then
        assert table.name == "VIP 테이블"
    
    def test_order_model_factory_creates_valid_order(self):
        """OrderModelFactory가 유효한 주문 모델을 생성한다."""
        # Given & When
        order = OrderModelFactory()
        
        # Then
        assert isinstance(order, OrderModel)
        assert order.id is not None
        assert order.table is not None
        assert order.order_date is not None
        assert order.status in ['pending', 'completed', 'cancelled', 'pre_order']
        assert isinstance(order.is_visible, bool)
        assert isinstance(order.discord_notified, bool)
        
        # 관련 테이블이 존재하는지 확인
        assert TableModel.objects.filter(id=order.table.id).exists()
    
    def test_order_model_factory_with_table(self):
        """OrderModelFactory가 지정된 테이블로 주문을 생성한다."""
        # Given
        table = TableModelFactory(name="지정 테이블")
        
        # When
        order = OrderModelFactory(table=table)
        
        # Then
        assert order.table.id == table.id
        assert order.table.name == "지정 테이블"
    
    def test_order_item_model_factory_creates_valid_order_item(self):
        """OrderItemModelFactory가 유효한 주문 아이템을 생성한다."""
        # Given & When
        order_item = OrderItemModelFactory()
        
        # Then
        assert isinstance(order_item, OrderItemModel)
        assert order_item.id is not None
        assert order_item.order is not None
        assert order_item.food is not None
        assert order_item.quantity > 0
        assert order_item.price >= 0
        
        # 관련 객체들이 존재하는지 확인
        assert OrderModel.objects.filter(id=order_item.order.id).exists()
        assert FoodModel.objects.filter(id=order_item.food.id).exists()


@pytest.mark.unit
class TestEntityFactories:
    """Test cases for domain entity factories."""
    
    def test_food_factory_creates_valid_food(self):
        """FoodFactory가 유효한 음식 엔티티를 생성한다."""
        # Given & When
        food = FoodFactory()
        
        # Then
        assert isinstance(food, Food)
        assert food.id is not None
        assert food.name is not None
        assert food.price > 0
        assert food.category in [FoodCategory.MAIN, FoodCategory.SIDE]
        assert food.description is not None
        assert food.image is not None
        assert isinstance(food.sold_out, bool)
    
    def test_sold_out_food_factory_creates_sold_out_food(self):
        """SoldOutFoodFactory가 품절된 음식 엔티티를 생성한다."""
        # Given & When
        food = SoldOutFoodFactory()
        
        # Then
        assert isinstance(food, Food)
        assert food.sold_out is True
    
    def test_drink_food_factory_creates_drink(self):
        """DrinkFoodFactory가 음료 카테고리 음식을 생성한다."""
        # Given & When
        drink = DrinkFoodFactory()
        
        # Then
        assert isinstance(drink, Food)
        assert drink.category == FoodCategory.SIDE
        assert "음료" in drink.name
    
    def test_food_factory_with_custom_attributes(self):
        """FoodFactory가 커스텀 속성으로 음식을 생성한다."""
        # Given & When
        food = FoodFactory(
            id=999,
            name="특별한 음식",
            price=25000,
            category=FoodCategory.MAIN,
            sold_out=True
        )
        
        # Then
        assert food.id == 999
        assert food.name == "특별한 음식"
        assert food.price == 25000
        assert food.category == FoodCategory.MAIN
        assert food.sold_out is True
    
    def test_table_factory_creates_valid_table(self):
        """TableFactory가 유효한 테이블 엔티티를 생성한다."""
        # Given & When
        table = TableFactory()
        
        # Then
        assert isinstance(table, Table)
        assert table.id is not None
        assert table.name is not None
        assert table.created_at is not None
        assert table.updated_at is not None
    
    def test_table_factory_with_custom_attributes(self):
        """TableFactory가 커스텀 속성으로 테이블을 생성한다."""
        # Given & When
        table = TableFactory(
            id="custom-table-id",
            name="커스텀 테이블"
        )
        
        # Then
        assert table.id == "custom-table-id"
        assert table.name == "커스텀 테이블"
    
    def test_order_item_factory_creates_valid_order_item(self):
        """OrderItemFactory가 유효한 주문 아이템을 생성한다."""
        # Given & When
        order_item = OrderItemFactory()
        
        # Then
        assert isinstance(order_item, OrderItem)
        assert isinstance(order_item.food, Food)
        assert order_item.quantity > 0
        assert order_item.price > 0
        assert order_item.total_price == order_item.quantity * order_item.price
    
    def test_order_item_factory_with_custom_food(self):
        """OrderItemFactory가 지정된 음식으로 주문 아이템을 생성한다."""
        # Given
        food = FoodFactory(name="지정 음식", price=8000)
        
        # When
        order_item = OrderItemFactory(food=food, quantity=3)
        
        # Then
        assert order_item.food.name == "지정 음식"
        assert order_item.price == 8000
        assert order_item.quantity == 3
        assert order_item.total_price == 24000
    
    def test_minus_order_item_factory_creates_valid_minus_item(self):
        """MinusOrderItemFactory가 유효한 마이너스 주문 아이템을 생성한다."""
        # Given & When
        minus_item = MinusOrderItemFactory()
        
        # Then
        assert isinstance(minus_item, MinusOrderItem)
        assert isinstance(minus_item.food, Food)
        assert minus_item.quantity < 0
        assert minus_item.price > 0
        assert minus_item.reason in ['sold_out', 'unavailable', 'damaged']
        assert minus_item.total_price < 0
    
    def test_order_factory_creates_valid_order(self):
        """OrderFactory가 유효한 주문 엔티티를 생성한다."""
        # Given & When
        order = OrderFactory()
        
        # Then
        assert isinstance(order, Order)
        assert order.id is not None
        assert isinstance(order.table, Table)
        assert order.order_date is not None
        assert isinstance(order.items, list)
        assert len(order.items) > 0
        assert all(isinstance(item, OrderItem) for item in order.items)
        assert order.status == 'completed'
        assert order.is_visible is True
        assert order.discord_notified is False
    
    def test_pre_order_factory_creates_pre_order(self):
        """PreOrderFactory가 선주문을 생성한다."""
        # Given & When
        pre_order = PreOrderFactory()
        
        # Then
        assert isinstance(pre_order, Order)
        assert pre_order.status == 'pre_order'
        assert pre_order.payer_name is not None
        assert pre_order.pre_order_amount is not None
        assert pre_order.pre_order_amount > 0
    
    def test_order_factory_with_custom_items(self):
        """OrderFactory가 지정된 아이템들로 주문을 생성한다."""
        # Given
        item1 = OrderItemFactory()
        item2 = OrderItemFactory()
        
        # When
        order = OrderFactory(items=[item1, item2])
        
        # Then
        assert len(order.items) == 2
        assert order.items[0] == item1
        assert order.items[1] == item2
    
    def test_order_factory_total_amount_calculation(self):
        """OrderFactory로 생성된 주문의 총액이 올바르게 계산된다."""
        # Given
        food = FoodFactory(price=10000)
        item1 = OrderItemFactory(food=food, quantity=2, price=10000)
        item2 = OrderItemFactory(food=food, quantity=1, price=10000)
        
        # When
        order = OrderFactory(items=[item1, item2])
        
        # Then
        assert order.total_amount == 30000  # (2*10000) + (1*10000)