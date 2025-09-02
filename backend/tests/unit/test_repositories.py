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
        FoodModelFactory(category='menu')
        FoodModelFactory(category='drinks')
        repository = DjangoFoodRepository()
        
        # When
        from domain.entities.food import FoodCategory
        foods = repository.get_by_category(FoodCategory.MENU)
        
        # Then
        assert len(foods) == 1
        assert foods[0].category.value == 'menu'
    
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