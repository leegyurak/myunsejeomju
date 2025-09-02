"""
Unit tests for domain entities.
"""
import pytest
from datetime import datetime
from django.utils import timezone

from domain.entities.food import Food, FoodCategory
from domain.entities.table import Table
from domain.entities.order import Order, OrderItem, MinusOrderItem
from tests.factories.entity_factories import (
    FoodFactory,
    TableFactory,
    OrderFactory,
    OrderItemFactory,
    MinusOrderItemFactory
)


@pytest.mark.unit
class TestFood:
    """Test cases for Food entity."""
    
    def test_create_food(self):
        """음식 엔티티를 생성할 수 있다."""
        # Given & When
        food = Food(
            id=1,
            name="비빔밥",
            price=12000,
            category=FoodCategory.MENU,
            description="맛있는 비빔밥",
            image="http://example.com/bibimbap.jpg",
            sold_out=False
        )
        
        # Then
        assert food.id == 1
        assert food.name == "비빔밥"
        assert food.price == 12000
        assert food.category == FoodCategory.MENU
        assert food.description == "맛있는 비빔밥"
        assert food.image == "http://example.com/bibimbap.jpg"
        assert food.sold_out is False
    
    def test_food_category_enum(self):
        """음식 카테고리 열거형이 올바르게 작동한다."""
        # Given & When & Then
        assert FoodCategory.MENU.value == "menu"
        assert FoodCategory.DRINKS.value == "drinks"
        
        # 문자열로 카테고리 생성 가능
        menu_category = FoodCategory("menu")
        drinks_category = FoodCategory("drinks")
        
        assert menu_category == FoodCategory.MENU
        assert drinks_category == FoodCategory.DRINKS
    
    def test_food_factory(self):
        """음식 팩토리가 올바르게 작동한다."""
        # Given & When
        food = FoodFactory()
        
        # Then
        assert food.id is not None
        assert food.name is not None
        assert food.price > 0
        assert food.category in [FoodCategory.MENU, FoodCategory.DRINKS]
        assert food.description is not None
        assert food.image is not None
        assert isinstance(food.sold_out, bool)


@pytest.mark.unit
class TestTable:
    """Test cases for Table entity."""
    
    def test_create_table(self):
        """테이블 엔티티를 생성할 수 있다."""
        # Given
        now = timezone.now()
        
        # When
        table = Table(
            id="table-123",
            name="테이블1",
            created_at=now,
            updated_at=now
        )
        
        # Then
        assert table.id == "table-123"
        assert table.name == "테이블1"
        assert table.created_at == now
        assert table.updated_at == now
    
    def test_table_factory(self):
        """테이블 팩토리가 올바르게 작동한다."""
        # Given & When
        table = TableFactory()
        
        # Then
        assert table.id is not None
        assert table.name is not None
        assert table.created_at is not None
        assert table.updated_at is not None
        assert isinstance(table.id, str)


@pytest.mark.unit
class TestOrderItem:
    """Test cases for OrderItem entity."""
    
    def test_create_order_item(self):
        """주문 아이템을 생성할 수 있다."""
        # Given
        food = FoodFactory(price=10000)
        
        # When
        order_item = OrderItem(
            food=food,
            quantity=3,
            price=10000
        )
        
        # Then
        assert order_item.food == food
        assert order_item.quantity == 3
        assert order_item.price == 10000
    
    def test_order_item_total_price(self):
        """주문 아이템 총 가격을 계산할 수 있다."""
        # Given
        food = FoodFactory(price=10000)
        order_item = OrderItem(
            food=food,
            quantity=3,
            price=10000
        )
        
        # When & Then
        assert order_item.total_price == 30000
    
    def test_order_item_factory(self):
        """주문 아이템 팩토리가 올바르게 작동한다."""
        # Given & When
        order_item = OrderItemFactory()
        
        # Then
        assert order_item.food is not None
        assert order_item.quantity > 0
        assert order_item.price > 0
        assert order_item.total_price == order_item.quantity * order_item.price


@pytest.mark.unit
class TestMinusOrderItem:
    """Test cases for MinusOrderItem entity."""
    
    def test_create_minus_order_item(self):
        """마이너스 주문 아이템을 생성할 수 있다."""
        # Given
        food = FoodFactory(price=10000)
        
        # When
        minus_item = MinusOrderItem(
            food=food,
            quantity=-2,
            price=10000,
            reason="sold_out"
        )
        
        # Then
        assert minus_item.food == food
        assert minus_item.quantity == -2
        assert minus_item.price == 10000
        assert minus_item.reason == "sold_out"
    
    def test_minus_order_item_total_price(self):
        """마이너스 주문 아이템 총 가격을 계산할 수 있다."""
        # Given
        food = FoodFactory(price=10000)
        minus_item = MinusOrderItem(
            food=food,
            quantity=-2,
            price=10000,
            reason="sold_out"
        )
        
        # When & Then
        assert minus_item.total_price == -20000
    
    def test_minus_order_item_factory(self):
        """마이너스 주문 아이템 팩토리가 올바르게 작동한다."""
        # Given & When
        minus_item = MinusOrderItemFactory()
        
        # Then
        assert minus_item.food is not None
        assert minus_item.quantity < 0
        assert minus_item.price > 0
        assert minus_item.reason in ["sold_out", "unavailable", "damaged"]


@pytest.mark.unit
class TestOrder:
    """Test cases for Order entity."""
    
    def test_create_order(self):
        """주문을 생성할 수 있다."""
        # Given
        table = TableFactory()
        food = FoodFactory(price=10000)
        order_item = OrderItem(food=food, quantity=2, price=10000)
        now = timezone.now()
        
        # When
        order = Order(
            id="order-123",
            table=table,
            order_date=now,
            items=[order_item],
            status="completed"
        )
        
        # Then
        assert order.id == "order-123"
        assert order.table == table
        assert order.order_date == now
        assert len(order.items) == 1
        assert order.items[0] == order_item
        assert order.status == "completed"
    
    def test_order_total_amount_from_items(self):
        """주문 총액을 아이템들로부터 계산할 수 있다."""
        # Given
        table = TableFactory()
        food1 = FoodFactory(price=10000)
        food2 = FoodFactory(price=15000)
        
        order_item1 = OrderItem(food=food1, quantity=2, price=10000)
        order_item2 = OrderItem(food=food2, quantity=1, price=15000)
        
        order = Order(
            id="order-123",
            table=table,
            order_date=timezone.now(),
            items=[order_item1, order_item2]
        )
        
        # When & Then
        assert order.total_amount == 35000  # (10000*2) + (15000*1)
    
    def test_order_total_amount_with_pre_order_amount(self):
        """선주문 금액이 있는 경우 해당 금액을 사용한다."""
        # Given
        table = TableFactory()
        food = FoodFactory(price=10000)
        order_item = OrderItem(food=food, quantity=2, price=10000)
        
        order = Order(
            id="order-123",
            table=table,
            order_date=timezone.now(),
            items=[order_item],
            pre_order_amount=25000  # 실제 아이템 총액보다 높게 설정
        )
        
        # When & Then
        assert order.total_amount == 25000  # pre_order_amount를 사용
    
    def test_order_total_amount_with_minus_items(self):
        """마이너스 아이템이 있는 경우 총액에서 차감된다."""
        # Given
        table = TableFactory()
        food = FoodFactory(price=10000)
        
        order_item = OrderItem(food=food, quantity=3, price=10000)
        minus_item = MinusOrderItem(food=food, quantity=-1, price=10000, reason="sold_out")
        
        order = Order(
            id="order-123",
            table=table,
            order_date=timezone.now(),
            items=[order_item],
            minus_items=[minus_item]
        )
        
        # When & Then
        assert order.total_amount == 20000  # (30000) + (-10000)
    
    def test_order_factory(self):
        """주문 팩토리가 올바르게 작동한다."""
        # Given & When
        order = OrderFactory()
        
        # Then
        assert order.id is not None
        assert order.table is not None
        assert order.order_date is not None
        assert order.items is not None
        assert len(order.items) > 0
        assert order.status == "completed"
        assert order.is_visible is True
        assert order.discord_notified is False
    
    def test_order_with_payer_name(self):
        """결제자 이름이 있는 주문을 생성할 수 있다."""
        # Given
        table = TableFactory()
        
        # When
        order = Order(
            id="order-123",
            table=table,
            order_date=timezone.now(),
            items=[],
            payer_name="홍길동"
        )
        
        # Then
        assert order.payer_name == "홍길동"
    
    def test_order_visibility(self):
        """주문 가시성을 설정할 수 있다."""
        # Given
        table = TableFactory()
        
        # When
        visible_order = Order(
            id="order-1",
            table=table,
            order_date=timezone.now(),
            items=[],
            is_visible=True
        )
        
        hidden_order = Order(
            id="order-2",
            table=table,
            order_date=timezone.now(),
            items=[],
            is_visible=False
        )
        
        # Then
        assert visible_order.is_visible is True
        assert hidden_order.is_visible is False
    
    def test_order_discord_notification_status(self):
        """Discord 알림 상태를 설정할 수 있다."""
        # Given
        table = TableFactory()
        
        # When
        order = Order(
            id="order-1",
            table=table,
            order_date=timezone.now(),
            items=[],
            discord_notified=True
        )
        
        # Then
        assert order.discord_notified is True