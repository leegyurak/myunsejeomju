"""
Unit tests for order domain service.
"""
import pytest
from unittest.mock import Mock

from domain.services.order_service import OrderDomainService, TransactionManager
from tests.factories.entity_factories import FoodFactory, SoldOutFoodFactory, OrderFactory


@pytest.mark.unit
class TestTransactionManager:
    """Test cases for TransactionManager interface."""
    
    def test_transaction_manager_is_abstract(self):
        """TransactionManager는 추상 클래스이다."""
        # Given & When & Then
        with pytest.raises(TypeError):
            TransactionManager()


@pytest.mark.unit
class TestOrderDomainService:
    """Test cases for OrderDomainService."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_transaction_manager = Mock(spec=TransactionManager)
        self.service = OrderDomainService(self.mock_transaction_manager)
    
    def test_validate_food_availability_with_available_foods(self):
        """사용 가능한 음식들로만 구성된 주문은 검증을 통과한다."""
        # Given
        food1 = FoodFactory(id=1, name="비빔밥", sold_out=False)
        food2 = FoodFactory(id=2, name="냉면", sold_out=False)
        foods = [food1, food2]
        
        order_items = [
            {'food_id': 1, 'quantity': 2},
            {'food_id': 2, 'quantity': 1}
        ]
        
        # When & Then (예외가 발생하지 않아야 함)
        self.service.validate_food_availability(foods, order_items)
    
    def test_validate_food_availability_with_sold_out_food(self):
        """품절된 음식이 포함된 주문은 검증에 실패한다."""
        # Given
        available_food = FoodFactory(id=1, name="비빔밥", sold_out=False)
        sold_out_food = SoldOutFoodFactory(id=2, name="냉면")
        foods = [available_food, sold_out_food]
        
        order_items = [
            {'food_id': 1, 'quantity': 2},
            {'food_id': 2, 'quantity': 1}  # 품절된 음식
        ]
        
        # When & Then
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_food_availability(foods, order_items)
        
        assert "품절되었습니다" in str(exc_info.value)
        assert "냉면" in str(exc_info.value)
    
    def test_validate_food_availability_with_multiple_sold_out_foods(self):
        """여러 품절 음식이 포함된 경우 모든 품절 음식을 나열한다."""
        # Given
        available_food = FoodFactory(id=1, name="비빔밥", sold_out=False)
        sold_out_food1 = SoldOutFoodFactory(id=2, name="냉면")
        sold_out_food2 = SoldOutFoodFactory(id=3, name="김치찌개")
        foods = [available_food, sold_out_food1, sold_out_food2]
        
        order_items = [
            {'food_id': 1, 'quantity': 1},
            {'food_id': 2, 'quantity': 1},  # 품절
            {'food_id': 3, 'quantity': 1}   # 품절
        ]
        
        # When & Then
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_food_availability(foods, order_items)
        
        error_message = str(exc_info.value)
        assert "품절되었습니다" in error_message
        assert "냉면" in error_message
        assert "김치찌개" in error_message
    
    def test_validate_food_availability_with_non_existent_food(self):
        """존재하지 않는 음식 ID가 포함된 경우 예외를 발생시킨다."""
        # Given
        food = FoodFactory(id=1, name="비빔밥", sold_out=False)
        foods = [food]
        
        order_items = [
            {'food_id': 1, 'quantity': 2},
            {'food_id': 999, 'quantity': 1}  # 존재하지 않는 ID
        ]
        
        # When & Then
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_food_availability(foods, order_items)
        
        assert "Food with id 999 not found" in str(exc_info.value)
    
    def test_validate_food_availability_with_empty_foods(self):
        """음식 목록이 비어있는 경우 존재하지 않는 음식 오류를 발생시킨다."""
        # Given
        foods = []
        order_items = [{'food_id': 1, 'quantity': 1}]
        
        # When & Then
        with pytest.raises(ValueError) as exc_info:
            self.service.validate_food_availability(foods, order_items)
        
        assert "Food with id 1 not found" in str(exc_info.value)
    
    def test_validate_food_availability_with_empty_order_items(self):
        """주문 아이템이 비어있는 경우 아무 오류 없이 통과한다."""
        # Given
        food = FoodFactory(id=1, name="비빔밥", sold_out=False)
        foods = [food]
        order_items = []
        
        # When & Then (예외가 발생하지 않아야 함)
        self.service.validate_food_availability(foods, order_items)
    
    def test_create_order_with_availability_check(self):
        """재고 체크와 함께 주문을 생성한다."""
        # Given
        expected_order = OrderFactory()
        
        def mock_create_order_func(arg1, arg2, kwarg1=None):
            return expected_order
        
        self.mock_transaction_manager.execute_in_transaction.return_value = expected_order
        
        # When
        result = self.service.create_order_with_availability_check(
            mock_create_order_func, "arg1", "arg2", kwarg1="kwarg1"
        )
        
        # Then
        assert result == expected_order
        self.mock_transaction_manager.execute_in_transaction.assert_called_once_with(
            mock_create_order_func, "arg1", "arg2", kwarg1="kwarg1"
        )
    
    def test_create_order_with_availability_check_handles_transaction_failure(self):
        """트랜잭션 실패 시 예외를 그대로 전파한다."""
        # Given
        def mock_create_order_func():
            return OrderFactory()
        
        transaction_error = Exception("Transaction failed")
        self.mock_transaction_manager.execute_in_transaction.side_effect = transaction_error
        
        # When & Then
        with pytest.raises(Exception) as exc_info:
            self.service.create_order_with_availability_check(mock_create_order_func)
        
        assert str(exc_info.value) == "Transaction failed"
        self.mock_transaction_manager.execute_in_transaction.assert_called_once()
    
    def test_service_initialization(self):
        """서비스가 트랜잭션 매니저와 함께 올바르게 초기화된다."""
        # Given & When
        service = OrderDomainService(self.mock_transaction_manager)
        
        # Then
        assert service.transaction_manager == self.mock_transaction_manager