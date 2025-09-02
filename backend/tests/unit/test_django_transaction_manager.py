"""
Unit tests for Django transaction manager.
"""
import pytest
from unittest.mock import Mock, patch
from django.test import TransactionTestCase

from infrastructure.transaction.django_transaction_manager import DjangoTransactionManager
from domain.services.order_service import TransactionManager


@pytest.mark.unit
@pytest.mark.django_db(transaction=True)
class TestDjangoTransactionManager(TransactionTestCase):
    """Test cases for DjangoTransactionManager."""
    
    def setUp(self):
        """각 테스트 실행 전 설정."""
        self.transaction_manager = DjangoTransactionManager()
    
    def test_implements_transaction_manager_interface(self):
        """DjangoTransactionManager는 TransactionManager 인터페이스를 구현한다."""
        # Given & When & Then
        assert isinstance(self.transaction_manager, TransactionManager)
    
    def test_execute_in_transaction_runs_function(self):
        """트랜잭션 내에서 함수를 실행한다."""
        # Given
        mock_func = Mock(return_value="success")
        args = ("arg1", "arg2")
        kwargs = {"kwarg1": "value1", "kwarg2": "value2"}
        
        # When
        result = self.transaction_manager.execute_in_transaction(
            mock_func, *args, **kwargs
        )
        
        # Then
        assert result == "success"
        mock_func.assert_called_once_with(*args, **kwargs)
    
    def test_execute_in_transaction_returns_function_result(self):
        """트랜잭션 내에서 실행된 함수의 결과를 반환한다."""
        # Given
        expected_result = {"status": "created", "id": 123}
        mock_func = Mock(return_value=expected_result)
        
        # When
        result = self.transaction_manager.execute_in_transaction(mock_func)
        
        # Then
        assert result == expected_result
    
    def test_execute_in_transaction_propagates_exceptions(self):
        """트랜잭션 내에서 발생한 예외를 전파한다."""
        # Given
        def failing_function():
            raise ValueError("Something went wrong")
        
        # When & Then
        with pytest.raises(ValueError) as exc_info:
            self.transaction_manager.execute_in_transaction(failing_function)
        
        assert str(exc_info.value) == "Something went wrong"
    
    @patch('infrastructure.transaction.django_transaction_manager.transaction.atomic')
    def test_execute_in_transaction_uses_django_atomic(self, mock_atomic):
        """Django의 transaction.atomic을 사용한다."""
        # Given
        mock_func = Mock(return_value="result")
        mock_atomic.return_value.__enter__ = Mock()
        mock_atomic.return_value.__exit__ = Mock()
        
        # When
        self.transaction_manager.execute_in_transaction(mock_func)
        
        # Then
        mock_atomic.assert_called_once()
    
    def test_execute_in_transaction_with_no_arguments(self):
        """인자 없이 함수를 실행할 수 있다."""
        # Given
        mock_func = Mock(return_value="no_args_result")
        
        # When
        result = self.transaction_manager.execute_in_transaction(mock_func)
        
        # Then
        assert result == "no_args_result"
        mock_func.assert_called_once_with()
    
    def test_execute_in_transaction_with_only_args(self):
        """위치 인자만으로 함수를 실행할 수 있다."""
        # Given
        mock_func = Mock(return_value="args_only")
        args = ("arg1", "arg2", "arg3")
        
        # When
        result = self.transaction_manager.execute_in_transaction(mock_func, *args)
        
        # Then
        assert result == "args_only"
        mock_func.assert_called_once_with(*args)
    
    def test_execute_in_transaction_with_only_kwargs(self):
        """키워드 인자만으로 함수를 실행할 수 있다."""
        # Given
        mock_func = Mock(return_value="kwargs_only")
        kwargs = {"key1": "value1", "key2": "value2"}
        
        # When
        result = self.transaction_manager.execute_in_transaction(mock_func, **kwargs)
        
        # Then
        assert result == "kwargs_only"
        mock_func.assert_called_once_with(**kwargs)