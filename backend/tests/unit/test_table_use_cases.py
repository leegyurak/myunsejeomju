"""
Unit tests for table use cases.
"""
import pytest
from unittest.mock import Mock, patch

from domain.use_cases.table_use_cases import (
    GetAllTablesUseCase,
    GetTableByIdUseCase,
    CreateTableUseCase
)
from tests.factories.entity_factories import TableFactory


@pytest.mark.unit
class TestGetAllTablesUseCase:
    """Test cases for GetAllTablesUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_repository = Mock()
        self.use_case = GetAllTablesUseCase(self.mock_repository)
    
    def test_execute_returns_all_tables(self):
        """모든 테이블을 반환한다."""
        # Given
        tables = [
            TableFactory(name="테이블1"),
            TableFactory(name="테이블2"),
            TableFactory(name="테이블3")
        ]
        self.mock_repository.get_all.return_value = tables
        
        # When
        result = self.use_case.execute()
        
        # Then
        assert result == tables
        self.mock_repository.get_all.assert_called_once()
    
    def test_execute_returns_empty_list_when_no_tables(self):
        """테이블이 없을 때 빈 리스트를 반환한다."""
        # Given
        self.mock_repository.get_all.return_value = []
        
        # When
        result = self.use_case.execute()
        
        # Then
        assert result == []
        self.mock_repository.get_all.assert_called_once()


@pytest.mark.unit
class TestGetTableByIdUseCase:
    """Test cases for GetTableByIdUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_repository = Mock()
        self.use_case = GetTableByIdUseCase(self.mock_repository)
    
    def test_execute_returns_table_when_exists(self):
        """테이블이 존재할 때 해당 테이블을 반환한다."""
        # Given
        table_id = "table-123"
        table = TableFactory(id=table_id, name="테이블1")
        self.mock_repository.get_by_id.return_value = table
        
        # When
        result = self.use_case.execute(table_id)
        
        # Then
        assert result == table
        self.mock_repository.get_by_id.assert_called_once_with(table_id)
    
    def test_execute_returns_none_when_not_exists(self):
        """테이블이 존재하지 않을 때 None을 반환한다."""
        # Given
        table_id = "non-existent-table"
        self.mock_repository.get_by_id.return_value = None
        
        # When
        result = self.use_case.execute(table_id)
        
        # Then
        assert result is None
        self.mock_repository.get_by_id.assert_called_once_with(table_id)


@pytest.mark.unit
class TestCreateTableUseCase:
    """Test cases for CreateTableUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_repository = Mock()
        self.use_case = CreateTableUseCase(self.mock_repository)
    
    @patch('domain.entities.table.Table.create')
    def test_execute_creates_and_saves_table(self, mock_create):
        """새 테이블을 생성하고 저장한다."""
        # Given
        existing_tables = [TableFactory(), TableFactory()]  # 2개의 기존 테이블
        new_table = TableFactory(name="테이블3")
        
        mock_create.return_value = new_table
        self.mock_repository.get_all.return_value = existing_tables
        self.mock_repository.create.return_value = new_table
        
        # When
        result = self.use_case.execute()
        
        # Then
        assert result == new_table
        mock_create.assert_called_once_with(name="테이블3")
        self.mock_repository.get_all.assert_called_once()
        self.mock_repository.create.assert_called_once_with(new_table)
    
    @patch('domain.entities.table.Table.create')
    def test_execute_handles_repository_creation(self, mock_create):
        """리포지토리를 통한 테이블 생성을 처리한다."""
        # Given
        existing_tables = []  # 기존 테이블 없음
        table_to_create = TableFactory(name="테이블1")
        created_table = TableFactory(id="created-id", name="테이블1")
        
        mock_create.return_value = table_to_create
        self.mock_repository.get_all.return_value = existing_tables
        self.mock_repository.create.return_value = created_table
        
        # When
        result = self.use_case.execute()
        
        # Then
        assert result == created_table
        assert result.id == "created-id"
        mock_create.assert_called_once_with(name="테이블1")
        self.mock_repository.get_all.assert_called_once()
        self.mock_repository.create.assert_called_once_with(table_to_create)