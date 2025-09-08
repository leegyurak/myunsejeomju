"""
Integration tests for food API endpoints.
"""
import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TransactionTestCase

from tests.factories.model_factories import FoodModelFactory, SoldOutFoodModelFactory
from domain.entities.food import FoodCategory


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.django_db(transaction=True)
class TestFoodAPIEndpoints(TransactionTestCase):
    """Test cases for food API endpoints."""
    
    def setUp(self):
        """각 테스트 실행 전 설정."""
        self.client = APIClient()
    
    def test_get_food_list(self):
        """음식 목록을 조회할 수 있다."""
        # Given
        food1 = FoodModelFactory(name="비빔밥", price=12000)
        food2 = FoodModelFactory(name="냉면", price=10000)
        food3 = SoldOutFoodModelFactory(name="품절음식")
        
        # When
        response = self.client.get('/api/foods/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert len(response_data) == 3
        
        # 음식 정보 확인
        food_names = [food['name'] for food in response_data]
        assert "비빔밥" in food_names
        assert "냉면" in food_names
        assert "품절음식" in food_names
        
        # 가격 확인
        bibimbap = next(food for food in response_data if food['name'] == "비빔밥")
        assert bibimbap['price'] == 12000
        
        # 품절 상태 확인
        sold_out_food = next(food for food in response_data if food['name'] == "품절음식")
        assert sold_out_food['soldOut'] is True
    
    def test_get_food_list_by_menu_category(self):
        """메뉴 카테고리로 음식 목록을 필터링할 수 있다."""
        # Given
        menu_food = FoodModelFactory(
            name="비빔밥", 
            category=FoodCategory.MAIN.value,
            price=12000
        )
        drink_food = FoodModelFactory(
            name="콜라", 
            category=FoodCategory.SIDE.value,
            price=2000
        )
        
        # When
        response = self.client.get('/api/foods/?category=main')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]['name'] == "비빔밥"
        assert response_data[0]['category'] == "main"
    
    def test_get_food_list_by_drinks_category(self):
        """음료 카테고리로 음식 목록을 필터링할 수 있다."""
        # Given
        menu_food = FoodModelFactory(
            name="비빔밥", 
            category=FoodCategory.MAIN.value
        )
        drink_food = FoodModelFactory(
            name="콜라", 
            category=FoodCategory.SIDE.value
        )
        
        # When
        response = self.client.get('/api/foods/?category=side')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert len(response_data) == 1
        assert response_data[0]['name'] == "콜라"
        assert response_data[0]['category'] == "side"
    
    def test_get_food_list_with_invalid_category(self):
        """잘못된 카테고리로 요청 시 400 오류를 반환한다."""
        # Given
        FoodModelFactory(name="비빔밥")
        
        # When
        response = self.client.get('/api/foods/?category=invalid')
        
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'Invalid category' in response_data['error']
    
    def test_get_food_detail_existing(self):
        """존재하는 음식의 상세 정보를 조회할 수 있다."""
        # Given
        food = FoodModelFactory(
            name="비빔밥",
            price=12000,
            description="맛있는 비빔밥",
            category=FoodCategory.MAIN.value
        )
        
        # When
        response = self.client.get(f'/api/foods/{food.id}/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data['id'] == food.id
        assert response_data['name'] == "비빔밥"
        assert response_data['price'] == 12000
        assert response_data['description'] == "맛있는 비빔밥"
        assert response_data['category'] == "main"
        assert response_data['soldOut'] is False
    
    def test_get_food_detail_not_found(self):
        """존재하지 않는 음식 조회 시 404 오류를 반환한다."""
        # Given
        non_existent_id = 99999
        
        # When
        response = self.client.get(f'/api/foods/{non_existent_id}/')
        
        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'Food not found' in response_data['error']
    
    def test_get_empty_food_list(self):
        """음식이 없을 때 빈 배열을 반환한다."""
        # Given - 음식이 없음
        
        # When
        response = self.client.get('/api/foods/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data == []