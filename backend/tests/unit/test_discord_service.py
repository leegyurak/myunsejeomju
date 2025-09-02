"""
Unit tests for Discord notification service.
"""
import pytest
from unittest.mock import Mock, patch
from django.test import override_settings

from infrastructure.external.discord_service import DiscordNotificationService


@pytest.mark.unit
class TestDiscordNotificationService:
    """Test cases for DiscordNotificationService."""
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    def test_initialization_with_webhook_url(self):
        """웹훅 URL이 설정된 상태에서 서비스를 초기화할 수 있다."""
        # Given & When
        service = DiscordNotificationService()
        
        # Then
        assert service.webhook_url == "https://discord.com/api/webhooks/test"
    
    @override_settings(DISCORD_WEBHOOK_URL="")
    def test_initialization_without_webhook_url(self):
        """웹훅 URL이 없어도 서비스를 초기화할 수 있다."""
        # Given & When
        service = DiscordNotificationService()
        
        # Then
        assert service.webhook_url == ""
    
    @override_settings(DISCORD_WEBHOOK_URL="")
    def test_send_notification_without_webhook_url_returns_false(self):
        """웹훅 URL이 없으면 False를 반환한다."""
        # Given
        service = DiscordNotificationService()
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-123",
            payer_name="홍길동",
            total_amount=25000
        )
        
        # Then
        assert result is False
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_payment_notification_success(self, mock_post):
        """결제 완료 알림을 성공적으로 전송한다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-123",
            payer_name="홍길동",
            total_amount=25000,
            table_name="테이블1",
            order_items=[
                {"name": "비빔밥", "quantity": 2, "price": 12000},
                {"name": "콜라", "quantity": 1, "price": 2000}
            ]
        )
        
        # Then
        assert result is True
        mock_post.assert_called_once()
        
        # 호출된 인수 확인
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://discord.com/api/webhooks/test"
        
        # JSON 데이터 확인
        json_data = call_args[1]['json']
        assert 'embeds' in json_data
        embed = json_data['embeds'][0]
        assert embed['title'] == "🎉 결제 완료 알림"
        assert embed['color'] == 0x00ff00
        
        # 필드 확인
        fields = embed['fields']
        order_id_field = next(f for f in fields if f['name'] == '주문 번호')
        assert 'order-123' in order_id_field['value']
        
        payer_field = next(f for f in fields if f['name'] == '결제자')
        assert payer_field['value'] == '홍길동'
        
        amount_field = next(f for f in fields if f['name'] == '결제 금액')
        assert '25,000원' in amount_field['value']
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_payment_notification_with_minimal_data(self, mock_post):
        """최소한의 데이터로 알림을 전송할 수 있다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-456",
            payer_name="김철수",
            total_amount=15000
        )
        
        # Then
        assert result is True
        mock_post.assert_called_once()
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_payment_notification_with_none_payer_name(self, mock_post):
        """결제자 이름이 None인 경우 '알 수 없음'으로 표시한다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-789",
            payer_name=None,
            total_amount=20000
        )
        
        # Then
        assert result is True
        
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        embed = json_data['embeds'][0]
        fields = embed['fields']
        
        payer_field = next(f for f in fields if f['name'] == '결제자')
        assert payer_field['value'] == '알 수 없음'
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_payment_notification_request_failure(self, mock_post):
        """Discord 요청이 실패하면 False를 반환한다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-fail",
            payer_name="테스트",
            total_amount=10000
        )
        
        # Then
        assert result is False
        mock_post.assert_called_once()
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_payment_notification_request_exception(self, mock_post):
        """Discord 요청 중 예외가 발생하면 False를 반환한다."""
        # Given
        mock_post.side_effect = Exception("Network error")
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-exception",
            payer_name="테스트",
            total_amount=5000
        )
        
        # Then
        assert result is False
        mock_post.assert_called_once()
    
    @override_settings(DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_payment_notification_includes_order_items(self, mock_post):
        """주문 아이템이 있는 경우 알림에 포함된다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        order_items = [
            {"name": "비빔밥", "quantity": 1, "price": 12000},
            {"name": "냉면", "quantity": 2, "price": 10000}
        ]
        
        # When
        result = service.send_payment_completion_notification(
            order_id="order-with-items",
            payer_name="홍길동",
            total_amount=32000,
            table_name="테이블5",
            order_items=order_items
        )
        
        # Then
        assert result is True
        
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        embed = json_data['embeds'][0]
        fields = embed['fields']
        
        # 테이블 정보 확인
        table_field = next(f for f in fields if f['name'] == '테이블')
        assert table_field['value'] == '테이블5'