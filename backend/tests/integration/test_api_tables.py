"""
Integration tests for table API endpoints.
"""
import pytest
import json
from unittest.mock import patch
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TransactionTestCase, override_settings

from tests.factories.model_factories import TableModelFactory, OrderModelFactory


@pytest.mark.integration
@pytest.mark.database
@pytest.mark.django_db(transaction=True)
class TestTableAPIEndpoints(TransactionTestCase):
    """Test cases for table API endpoints."""
    
    def setUp(self):
        """각 테스트 실행 전 설정."""
        self.client = APIClient()
    
    def test_get_table_list(self):
        """테이블 목록을 조회할 수 있다."""
        # Given
        table1 = TableModelFactory(name="테이블1")
        table2 = TableModelFactory(name="테이블2")
        table3 = TableModelFactory(name="테이블3")
        
        # When
        response = self.client.get('/api/tables/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert len(response_data) == 3
        
        # 테이블 정보 확인
        table_names = [table['name'] for table in response_data]
        assert "테이블1" in table_names
        assert "테이블2" in table_names
        assert "테이블3" in table_names
        
        # 각 테이블에 필수 필드가 포함되어 있는지 확인
        for table in response_data:
            assert 'id' in table
            assert 'name' in table
            assert 'createdAt' in table
            assert 'updatedAt' in table
    
    def test_get_table_detail_existing(self):
        """존재하는 테이블의 상세 정보를 조회할 수 있다."""
        # Given
        table = TableModelFactory(name="테이블1")
        
        # When
        response = self.client.get(f'/api/tables/{table.id}/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data['id'] == str(table.id)
        assert response_data['name'] == "테이블1"
        assert 'createdAt' in response_data
        assert 'updatedAt' in response_data
    
    def test_get_table_detail_not_found(self):
        """존재하지 않는 테이블 조회 시 404 오류를 반환한다."""
        # Given
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        
        # When
        response = self.client.get(f'/api/tables/{non_existent_id}/')
        
        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'Table not found' in response_data['error']
    
    def test_create_table(self):
        """새 테이블을 생성할 수 있다."""
        # Given - 별도 데이터 불필요
        
        # When
        response = self.client.post('/api/tables/create/')
        
        # Then
        assert response.status_code == status.HTTP_201_CREATED
        
        response_data = response.json()
        assert 'id' in response_data
        assert 'name' in response_data
        assert 'createdAt' in response_data
        assert 'updatedAt' in response_data
        
        # 테이블 이름이 자동 생성되었는지 확인
        assert response_data['name'].startswith('테이블')
    
    def test_get_table_orders_empty(self):
        """주문이 없는 테이블의 주문 내역을 조회할 수 있다."""
        # Given
        table = TableModelFactory()
        
        # When
        response = self.client.get(f'/api/tables/{table.id}/orders/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'orders' in response_data
        assert 'totalSpent' in response_data
        assert response_data['orders'] == []
        assert response_data['totalSpent'] == 0
    
    def test_get_table_orders_with_orders(self):
        """주문이 있는 테이블의 주문 내역을 조회할 수 있다."""
        # Given
        table = TableModelFactory()
        order1 = OrderModelFactory(table=table, is_visible=True)
        order2 = OrderModelFactory(table=table, is_visible=True)
        # 다른 테이블의 주문 (결과에 포함되지 않아야 함)
        other_table = TableModelFactory()
        other_order = OrderModelFactory(table=other_table, is_visible=True)
        
        # When
        response = self.client.get(f'/api/tables/{table.id}/orders/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'orders' in response_data
        assert 'totalSpent' in response_data
        assert len(response_data['orders']) == 2
        assert isinstance(response_data['totalSpent'], int)
        
        # 주문 ID 확인
        order_ids = [order['id'] for order in response_data['orders']]
        assert str(order1.id) in order_ids
        assert str(order2.id) in order_ids
        assert str(other_order.id) not in order_ids
    
    def test_get_table_orders_invalid_table_id(self):
        """존재하지 않는 테이블의 주문 내역 조회 시 빈 결과를 반환한다."""
        # Given
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        
        # When
        response = self.client.get(f'/api/tables/{non_existent_id}/orders/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'orders' in response_data
        assert 'totalSpent' in response_data
        assert response_data['orders'] == []
        assert response_data['totalSpent'] == 0
    
    def test_reset_table_orders(self):
        """테이블의 주문들을 리셋할 수 있다."""
        # Given
        table = TableModelFactory()
        order1 = OrderModelFactory(table=table, is_visible=True)
        order2 = OrderModelFactory(table=table, is_visible=True)
        
        # When
        response = self.client.delete(f'/api/tables/{table.id}/orders/reset/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'message' in response_data
        assert 'reset' in response_data['message'].lower()
    
    def test_reset_orders_invalid_table_id(self):
        """존재하지 않는 테이블의 주문 리셋 시 404 오류를 반환한다."""
        # Given
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        
        # When
        response = self.client.delete(f'/api/tables/{non_existent_id}/orders/reset/')
        
        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'Table not found' in response_data['error']
    
    def test_get_empty_table_list(self):
        """테이블이 없을 때 빈 배열을 반환한다."""
        # Given - 테이블이 없음
        
        # When
        response = self.client.get('/api/tables/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert response_data == []

    @pytest.mark.django_db(transaction=True)
    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_call_staff_success(self, mock_post):
        """테이블에서 직원 호출을 성공적으로 할 수 있다."""
        # Given
        mock_post.return_value.status_code = 204
        table = TableModelFactory(name="테이블1")
        
        # When
        response = self.client.post(f'/api/tables/{table.id}/call-staff/', {
            'message': '물 한 잔 부탁드립니다'
        }, format='json')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'message' in response_data
        assert 'Staff call notification sent' in response_data['message']
        assert str(table.id) in response_data['message']
        
        # Discord 서비스 호출 확인
        mock_post.assert_called_once()

    @pytest.mark.django_db(transaction=True) 
    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_call_staff_without_message(self, mock_post):
        """메시지 없이도 직원 호출을 할 수 있다."""
        # Given
        mock_post.return_value.status_code = 204
        table = TableModelFactory(name="테이블2")
        
        # When
        response = self.client.post(f'/api/tables/{table.id}/call-staff/')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'message' in response_data
        assert 'Staff call notification sent' in response_data['message']
        
        # Discord 서비스 호출 확인
        mock_post.assert_called_once()

    @pytest.mark.django_db(transaction=True)
    def test_call_staff_table_not_found(self):
        """존재하지 않는 테이블에서 직원 호출 시 404 오류를 반환한다."""
        # Given
        non_existent_id = "00000000-0000-0000-0000-000000000000"
        
        # When
        response = self.client.post(f'/api/tables/{non_existent_id}/call-staff/', {
            'message': '직원 호출'
        }, format='json')
        
        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        response_data = response.json()
        assert 'error' in response_data
        assert 'Table not found' in response_data['error']

    @pytest.mark.django_db(transaction=True)
    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_call_staff_with_empty_message(self, mock_post):
        """빈 메시지로도 직원 호출을 할 수 있다."""
        # Given
        mock_post.return_value.status_code = 204
        table = TableModelFactory(name="테이블3")
        
        # When
        response = self.client.post(f'/api/tables/{table.id}/call-staff/', {
            'message': ''
        }, format='json')
        
        # Then
        assert response.status_code == status.HTTP_200_OK
        
        response_data = response.json()
        assert 'message' in response_data
        assert 'Staff call notification sent' in response_data['message']
        
        # Discord 서비스 호출 확인
        mock_post.assert_called_once()