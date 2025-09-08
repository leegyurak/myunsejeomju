"""
Unit tests for use cases.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import uuid
from datetime import datetime

from domain.use_cases.order_use_cases import CreateOrderUseCase, CreatePreOrderUseCase
from domain.entities.food import Food, FoodCategory
from domain.entities.table import Table
from domain.entities.order import Order, OrderItem
from domain.services.order_service import TransactionManager
from tests.factories.entity_factories import (
    FoodFactory,
    SoldOutFoodFactory,
    TableFactory,
    OrderFactory
)


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
class TestCreateOrderUseCase:
    """Test cases for CreateOrderUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_order_repository = Mock()
        self.mock_food_repository = Mock()
        self.mock_table_repository = Mock()
        self.mock_transaction_manager = Mock(spec=TransactionManager)
        
        self.use_case = CreateOrderUseCase(
            self.mock_order_repository,
            self.mock_food_repository,
            self.mock_table_repository,
            self.mock_transaction_manager
        )
    
    def test_execute_successful_order_creation(self):
        """정상적인 주문 생성이 성공한다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [
            {'food_id': 1, 'quantity': 2},
            {'food_id': 2, 'quantity': 1}
        ]
        
        # Mock 설정
        table = TableFactory(id=table_id)
        food1 = FoodFactory(id=1, price=10000)
        food2 = FoodFactory(id=2, price=15000)
        order = OrderFactory()
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [food1, food2]
        self.mock_order_repository.create.return_value = order
        
        # transaction_manager가 전달받은 함수를 실행하도록 설정
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When
        result = self.use_case.execute(table_id, items_data)
        
        # Then
        assert result == order
        self.mock_table_repository.get_by_id.assert_called_once_with(table_id)
        self.mock_food_repository.get_by_ids_for_update.assert_called_once_with([1, 2])
        self.mock_order_repository.create.assert_called_once()
        self.mock_transaction_manager.execute_in_transaction.assert_called_once()
    
    def test_execute_table_not_found(self):
        """존재하지 않는 테이블 ID로 주문 시 에러가 발생한다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [{'food_id': 1, 'quantity': 1}]
        
        self.mock_table_repository.get_by_id.return_value = None
        
        # When & Then
        with pytest.raises(ValueError, match=f"Table with id {table_id} not found"):
            self.use_case.execute(table_id, items_data)
    
    def test_execute_food_not_found(self):
        """존재하지 않는 음식 ID로 주문 시 에러가 발생한다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [{'food_id': 999, 'quantity': 1}]
        
        table = TableFactory(id=table_id)
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = []
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When & Then
        with pytest.raises(ValueError, match="Food with id 999 not found"):
            self.use_case.execute(table_id, items_data)
    
    def test_execute_sold_out_food(self):
        """품절된 음식으로 주문 시 에러가 발생한다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [{'food_id': 1, 'quantity': 1}]
        
        table = TableFactory(id=table_id)
        sold_out_food = SoldOutFoodFactory(id=1, name="품절된음식")
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [sold_out_food]
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When & Then
        with pytest.raises(ValueError, match="음식 '품절된음식'이\\(가\\) 품절되었습니다"):
            self.use_case.execute(table_id, items_data)
    
    def test_execute_multiple_items_with_sold_out(self):
        """여러 음식 중 일부가 품절된 경우 에러가 발생한다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [
            {'food_id': 1, 'quantity': 1},
            {'food_id': 2, 'quantity': 1}
        ]
        
        table = TableFactory(id=table_id)
        available_food = FoodFactory(id=1, name="사용가능음식")
        sold_out_food = SoldOutFoodFactory(id=2, name="품절음식")
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [available_food, sold_out_food]
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When & Then
        with pytest.raises(ValueError, match="음식 '품절음식'이\\(가\\) 품절되었습니다"):
            self.use_case.execute(table_id, items_data)
    
    def test_execute_order_items_creation(self):
        """주문 아이템이 올바르게 생성된다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [
            {'food_id': 1, 'quantity': 2},
            {'food_id': 2, 'quantity': 1}
        ]
        
        table = TableFactory(id=table_id)
        food1 = FoodFactory(id=1, price=10000)
        food2 = FoodFactory(id=2, price=15000)
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [food1, food2]
        self.mock_order_repository.create.return_value = OrderFactory()
        
        created_order_entity = None
        def capture_order_entity(order_entity):
            nonlocal created_order_entity
            created_order_entity = order_entity
            return order_entity
        
        self.mock_order_repository.create.side_effect = capture_order_entity
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When
        self.use_case.execute(table_id, items_data)
        
        # Then
        assert created_order_entity is not None
        assert len(created_order_entity.items) == 2
        
        # 첫 번째 아이템 검증
        item1 = created_order_entity.items[0]
        assert item1.food.id == 1
        assert item1.quantity == 2
        assert item1.price == 10000
        
        # 두 번째 아이템 검증
        item2 = created_order_entity.items[1]
        assert item2.food.id == 2
        assert item2.quantity == 1
        assert item2.price == 15000
        
        # 주문 기본 정보 검증
        assert created_order_entity.table.id == table_id
        assert created_order_entity.status == 'completed'
        assert created_order_entity.id is not None
    
    def test_execute_transaction_rollback(self):
        """트랜잭션 실행 중 오류 발생 시 롤백된다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [{'food_id': 1, 'quantity': 1}]
        
        table = TableFactory(id=table_id)
        food = FoodFactory(id=1)
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [food]
        
        # 주문 생성에서 예외 발생하도록 설정
        self.mock_order_repository.create.side_effect = Exception("Database error")
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When & Then
        with pytest.raises(Exception, match="Database error"):
            self.use_case.execute(table_id, items_data)
    
    def test_execute_first_order_requires_main_menu(self):
        """테이블의 첫 번째 주문에는 메인 메뉴가 반드시 포함되어야 한다."""
        # Given
        table_id = str(uuid.uuid4())
        # 사이드 메뉴만 주문하는 경우
        items_data = [{'food_id': 1, 'quantity': 1}]
        
        table = TableFactory(id=table_id)
        side_food = FoodFactory(id=1, category=FoodCategory.SIDE, name="사이다")
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [side_food]
        # 테이블에 기존 주문이 없음 (첫 주문)
        self.mock_order_repository.get_by_table_id.return_value = []
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When & Then
        with pytest.raises(ValueError, match="첫 주문에는 반드시 메인 메뉴가 하나 이상 포함되어야 합니다."):
            self.use_case.execute(table_id, items_data)
    
    def test_execute_first_order_with_main_menu_succeeds(self):
        """테이블의 첫 번째 주문에 메인 메뉴가 포함되면 성공한다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [
            {'food_id': 1, 'quantity': 1},  # 메인 메뉴
            {'food_id': 2, 'quantity': 1}   # 사이드 메뉴
        ]
        
        table = TableFactory(id=table_id)
        main_food = FoodFactory(id=1, category=FoodCategory.MAIN, name="비빔밥")
        side_food = FoodFactory(id=2, category=FoodCategory.SIDE, name="콜라")
        order = OrderFactory()
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [main_food, side_food]
        # 테이블에 기존 주문이 없음 (첫 주문)
        self.mock_order_repository.get_by_table_id.return_value = []
        self.mock_order_repository.create.return_value = order
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When
        result = self.use_case.execute(table_id, items_data)
        
        # Then
        assert result == order
        self.mock_order_repository.create.assert_called_once()
    
    def test_execute_second_order_can_be_side_only(self):
        """테이블의 두 번째 이후 주문은 사이드 메뉴만 주문해도 된다."""
        # Given
        table_id = str(uuid.uuid4())
        items_data = [{'food_id': 1, 'quantity': 1}]  # 사이드 메뉴만
        
        table = TableFactory(id=table_id)
        side_food = FoodFactory(id=1, category=FoodCategory.SIDE, name="콜라")
        existing_order = OrderFactory()
        order = OrderFactory()
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_ids_for_update.return_value = [side_food]
        # 테이블에 기존 주문이 있음 (첫 주문이 아님)
        self.mock_order_repository.get_by_table_id.return_value = [existing_order]
        self.mock_order_repository.create.return_value = order
        
        def execute_transaction(func):
            return func()
        self.mock_transaction_manager.execute_in_transaction.side_effect = execute_transaction
        
        # When
        result = self.use_case.execute(table_id, items_data)
        
        # Then
        assert result == order
        self.mock_order_repository.create.assert_called_once()


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
class TestCreatePreOrderUseCase:
    """Test cases for CreatePreOrderUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_order_repository = Mock()
        self.mock_food_repository = Mock()
        self.mock_table_repository = Mock()
        
        self.use_case = CreatePreOrderUseCase(
            self.mock_order_repository,
            self.mock_table_repository,
            self.mock_food_repository
        )
    
    def test_execute_first_pre_order_requires_main_menu(self):
        """테이블의 첫 번째 선주문에는 메인 메뉴가 반드시 포함되어야 한다."""
        # Given
        table_id = str(uuid.uuid4())
        payer_name = "홍길동"
        total_amount = 5000
        # 사이드 메뉴만 주문하는 경우
        items_data = [{'food_id': 1, 'quantity': 1}]
        
        table = TableFactory(id=table_id)
        side_food = FoodFactory(id=1, category=FoodCategory.SIDE, name="콜라")
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_id.return_value = side_food
        # 테이블에 기존 주문이 없음 (첫 주문)
        self.mock_order_repository.get_by_table_id.return_value = []
        
        # When & Then
        with pytest.raises(ValueError, match="첫 주문에는 반드시 메인 메뉴가 하나 이상 포함되어야 합니다."):
            self.use_case.execute(table_id, payer_name, total_amount, items_data)
    
    def test_execute_first_pre_order_with_main_menu_succeeds(self):
        """테이블의 첫 번째 선주문에 메인 메뉴가 포함되면 성공한다."""
        # Given
        table_id = str(uuid.uuid4())
        payer_name = "홍길동"
        total_amount = 15000
        items_data = [
            {'food_id': 1, 'quantity': 1},  # 메인 메뉴
            {'food_id': 2, 'quantity': 1}   # 사이드 메뉴
        ]
        
        table = TableFactory(id=table_id)
        main_food = FoodFactory(id=1, category=FoodCategory.MAIN, name="비빔밥")
        side_food = FoodFactory(id=2, category=FoodCategory.SIDE, name="콜라")
        order = OrderFactory()
        
        self.mock_table_repository.get_by_id.return_value = table
        # 첫 번째 호출은 메인 메뉴, 두 번째 호출은 사이드 메뉴 반환
        self.mock_food_repository.get_by_id.side_effect = [main_food, main_food, side_food]
        # 테이블에 기존 주문이 없음 (첫 주문)
        self.mock_order_repository.get_by_table_id.return_value = []
        self.mock_order_repository.create.return_value = order
        
        # When
        result = self.use_case.execute(table_id, payer_name, total_amount, items_data)
        
        # Then
        assert result == order
        self.mock_order_repository.create.assert_called_once()
    
    def test_execute_second_pre_order_can_be_side_only(self):
        """테이블의 두 번째 이후 선주문은 사이드 메뉴만 주문해도 된다."""
        # Given
        table_id = str(uuid.uuid4())
        payer_name = "홍길동"
        total_amount = 3000
        items_data = [{'food_id': 1, 'quantity': 1}]  # 사이드 메뉴만
        
        table = TableFactory(id=table_id)
        side_food = FoodFactory(id=1, category=FoodCategory.SIDE, name="콜라")
        existing_order = OrderFactory()
        order = OrderFactory()
        
        self.mock_table_repository.get_by_id.return_value = table
        self.mock_food_repository.get_by_id.return_value = side_food
        # 테이블에 기존 주문이 있음 (첫 주문이 아님)
        self.mock_order_repository.get_by_table_id.return_value = [existing_order]
        self.mock_order_repository.create.return_value = order
        
        # When
        result = self.use_case.execute(table_id, payer_name, total_amount, items_data)
        
        # Then
        assert result == order
        self.mock_order_repository.create.assert_called_once()