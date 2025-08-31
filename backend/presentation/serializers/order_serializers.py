from datetime import timezone
from rest_framework import serializers
from domain.entities.order import Order, OrderItem, MinusOrderItem
from .food_serializers import FoodSerializer
from .table_serializers import TableSerializer


class OrderItemSerializer(serializers.Serializer):
    food = FoodSerializer(read_only=True)
    quantity = serializers.IntegerField(min_value=1)
    price = serializers.IntegerField(min_value=0, read_only=True)
    
    def to_representation(self, instance: OrderItem):
        return {
            'food': FoodSerializer().to_representation(instance.food),
            'quantity': instance.quantity,
            'price': instance.price,
        }


class MinusOrderItemSerializer(serializers.Serializer):
    food = FoodSerializer(read_only=True)
    quantity = serializers.IntegerField()  # 음수 값
    price = serializers.IntegerField(min_value=0, read_only=True)
    reason = serializers.CharField(read_only=True)
    
    def to_representation(self, instance: MinusOrderItem):
        return {
            'food': FoodSerializer().to_representation(instance.food),
            'quantity': instance.quantity,
            'price': instance.price,
            'reason': instance.reason,
        }


class OrderSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    table = TableSerializer(read_only=True)
    order_date = serializers.DateTimeField(read_only=True, source='orderDate')
    items = OrderItemSerializer(many=True, read_only=True)
    minus_items = MinusOrderItemSerializer(many=True, read_only=True)
    total_amount = serializers.SerializerMethodField(read_only=True)
    
    def get_total_amount(self, obj: Order):
        return obj.total_amount
    
    def to_representation(self, instance: Order):
        return {
            'id': instance.id,
            'table': TableSerializer().to_representation(instance.table),
            'orderDate': instance.order_date.isoformat() if instance.order_date.tzinfo else instance.order_date.replace(tzinfo=timezone.utc).isoformat(),
            'items': [OrderItemSerializer().to_representation(item) for item in instance.items],
            'minusItems': [MinusOrderItemSerializer().to_representation(item) for item in (instance.minus_items or [])],
            'totalAmount': instance.total_amount,
        }


class CreateOrderItemSerializer(serializers.Serializer):
    food_id = serializers.IntegerField(min_value=1)
    quantity = serializers.IntegerField(min_value=1)


class CreateOrderSerializer(serializers.Serializer):
    table_id = serializers.CharField()
    items = CreateOrderItemSerializer(many=True, min_length=1)


class OrderHistorySerializer(serializers.Serializer):
    orders = OrderSerializer(many=True, read_only=True)
    total_spent = serializers.SerializerMethodField(read_only=True)
    
    def get_total_spent(self, obj):
        return sum(order.total_amount for order in obj['orders'])
    
    def to_representation(self, instance):
        return {
            'orders': [OrderSerializer().to_representation(order) for order in instance['orders']],
            'totalSpent': self.get_total_spent(instance),
        }


class CreatePreOrderSerializer(serializers.Serializer):
    payer_name = serializers.CharField(max_length=100)
    total_amount = serializers.IntegerField(min_value=1)
    items = CreateOrderItemSerializer(many=True, min_length=1)