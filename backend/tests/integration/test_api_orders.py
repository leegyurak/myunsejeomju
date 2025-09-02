"""
Integration tests for order API endpoints.
"""
import pytest
import json
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TransactionTestCase

from tests.factories.model_factories import (
    FoodModelFactory,
    SoldOutFoodModelFactory,
    TableModelFactory
)


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.django_db(transaction=True)
class TestOrderAPIEndpoints(TransactionTestCase):
    """Test cases for order API endpoints."""
    
    def setUp(self):
        """각 테스트 실행 전 설정."""
        self.client = APIClient()
    
    def test_create_order_success(self):
        """정상적인 주문 생성 API 테스트."""
        # Given
        food1 = FoodModelFactory(name="비빔밥", price=12000, sold_out=False)
        food2 = FoodModelFactory(name="냉면", price=10000, sold_out=False)
        table = TableModelFactory()
        
        order_data = {
            'table_id': str(table.id),
            'items': [
                {'food_id': food1.id, 'quantity': 2},
                {'food_id': food2.id, 'quantity': 1}
            ]
        }
        
        # When
        response = self.client.post(
            '/api/orders/',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        # Then
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        assert 'id' in response_data
        assert response_data['table']['id'] == str(table.id)
        assert len(response_data['items']) == 2
        
        # 총액 검증 (비빔밥 2개 + 냉면 1개 = 24000 + 10000 = 34000)
        assert response_data['totalAmount'] == 34000
    
    def test_create_order_with_sold_out_food(self):
        """품절된 음식으로 주문 시 실패하는 API 테스트."""
        # Given
        available_food = FoodModelFactory(name="사용가능음식", sold_out=False)
        sold_out_food = SoldOutFoodModelFactory(name="품절음식")
        table = TableModelFactory()
        
        order_data = {
            'table_id': str(table.id),
            'items': [
                {'food_id': available_food.id, 'quantity': 1},
                {'food_id': sold_out_food.id, 'quantity': 1}
            ]
        }
        
        # When
        response = self.client.post(
            '/api/orders/',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert 'error' in response_data
        assert '품절음식' in response_data['error']
        assert '품절' in response_data['error']
    
    def test_create_order_with_invalid_table(self):
        """존재하지 않는 테이블 ID로 주문 시 실패하는 API 테스트."""
        # Given
        food = FoodModelFactory(sold_out=False)
        invalid_table_id = "00000000-0000-0000-0000-000000000000"
        
        order_data = {
            'table_id': invalid_table_id,
            'items': [
                {'food_id': food.id, 'quantity': 1}
            ]
        }
        
        # When
        response = self.client.post(
            '/api/orders/',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'not found' in response_data['error']
    
    def test_create_order_with_invalid_food(self):
        """존재하지 않는 음식 ID로 주문 시 실패하는 API 테스트."""
        # Given
        table = TableModelFactory()
        invalid_food_id = 999999
        
        order_data = {
            'table_id': str(table.id),
            'items': [
                {'food_id': invalid_food_id, 'quantity': 1}
            ]
        }
        
        # When
        response = self.client.post(
            '/api/orders/',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'not found' in response_data['error']
    
    def test_create_order_with_invalid_data(self):
        """잘못된 데이터로 주문 시 실패하는 API 테스트."""
        # Given
        invalid_order_data = {
            'table_id': 'invalid-uuid',
            'items': []  # 빈 아이템 리스트
        }
        
        # When
        response = self.client.post(
            '/api/orders/',
            data=json.dumps(invalid_order_data),
            content_type='application/json'
        )
        
        # Then
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_get_order_history(self):
        """주문 내역 조회 API 테스트."""
        # Given - setUp에서 주문 생성은 복잡하므로 간단한 조회 테스트만 수행
        
        # When
        response = self.client.get('/api/orders/history/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'orders' in response_data
        assert 'totalSpent' in response_data
        assert isinstance(response_data['orders'], list)
        assert isinstance(response_data['totalSpent'], int)
    
    def test_get_table_orders(self):
        """특정 테이블의 주문 내역 조회 API 테스트."""
        # Given
        table = TableModelFactory()
        
        # When
        response = self.client.get(f'/api/tables/{table.id}/orders/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'orders' in response_data
        assert 'totalSpent' in response_data