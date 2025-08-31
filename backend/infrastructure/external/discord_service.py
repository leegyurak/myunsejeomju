import requests
import json
from datetime import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class DiscordNotificationService:
    """Discord webhook을 통한 알림 서비스"""
    
    def __init__(self):
        self.webhook_url = settings.DISCORD_WEBHOOK_URL
    
    def send_payment_completion_notification(self, order_id: str, payer_name: str, total_amount: int, table_name: str = None, order_items: list = None) -> bool:
        """
        결제 완료 알림을 Discord로 전송합니다.
        
        Args:
            order_id: 주문 ID
            payer_name: 결제자 이름
            total_amount: 결제 금액
            table_name: 테이블 이름 (선택적)
            order_items: 주문 아이템 목록 (선택적)
        
        Returns:
            bool: 전송 성공 여부
        """
        if not self.webhook_url:
            logger.warning("Discord webhook URL이 설정되지 않았습니다.")
            return False
        
        try:
            # 임베드 메시지 생성
            embed = {
                "title": "🎉 결제 완료 알림",
                "description": f"새로운 주문이 결제 완료되었습니다!",
                "color": 0x00ff00,  # 녹색
                "fields": [
                    {
                        "name": "주문 번호",
                        "value": f"`{order_id}`",
                        "inline": True
                    },
                    {
                        "name": "결제자",
                        "value": payer_name or "알 수 없음",
                        "inline": True
                    },
                    {
                        "name": "결제 금액",
                        "value": f"{total_amount:,}원",
                        "inline": True
                    }
                ],
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "숭실대축제 주문 시스템"
                }
            }
            
            # 테이블 정보가 있으면 추가
            if table_name:
                embed["fields"].insert(2, {
                    "name": "테이블",
                    "value": table_name,
                    "inline": True
                })
            
            # 주문 메뉴 정보가 있으면 추가
            if order_items:
                menu_text = ""
                for item in order_items:
                    menu_text += f"• {item['name']} x{item['quantity']} ({item['price']:,}원)\n"
                
                embed["fields"].append({
                    "name": "주문 메뉴",
                    "value": menu_text.strip(),
                    "inline": False
                })
            
            payload = {
                "embeds": [embed],
                "username": "주문알리미"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info(f"Discord 알림 전송 성공: 주문 {order_id}")
                return True
            else:
                logger.error(f"Discord 알림 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord 알림 전송 중 네트워크 오류: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Discord 알림 전송 중 예상치 못한 오류: {str(e)}")
            return False
    
    def send_custom_notification(self, title: str, message: str, color: int = 0x0099ff) -> bool:
        """
        커스텀 알림을 Discord로 전송합니다.
        
        Args:
            title: 알림 제목
            message: 알림 내용
            color: 임베드 색상 (기본값: 파란색)
        
        Returns:
            bool: 전송 성공 여부
        """
        if not self.webhook_url:
            logger.warning("Discord webhook URL이 설정되지 않았습니다.")
            return False
        
        try:
            embed = {
                "title": title,
                "description": message,
                "color": color,
                "timestamp": datetime.now().isoformat(),
                "footer": {
                    "text": "숭실대축제 주문 시스템"
                }
            }
            
            payload = {
                "embeds": [embed],
                "username": "축제 알림 봇"
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code == 204:
                logger.info(f"Discord 커스텀 알림 전송 성공: {title}")
                return True
            else:
                logger.error(f"Discord 커스텀 알림 전송 실패: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Discord 커스텀 알림 전송 중 네트워크 오류: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Discord 커스텀 알림 전송 중 예상치 못한 오류: {str(e)}")
            return False


# 싱글톤 인스턴스
discord_service = DiscordNotificationService()