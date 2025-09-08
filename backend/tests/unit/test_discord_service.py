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

    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/call-test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_staff_call_notification_success(self, mock_post):
        """직원호출 알림을 성공적으로 전송한다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_staff_call_notification(
            table_id="1",
            message="물 한 잔 부탁드립니다"
        )
        
        # Then
        assert result is True
        mock_post.assert_called_once()
        
        # 호출된 인수 확인
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://discord.com/api/webhooks/call-test"
        
        # JSON 데이터 확인
        json_data = call_args[1]['json']
        assert 'embeds' in json_data
        embed = json_data['embeds'][0]
        assert embed['title'] == "🔔 직원 호출"
        assert embed['color'] == 0xff9900  # 주황색
        assert "1에서 직원을 호출하였습니다!" in embed['description']
        assert "물 한 잔 부탁드립니다" in embed['description']
        
        # 필드 확인
        fields = embed['fields']
        table_field = next(f for f in fields if f['name'] == '테이블')
        assert table_field['value'] == '1'
        
        message_field = next(f for f in fields if f['name'] == '고객 메시지')
        assert message_field['value'] == '물 한 잔 부탁드립니다'

    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/call-test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_staff_call_notification_without_message(self, mock_post):
        """메시지 없이 직원호출 알림을 전송할 수 있다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 204
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_staff_call_notification(table_id="5")
        
        # Then
        assert result is True
        mock_post.assert_called_once()
        
        call_args = mock_post.call_args
        json_data = call_args[1]['json']
        embed = json_data['embeds'][0]
        
        # 기본 메시지만 포함되고 고객 메시지 필드는 없어야 함
        assert "5에서 직원을 호출하였습니다!" in embed['description']
        
        # 고객 메시지 필드가 없어야 함
        fields = embed['fields']
        message_fields = [f for f in fields if f['name'] == '고객 메시지']
        assert len(message_fields) == 0

    def test_send_staff_call_notification_without_webhook_url(self):
        """DISCORD_CALL_WEBHOOK_URL이 설정되지 않으면 False를 반환한다."""
        # Given
        service = DiscordNotificationService()
        
        # When
        result = service.send_staff_call_notification(
            table_id="1",
            message="테스트 메시지"
        )
        
        # Then
        assert result is False

    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/call-test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_staff_call_notification_request_failure(self, mock_post):
        """Discord 요청이 실패하면 False를 반환한다."""
        # Given
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_staff_call_notification(
            table_id="3",
            message="테스트"
        )
        
        # Then
        assert result is False
        mock_post.assert_called_once()

    @override_settings(DISCORD_CALL_WEBHOOK_URL="https://discord.com/api/webhooks/call-test")
    @patch('infrastructure.external.discord_service.requests.post')
    def test_send_staff_call_notification_request_exception(self, mock_post):
        """Discord 요청 중 예외가 발생하면 False를 반환한다."""
        # Given
        mock_post.side_effect = Exception("Network error")
        
        service = DiscordNotificationService()
        
        # When
        result = service.send_staff_call_notification(
            table_id="4",
            message="테스트"
        )
        
        # Then
        assert result is False
        mock_post.assert_called_once()

    @override_settings(DISCORD_CALL_WEBHOOK_URL="")
    def test_send_staff_call_notification_empty_webhook_url(self):
        """DISCORD_CALL_WEBHOOK_URL이 빈 문자열이면 False를 반환한다."""
        # Given
        service = DiscordNotificationService()
        
        # When
        result = service.send_staff_call_notification(
            table_id="1",
            message="테스트"
        )
        
        # Then
        assert result is False