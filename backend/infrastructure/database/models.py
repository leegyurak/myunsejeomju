from django.db import models
from django.utils import timezone
import uuid


class FoodModel(models.Model):
    CATEGORY_CHOICES = [
        ('main', 'Main'),
        ('side', 'Side'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='음식명')
    price = models.PositiveIntegerField(verbose_name='가격')
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, verbose_name='카테고리')
    description = models.TextField(blank=True, null=True, verbose_name='설명')
    image = models.URLField(blank=True, null=True, verbose_name='이미지 URL')
    sold_out = models.BooleanField(default=False, verbose_name='품절 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'foods'
        verbose_name = '음식'
        verbose_name_plural = '음식들'
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class TableModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='테이블 ID')
    name = models.CharField(max_length=50, null=True, blank=True, verbose_name='테이블 이름')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'tables'
        verbose_name = '테이블'
        verbose_name_plural = '테이블들'
    
    def __str__(self):
        return f"{self.name}"


class OrderModel(models.Model):
    STATUS_CHOICES = [
        ('pre_order', 'Pre Order'),
        ('completed', 'Completed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='주문 ID')
    table = models.ForeignKey(TableModel, on_delete=models.CASCADE, verbose_name='테이블')
    payer_name = models.CharField(max_length=100, null=True, blank=True, verbose_name='결제자 이름')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed', verbose_name='주문 상태')
    pre_order_amount = models.PositiveIntegerField(null=True, blank=True, verbose_name='선주문 총 금액')
    order_date = models.DateTimeField(default=timezone.now, verbose_name='주문일시')
    is_visible = models.BooleanField(default=True, verbose_name='표시 여부')
    discord_notified = models.BooleanField(default=False, verbose_name='Discord 알림 전송 여부')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    
    class Meta:
        db_table = 'orders'
        verbose_name = '주문'
        verbose_name_plural = '주문들'
        ordering = ['-order_date']
    
    def __str__(self):
        return f"Order {self.id} - Table {self.table.id}"
    
    @property
    def total_amount(self):
        # pre-order인 경우 pre_order_amount 사용
        if self.status == 'pre_order' and self.pre_order_amount is not None:
            return self.pre_order_amount
        
        # 일반 주문인 경우 items 기반 계산
        items_total = sum(item.total_price for item in self.items.all())
        minus_total = sum(minus_item.total_price for minus_item in self.minus_items.all())
        return items_total + minus_total


class OrderItemModel(models.Model):
    order = models.ForeignKey(OrderModel, related_name='items', on_delete=models.CASCADE)
    food = models.ForeignKey(FoodModel, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(verbose_name='수량')
    price = models.PositiveIntegerField(verbose_name='주문 당시 가격')
    
    class Meta:
        db_table = 'order_items'
        verbose_name = '주문 아이템'
        verbose_name_plural = '주문 아이템들'
    
    def __str__(self):
        return f"{self.food.name} x {self.quantity}"
    
    @property
    def total_price(self):
        return self.price * self.quantity


class MinusOrderItemModel(models.Model):
    REASON_CHOICES = [
        ('sold_out', 'Sold Out'),
        ('unavailable', 'Unavailable'),
        ('damaged', 'Damaged'),
    ]
    
    order = models.ForeignKey(OrderModel, related_name='minus_items', on_delete=models.CASCADE)
    food = models.ForeignKey(FoodModel, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name='수량(음수)')
    price = models.PositiveIntegerField(verbose_name='가격')
    reason = models.CharField(max_length=20, choices=REASON_CHOICES, verbose_name='차감 사유')
    
    class Meta:
        db_table = 'minus_order_items'
        verbose_name = '차감 주문 아이템'
        verbose_name_plural = '차감 주문 아이템들'
    
    def __str__(self):
        return f"{self.food.name} x {self.quantity} ({self.get_reason_display()})"
    
    @property
    def total_price(self):
        return self.price * self.quantity


class PaymentDepositModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name='입금 ID')
    transaction_name = models.CharField(max_length=100, verbose_name='입금자 이름')
    bank_account_number = models.CharField(max_length=50, verbose_name='계좌번호')
    amount = models.PositiveIntegerField(verbose_name='입금 금액')
    bank_code = models.CharField(max_length=10, verbose_name='은행 코드')
    bank_account_id = models.CharField(max_length=255, verbose_name='은행 계좌 ID')
    transaction_date = models.DateTimeField(verbose_name='거래 일시')
    processing_date = models.DateTimeField(verbose_name='처리 일시')
    balance = models.PositiveIntegerField(verbose_name='거래 후 잔액')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시')
    
    class Meta:
        db_table = 'payment_deposits'
        verbose_name = '입금 내역'
        verbose_name_plural = '입금 내역들'
        ordering = ['-transaction_date']
    
    def __str__(self):
        return f"{self.transaction_name} - {self.amount:,}원"


