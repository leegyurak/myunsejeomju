from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    # Foods
    path('foods/', views.food_list, name='food-list'),
    path('foods/<int:food_id>/', views.food_detail, name='food-detail'),
    
    # Tables  
    path('tables/', views.table_list, name='table-list'),
    path('tables/create/', views.create_table, name='create-table'),
    path('tables/<str:table_id>/', views.table_detail, name='table-detail'),
    path('tables/<str:table_id>/orders/', views.table_orders, name='table-orders'),
    
    # Orders
    path('orders/', views.create_order, name='create-order'),
    path('orders/history/', views.order_history, name='order-history'),
    path('orders/pre-order/<str:table_id>/', views.create_pre_order, name='create-pre-order'),
    
    # Webhooks
    path('webhook/payment/', views.payment_webhook, name='payment-webhook'),
    
    # Payment status check
    path('orders/<str:order_id>/payment-status/', views.check_payment_status, name='check-payment-status'),
    
    # Reset table orders
    path('tables/<str:table_id>/orders/reset/', views.reset_table_orders, name='reset-table-orders'),
]