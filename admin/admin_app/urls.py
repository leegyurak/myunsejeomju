from django.urls import path
from . import views

app_name = 'admin_app'

urlpatterns = [
    # Authentication
    path('login/', views.admin_login, name='login'),
    path('logout/', views.admin_logout, name='logout'),
    
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Food management - 음식 추가/품절 처리만
    path('foods/', views.food_list, name='food_list'),
    path('foods/create/', views.food_create, name='food_create'),
    path('foods/<int:pk>/toggle-sold-out/', views.food_toggle_sold_out, name='food_toggle_sold_out'),
    
    # Table management - 주문 조회, 퇴실 처리
    path('tables/', views.table_list, name='table_list'),
    path('tables/<str:pk>/orders/', views.table_orders, name='table_orders'),
    path('tables/<str:pk>/checkout/', views.table_checkout, name='table_checkout'),
    path('orders/<str:order_id>/delete/', views.order_hard_delete, name='order_hard_delete'),
    path('orders/<str:order_id>/complete/', views.order_complete, name='order_complete'),
    path('orders/<str:order_id>/items/<int:item_id>/refund/', views.order_item_refund, name='order_item_refund'),
    path('orders/<str:order_id>/full-refund/', views.order_full_refund, name='order_full_refund'),
    
    # Payment deposits - 입금 관리
    path('payments/', views.payment_list, name='payment_list'),
    path('payments/<str:pk>/', views.payment_detail, name='payment_detail'),
    
    # API endpoints for AJAX
    path('api/stats/', views.api_stats, name='api_stats'),
    path('api/foods/', views.api_food_list, name='api_food_list'),
]