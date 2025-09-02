from django.db import transaction
from domain.services.order_service import TransactionManager


class DjangoTransactionManager(TransactionManager):
    """Django 기반 트랜잭션 관리자"""
    
    def execute_in_transaction(self, func, *args, **kwargs):
        """Django 트랜잭션 내에서 함수를 실행합니다."""
        with transaction.atomic():
            return func(*args, **kwargs)