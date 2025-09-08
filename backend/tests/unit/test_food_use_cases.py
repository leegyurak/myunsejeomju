"""
Unit tests for food use cases.
"""
import pytest
from unittest.mock import Mock

from domain.use_cases.food_use_cases import (
    GetAllFoodsUseCase,
    GetFoodByIdUseCase,
    GetFoodsByCategoryUseCase
)
from domain.entities.food import FoodCategory
from tests.factories.entity_factories import FoodFactory, DrinkFoodFactory


@pytest.mark.unit
class TestGetAllFoodsUseCase:
    """Test cases for GetAllFoodsUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_repository = Mock()
        self.use_case = GetAllFoodsUseCase(self.mock_repository)
    
    def test_execute_returns_all_foods(self):
        """모든 음식을 반환한다."""
        # Given
        foods = [
            FoodFactory(name="비빔밥"),
            FoodFactory(name="냉면"),
            DrinkFoodFactory(name="콜라")
        ]
        self.mock_repository.get_all.return_value = foods
        
        # When
        result = self.use_case.execute()
        
        # Then
        assert result == foods
        self.mock_repository.get_all.assert_called_once()
    
    def test_execute_returns_empty_list_when_no_foods(self):
        """음식이 없을 때 빈 리스트를 반환한다."""
        # Given
        self.mock_repository.get_all.return_value = []
        
        # When
        result = self.use_case.execute()
        
        # Then
        assert result == []
        self.mock_repository.get_all.assert_called_once()


@pytest.mark.unit
class TestGetFoodByIdUseCase:
    """Test cases for GetFoodByIdUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_repository = Mock()
        self.use_case = GetFoodByIdUseCase(self.mock_repository)
    
    def test_execute_returns_food_when_exists(self):
        """음식이 존재할 때 해당 음식을 반환한다."""
        # Given
        food_id = 1
        food = FoodFactory(id=food_id, name="비빔밥")
        self.mock_repository.get_by_id.return_value = food
        
        # When
        result = self.use_case.execute(food_id)
        
        # Then
        assert result == food
        self.mock_repository.get_by_id.assert_called_once_with(food_id)
    
    def test_execute_returns_none_when_not_exists(self):
        """음식이 존재하지 않을 때 None을 반환한다."""
        # Given
        food_id = 999
        self.mock_repository.get_by_id.return_value = None
        
        # When
        result = self.use_case.execute(food_id)
        
        # Then
        assert result is None
        self.mock_repository.get_by_id.assert_called_once_with(food_id)


@pytest.mark.unit
class TestGetFoodsByCategoryUseCase:
    """Test cases for GetFoodsByCategoryUseCase."""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정."""
        self.mock_repository = Mock()
        self.use_case = GetFoodsByCategoryUseCase(self.mock_repository)
    
    def test_execute_returns_menu_foods(self):
        """메뉴 카테고리 음식들을 반환한다."""
        # Given
        category = FoodCategory.MAIN
        menu_foods = [
            FoodFactory(name="비빔밥", category=FoodCategory.MAIN),
            FoodFactory(name="냉면", category=FoodCategory.MAIN)
        ]
        self.mock_repository.get_by_category.return_value = menu_foods
        
        # When
        result = self.use_case.execute(category)
        
        # Then
        assert result == menu_foods
        self.mock_repository.get_by_category.assert_called_once_with(category)
    
    def test_execute_returns_drinks_foods(self):
        """음료 카테고리 음식들을 반환한다."""
        # Given
        category = FoodCategory.SIDE
        drink_foods = [
            DrinkFoodFactory(name="콜라"),
            DrinkFoodFactory(name="사이다")
        ]
        self.mock_repository.get_by_category.return_value = drink_foods
        
        # When
        result = self.use_case.execute(category)
        
        # Then
        assert result == drink_foods
        self.mock_repository.get_by_category.assert_called_once_with(category)
    
    def test_execute_returns_empty_list_when_no_foods_in_category(self):
        """해당 카테고리에 음식이 없을 때 빈 리스트를 반환한다."""
        # Given
        category = FoodCategory.MAIN
        self.mock_repository.get_by_category.return_value = []
        
        # When
        result = self.use_case.execute(category)
        
        # Then
        assert result == []
        self.mock_repository.get_by_category.assert_called_once_with(category)