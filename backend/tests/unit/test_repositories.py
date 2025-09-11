"""
Unit tests for repository implementations.
"""
import pytest
from django.db import transaction
from django.test import TransactionTestCase

from infrastructure.database.repositories import (
    DjangoFoodRepository,
    DjangoTableRepository, 
    DjangoOrderRepository
)
from infrastructure.database.models import FoodModel, TableModel, OrderModel
from tests.factories.model_factories import (
    FoodModelFactory,
    SoldOutFoodModelFactory,
    TableModelFactory,
    OrderModelFactory,
    OrderItemModelFactory
)
from tests.factories.entity_factories import (
    FoodFactory,
    TableFactory,
    OrderFactory,
    OrderItemFactory
)


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.django_db(transaction=True)
class TestDjangoFoodRepository:
    """Test cases for DjangoFoodRepository."""
    
    def test_get_all_foods(self):
        """모든 음식을 조회할 수 있다."""
        # Given
        FoodModelFactory.create_batch(3)
        repository = DjangoFoodRepository()
        
        # When
        foods = repository.get_all()
        
        # Then
        assert len(foods) == 3
        assert all(food.name for food in foods)
    
    def test_get_food_by_id_existing(self):
        """존재하는 음식 ID로 조회할 수 있다."""
        # Given
        food_model = FoodModelFactory()
        repository = DjangoFoodRepository()
        
        # When
        food = repository.get_by_id(food_model.id)
        
        # Then
        assert food is not None
        assert food.id == food_model.id
        assert food.name == food_model.name
    
    def test_get_food_by_id_non_existing(self):
        """존재하지 않는 음식 ID로 조회하면 None을 반환한다."""
        # Given
        repository = DjangoFoodRepository()
        
        # When
        food = repository.get_by_id(999)
        
        # Then
        assert food is None
    
    def test_get_by_category_menu(self):
        """메뉴 카테고리로 음식을 필터링할 수 있다."""
        # Given
        FoodModelFactory(category='main')
        FoodModelFactory(category='side')
        repository = DjangoFoodRepository()
        
        # When
        from domain.entities.food import FoodCategory
        foods = repository.get_by_category(FoodCategory.MAIN)
        
        # Then
        assert len(foods) == 1
        assert foods[0].category.value == 'main'
    
    def test_get_by_ids_for_update(self):
        """select_for_update로 여러 음식을 조회할 수 있다."""
        # Given
        food1 = FoodModelFactory()
        food2 = FoodModelFactory()
        food3 = FoodModelFactory()
        repository = DjangoFoodRepository()
        
        # When
        with transaction.atomic():
            foods = repository.get_by_ids_for_update([food1.id, food2.id])
        
        # Then
        assert len(foods) == 2
        food_ids = [food.id for food in foods]
        assert food1.id in food_ids
        assert food2.id in food_ids
        assert food3.id not in food_ids
    
    def test_create_food(self):
        """음식을 생성할 수 있다."""
        # Given
        food_entity = FoodFactory()
        repository = DjangoFoodRepository()
        
        # When
        created_food = repository.create(food_entity)
        
        # Then
        assert created_food.id is not None
        assert created_food.name == food_entity.name
        assert created_food.price == food_entity.price
        
        # DB에 실제로 저장되었는지 확인
        db_food = FoodModel.objects.get(id=created_food.id)
        assert db_food.name == food_entity.name


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.django_db(transaction=True)
class TestDjangoTableRepository:
    """Test cases for DjangoTableRepository."""
    
    def test_get_all_tables(self):
        """모든 테이블을 조회할 수 있다."""
        # Given
        TableModelFactory.create_batch(2)
        repository = DjangoTableRepository()
        
        # When
        tables = repository.get_all()
        
        # Then
        assert len(tables) == 2
    
    def test_get_table_by_id_existing(self):
        """존재하는 테이블 ID로 조회할 수 있다."""
        # Given
        table_model = TableModelFactory()
        repository = DjangoTableRepository()
        
        # When
        table = repository.get_by_id(str(table_model.id))
        
        # Then
        assert table is not None
        assert table.id == str(table_model.id)
        assert table.name == table_model.name
    
    def test_create_table(self):
        """테이블을 생성할 수 있다."""
        # Given
        table_entity = TableFactory()
        repository = DjangoTableRepository()
        
        # When
        created_table = repository.create(table_entity)
        
        # Then
        assert created_table.id == table_entity.id
        assert created_table.name == table_entity.name
        
        # DB에 실제로 저장되었는지 확인
        db_table = TableModel.objects.get(id=table_entity.id)
        assert db_table.name == table_entity.name


@pytest.mark.unit
@pytest.mark.database
@pytest.mark.django_db(transaction=True)
class TestDjangoOrderRepository:
    """Test cases for DjangoOrderRepository."""
    
    def test_get_all_visible_orders(self):
        """표시 가능한 모든 주문을 조회할 수 있다."""
        # Given
        visible_order = OrderModelFactory(is_visible=True)
        hidden_order = OrderModelFactory(is_visible=False)
        repository = DjangoOrderRepository()
        
        # When
        orders = repository.get_all()
        
        # Then
        assert len(orders) == 1
        assert orders[0].id == str(visible_order.id)
    
    def test_get_order_by_id(self):
        """주문 ID로 조회할 수 있다."""
        # Given
        order_model = OrderModelFactory()
        OrderItemModelFactory(order=order_model)
        repository = DjangoOrderRepository()
        
        # When
        order = repository.get_by_id(str(order_model.id))
        
        # Then
        assert order is not None
        assert order.id == str(order_model.id)
        assert len(order.items) == 1
    
    def test_create_order(self):
        """주문을 생성할 수 있다."""
        # Given
        table_model = TableModelFactory()
        food_model = FoodModelFactory()
        
        # Table 엔티티 생성
        table_entity = TableFactory(
            id=str(table_model.id),
            name=table_model.name
        )
        
        # Food 엔티티 생성
        food_entity = FoodFactory(
            id=food_model.id,
            name=food_model.name,
            price=food_model.price,
            category=food_model.category,
            sold_out=food_model.sold_out
        )
        
        # OrderItem 엔티티 생성
        order_item = OrderItemFactory(
            food=food_entity,
            quantity=2,
            price=food_model.price
        )
        
        # Order 엔티티 생성
        order_entity = OrderFactory(
            table=table_entity,
            items=[order_item]
        )
        repository = DjangoOrderRepository()
        
        # When
        created_order = repository.create(order_entity)
        
        # Then
        assert created_order.id == order_entity.id
        assert created_order.table.id == str(table_model.id)
        assert len(created_order.items) == 1
        
        # DB에 실제로 저장되었는지 확인
        db_order = OrderModel.objects.get(id=order_entity.id)
        assert str(db_order.id) == order_entity.id
    
    def test_get_orders_by_table_id(self):
        """테이블 ID로 주문들을 조회할 수 있다."""
        # Given
        table1 = TableModelFactory()
        table2 = TableModelFactory()
        order1 = OrderModelFactory(table=table1, is_visible=True)
        order2 = OrderModelFactory(table=table1, is_visible=True)
        order3 = OrderModelFactory(table=table2, is_visible=True)
        repository = DjangoOrderRepository()
        
        # When
        orders = repository.get_by_table_id(str(table1.id))
        
        # Then
        assert len(orders) == 2
        order_ids = [order.id for order in orders]
        assert str(order1.id) in order_ids
        assert str(order2.id) in order_ids
        assert str(order3.id) not in order_ids
    
    def test_update_discord_notification_status(self):
        """Discord 알림 상태를 업데이트할 수 있다."""
        # Given
        order_model = OrderModelFactory(discord_notified=False)
        repository = DjangoOrderRepository()
        
        # When
        result = repository.update_discord_notification_status(str(order_model.id), True)
        
        # Then
        assert result is True
        order_model.refresh_from_db()
        assert order_model.discord_notified is True
    
    def test_order_items_filtering_with_minus_items(self):
        """minus order items가 있는 경우 해당 order items가 제외된다."""
        # Given
        table_model = TableModelFactory()
        food1 = FoodModelFactory(name="음식1", price=10000)
        food2 = FoodModelFactory(name="음식2", price=15000)
        food3 = FoodModelFactory(name="음식3", price=8000)
        
        order_model = OrderModelFactory(table=table_model)
        
        # Order items 생성
        OrderItemModelFactory(order=order_model, food=food1, quantity=2, price=10000)  # 20,000원
        OrderItemModelFactory(order=order_model, food=food2, quantity=1, price=15000)  # 15,000원
        OrderItemModelFactory(order=order_model, food=food3, quantity=3, price=8000)   # 24,000원
        
        # Minus order items 생성 (food1과 food3에 대해)
        from tests.factories.model_factories import MinusOrderItemModelFactory
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-1, price=10000, reason='sold_out')  # -10,000원
        MinusOrderItemModelFactory(order=order_model, food=food3, quantity=-3, price=8000, reason='unavailable')  # -24,000원
        
        repository = DjangoOrderRepository()
        
        # When
        order = repository.get_by_id(str(order_model.id))
        
        # Then
        assert order is not None
        assert len(order.items) == 2  # food1(수량1개), food2(수량1개)만 남아야 함
        
        # food1: 원래 2개 - 1개 = 1개 남음
        food1_item = next((item for item in order.items if item.food.id == food1.id), None)
        assert food1_item is not None
        assert food1_item.quantity == 1
        
        # food2: 차감 없음, 그대로 1개
        food2_item = next((item for item in order.items if item.food.id == food2.id), None)
        assert food2_item is not None
        assert food2_item.quantity == 1
        
        # food3: 원래 3개 - 3개 = 0개, 제외됨
        food3_item = next((item for item in order.items if item.food.id == food3.id), None)
        assert food3_item is None
    
    def test_total_amount_calculation_with_minus_items(self):
        """minus order items가 있는 경우 총액이 올바르게 계산된다."""
        # Given
        table_model = TableModelFactory()
        food1 = FoodModelFactory(name="음식1", price=10000)
        food2 = FoodModelFactory(name="음식2", price=15000)
        
        order_model = OrderModelFactory(table=table_model, status='completed', pre_order_amount=None)
        
        # Order items: 총 35,000원
        OrderItemModelFactory(order=order_model, food=food1, quantity=2, price=10000)  # 20,000원
        OrderItemModelFactory(order=order_model, food=food2, quantity=1, price=15000)  # 15,000원
        
        # Minus order items: -10,000원 차감
        from tests.factories.model_factories import MinusOrderItemModelFactory
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-1, price=10000, reason='sold_out')
        
        repository = DjangoOrderRepository()
        
        # When
        order = repository.get_by_id(str(order_model.id))
        
        # Then
        # 예상 총액: food1(1개 * 10,000원) + food2(1개 * 15,000원) = 25,000원
        assert order.total_amount == 25000
        assert order.effective_total_amount == 25000
    
    def test_pre_order_total_amount_not_affected_by_minus_items(self):
        """pre-order의 경우 minus items가 있어도 pre_order_amount를 사용한다."""
        # Given
        table_model = TableModelFactory()
        food1 = FoodModelFactory(name="음식1", price=10000)
        
        order_model = OrderModelFactory(
            table=table_model, 
            status='pre_order', 
            pre_order_amount=50000
        )
        
        # Order items와 minus order items 생성
        OrderItemModelFactory(order=order_model, food=food1, quantity=2, price=10000)
        from tests.factories.model_factories import MinusOrderItemModelFactory
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-1, price=10000, reason='sold_out')
        
        repository = DjangoOrderRepository()
        
        # When
        order = repository.get_by_id(str(order_model.id))
        
        # Then
        # pre-order의 경우 pre_order_amount 사용
        assert order.total_amount == 50000
        assert order.effective_total_amount is None  # pre-order는 effective_total_amount 계산 안 함
    
    def test_order_items_partial_quantity_reduction(self):
        """minus order items로 수량이 부분적으로 차감되는 경우."""
        # Given
        table_model = TableModelFactory()
        food1 = FoodModelFactory(name="음식1", price=10000)
        
        order_model = OrderModelFactory(table=table_model, status='completed', pre_order_amount=None)
        
        # Order items: 5개
        OrderItemModelFactory(order=order_model, food=food1, quantity=5, price=10000)
        
        # Minus order items: 2개 차감
        from tests.factories.model_factories import MinusOrderItemModelFactory
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-2, price=10000, reason='damaged')
        
        repository = DjangoOrderRepository()
        
        # When
        order = repository.get_by_id(str(order_model.id))
        
        # Then
        assert len(order.items) == 1
        assert order.items[0].quantity == 3  # 5 - 2 = 3
        assert order.total_amount == 30000  # 3 * 10,000원
    
    def test_multiple_minus_items_for_same_food(self):
        """같은 음식에 대해 여러 minus order items가 있는 경우."""
        # Given
        table_model = TableModelFactory()
        food1 = FoodModelFactory(name="음식1", price=10000)
        
        order_model = OrderModelFactory(table=table_model, status='completed', pre_order_amount=None)
        
        # Order items: 10개
        OrderItemModelFactory(order=order_model, food=food1, quantity=10, price=10000)
        
        # 여러 minus order items: 총 6개 차감
        from tests.factories.model_factories import MinusOrderItemModelFactory
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-3, price=10000, reason='sold_out')
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-2, price=10000, reason='damaged')
        MinusOrderItemModelFactory(order=order_model, food=food1, quantity=-1, price=10000, reason='unavailable')
        
        repository = DjangoOrderRepository()
        
        # When
        order = repository.get_by_id(str(order_model.id))
        
        # Then
        assert len(order.items) == 1
        assert order.items[0].quantity == 4  # 10 - (3+2+1) = 4
        assert order.total_amount == 40000  # 4 * 10,000원