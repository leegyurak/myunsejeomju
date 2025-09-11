"""
Unit tests for zero amount order filtering in use cases.
"""
import pytest
from unittest.mock import Mock
import uuid

from domain.use_cases.order_use_cases import GetOrdersByTableUseCase
from tests.factories.entity_factories import OrderFactory


@pytest.mark.unit
class TestGetOrdersByTableUseCaseZeroAmount:
    """Test cases for GetOrdersByTableUseCase with zero amount filtering."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_order_repository = Mock()
        self.use_case = GetOrdersByTableUseCase(self.mock_order_repository)
    
    def test_execute_returns_filtered_orders(self):
        """테이블별 주문 조회 시 0원 주문이 자동으로 필터링된다."""
        # Given
        table_id = str(uuid.uuid4())
        normal_order = OrderFactory()
        # Repository가 이미 0원 주문을 필터링하여 반환
        self.mock_order_repository.get_by_table_id.return_value = [normal_order]
        
        # When
        result = self.use_case.execute(table_id)
        
        # Then
        assert result == [normal_order]
        self.mock_order_repository.get_by_table_id.assert_called_once_with(table_id)
    
    def test_execute_with_empty_result(self):
        """모든 주문이 0원이어서 필터링된 경우 빈 리스트를 반환한다."""
        # Given
        table_id = str(uuid.uuid4())
        # Repository가 모든 주문을 필터링하여 빈 리스트 반환
        self.mock_order_repository.get_by_table_id.return_value = []
        
        # When
        result = self.use_case.execute(table_id)
        
        # Then
        assert result == []
        self.mock_order_repository.get_by_table_id.assert_called_once_with(table_id)