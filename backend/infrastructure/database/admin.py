from django.contrib import admin
from .models import FoodModel, TableModel, OrderModel, OrderItemModel, MinusOrderItemModel


@admin.register(FoodModel)
class FoodModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'price', 'category', 'sold_out', 'created_at')
    list_filter = ('category', 'sold_out', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('id',)


@admin.register(TableModel)
class TableModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    ordering = ('created_at',)
    readonly_fields = ('id', 'created_at', 'updated_at')


class OrderItemInline(admin.TabularInline):
    model = OrderItemModel
    extra = 0
    readonly_fields = ('food', 'quantity', 'price')


class MinusOrderItemInline(admin.TabularInline):
    model = MinusOrderItemModel
    extra = 0
    readonly_fields = ('food', 'quantity', 'price', 'reason')


@admin.register(OrderModel)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'table', 'order_date', 'created_at')
    list_filter = ('order_date', 'table')
    search_fields = ('id',)
    ordering = ('-order_date',)
    inlines = [OrderItemInline, MinusOrderItemInline]
    readonly_fields = ('id', 'order_date')