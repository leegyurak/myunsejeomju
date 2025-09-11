from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta

from .models import (
    FoodModel, TableModel, OrderModel,
    PaymentDepositModel
)


# ==================== 인증 관련 ====================

def admin_login(request):
    """관리자 로그인"""
    if request.user.is_authenticated:
        return redirect('admin_app:dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_staff:
            login(request, user)
            messages.success(request, f'{user.username}님, 관리자 페이지에 오신 것을 환영합니다.')
            next_url = request.GET.get('next', 'admin_app:dashboard')
            return redirect(next_url)
        else:
            messages.error(request, '유효하지 않은 관리자 계정입니다.')
    
    return render(request, 'admin_login.html')


def admin_logout(request):
    """관리자 로그아웃"""
    logout(request)
    messages.success(request, '성공적으로 로그아웃되었습니다.')
    return redirect('admin_app:login')


@login_required
def dashboard(request):
    """대시보드 메인 페이지"""
    # 통계 데이터 수집
    total_orders = OrderModel.objects.exclude(status='pre_order').count()
    total_foods = FoodModel.objects.count()
    total_tables = TableModel.objects.count()
    
    # 오늘 주문 수
    today = timezone.now().date()
    today_orders = OrderModel.objects.filter(order_date__date=today).exclude(status='pre_order').count()
    
    # 총 매출 (pre-order 제외)
    total_revenue = OrderModel.objects.exclude(status='pre_order').aggregate(
        revenue=Sum('pre_order_amount')
    )['revenue'] or 0
    
    # 최근 주문 5개 (pre-order 제외)
    recent_orders = OrderModel.objects.select_related('table').exclude(
        status='pre_order'
    ).order_by('-order_date')[:5]
    
    # 인기 메뉴 5개
    popular_foods = FoodModel.objects.annotate(
        order_count=Count('orderitemmodel__order', filter=~Q(orderitemmodel__order__status='pre_order'))
    ).order_by('-order_count')[:5]
    
    # 품절된 메뉴 수
    sold_out_foods = FoodModel.objects.filter(sold_out=True).count()
    
    context = {
        'total_orders': total_orders,
        'total_foods': total_foods,
        'total_tables': total_tables,
        'today_orders': today_orders,
        'total_revenue': total_revenue,
        'recent_orders': recent_orders,
        'popular_foods': popular_foods,
        'sold_out_foods': sold_out_foods,
    }
    
    return render(request, 'dashboard.html', context)


# ==================== 음식 관리 ====================

@login_required
def food_list(request):
    """음식 목록 - 추가/품절 처리만"""
    search = request.GET.get('search', '')
    category = request.GET.get('category', '')
    
    foods = FoodModel.objects.all()
    
    if search:
        foods = foods.filter(Q(name__icontains=search) | Q(description__icontains=search))
    
    if category:
        foods = foods.filter(category=category)
    
    foods = foods.order_by('-created_at')
    
    paginator = Paginator(foods, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'category': category,
        'categories': FoodModel.CATEGORY_CHOICES,
    }
    
    return render(request, 'food_list.html', context)


@login_required
def food_create(request):
    """음식 생성"""
    if request.method == 'POST':
        name = request.POST.get('name')
        price = request.POST.get('price')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        image = request.POST.get('image', '')
        
        food = FoodModel.objects.create(
            name=name,
            price=int(price),
            category=category,
            description=description,
            image=image if image else None
        )
        
        messages.success(request, f'{food.name}이(가) 성공적으로 추가되었습니다.')
        return redirect('admin_app:food_list')
    
    context = {
        'categories': FoodModel.CATEGORY_CHOICES,
    }
    
    return render(request, 'food_form.html', context)


@login_required
def food_toggle_sold_out(request, pk):
    """음식 품절 상태 토글"""
    food = get_object_or_404(FoodModel, pk=pk)
    
    if request.method == 'POST':
        food.sold_out = not food.sold_out
        food.save()
        
        status = "품절" if food.sold_out else "판매중"
        messages.success(request, f'{food.name}의 상태가 {status}으로 변경되었습니다.')
    
    return redirect('admin_app:food_list')


# ==================== 테이블 관리 ====================

@login_required
def table_list(request):
    """테이블 목록 - 주문 조회용"""
    search = request.GET.get('search', '')
    
    tables = TableModel.objects.annotate(
        active_order_count=Count('ordermodel', filter=Q(ordermodel__is_visible=True)),
        total_revenue=Sum('ordermodel__pre_order_amount', filter=Q(ordermodel__is_visible=True))
    )
    
    if search:
        tables = tables.filter(Q(name__icontains=search) | Q(id__icontains=search))
    
    tables = tables.order_by('-created_at')
    
    paginator = Paginator(tables, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
    }
    
    return render(request, 'table_list.html', context)


@login_required
def table_orders(request, pk):
    """특정 테이블의 주문 내역"""
    table = get_object_or_404(TableModel, pk=pk)
    
    # is_visible=True인 주문만 조회
    orders = OrderModel.objects.filter(
        table=table,
        is_visible=True
    ).select_related('table').prefetch_related('items__food').order_by('-order_date')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 총 매출 계산
    total_revenue = orders.aggregate(Sum('pre_order_amount'))['pre_order_amount__sum'] or 0
    
    context = {
        'table': table,
        'page_obj': page_obj,
        'total_revenue': total_revenue,
        'order_count': orders.count(),
    }
    
    return render(request, 'table_orders.html', context)


@login_required
def table_checkout(request, pk):
    """테이블 퇴실 처리 - 모든 주문을 is_visible=False로 변경"""
    table = get_object_or_404(TableModel, pk=pk)
    
    if request.method == 'POST':
        # 해당 테이블의 모든 활성 주문을 비활성화
        updated_count = OrderModel.objects.filter(
            table=table, 
            is_visible=True
        ).update(is_visible=False)
        
        if updated_count > 0:
            messages.success(request, f'{table.name} 테이블이 퇴실 처리되었습니다. ({updated_count}개 주문 처리)')
        else:
            messages.info(request, f'{table.name} 테이블에 처리할 주문이 없습니다.')
        
        return redirect('admin_app:table_list')
    
    # 활성 주문 수 확인
    active_orders_count = OrderModel.objects.filter(table=table, is_visible=True).count()
    total_amount = OrderModel.objects.filter(
        table=table, is_visible=True
    ).aggregate(Sum('pre_order_amount'))['pre_order_amount__sum'] or 0
    
    context = {
        'table': table,
        'active_orders_count': active_orders_count,
        'total_amount': total_amount,
    }
    
    return render(request, 'table_checkout.html', context)


@login_required
def order_hard_delete(request, order_id):
    """주문 완전 삭제 (Hard Delete)"""
    order = get_object_or_404(OrderModel, pk=order_id)
    table = order.table
    
    if request.method == 'POST':
        order_info = f"{str(order.id)[:8]}... (테이블: {table.name or str(table.id)[:8]}...)"
        order.delete()  # CASCADE로 관련 OrderItem들도 함께 삭제됨
        
        messages.success(request, f'주문 {order_info}이(가) 완전히 삭제되었습니다.')
        return redirect('admin_app:table_orders', pk=table.pk)
    
    context = {
        'order': order,
        'table': table,
        'return_url': request.META.get('HTTP_REFERER', f'/tables/{table.pk}/orders/')
    }
    
    return render(request, 'order_delete_confirm.html', context)


@login_required
def order_complete(request, order_id):
    """Pre-order를 Completed로 변경"""
    order = get_object_or_404(OrderModel, pk=order_id)
    table = order.table
    
    if request.method == 'POST':
        if order.status == 'pre_order':
            order.status = 'completed'
            order.save()
            
            order_info = f"{str(order.id)[:8]}... (테이블: {table.name or str(table.id)[:8]}...)"
            messages.success(request, f'주문 {order_info}이(가) 완료 처리되었습니다.')
        else:
            messages.warning(request, '이미 완료된 주문이거나 선주문이 아닙니다.')
        
        return redirect('admin_app:table_orders', pk=table.pk)
    
    context = {
        'order': order,
        'table': table,
        'return_url': request.META.get('HTTP_REFERER', f'/tables/{table.pk}/orders/')
    }
    
    return render(request, 'order_complete_confirm.html', context)


# ==================== 입금 관리 ====================

@login_required
def payment_list(request):
    """입금 내역 목록"""
    search = request.GET.get('search', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    payments = PaymentDepositModel.objects.all()
    
    if search:
        payments = payments.filter(
            Q(transaction_name__icontains=search) |
            Q(bank_account_number__icontains=search)
        )
    
    if date_from:
        payments = payments.filter(transaction_date__date__gte=date_from)
    
    if date_to:
        payments = payments.filter(transaction_date__date__lte=date_to)
    
    payments = payments.order_by('-transaction_date')
    
    # 통계 계산
    total_amount = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    paginator = Paginator(payments, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'total_amount': total_amount,
    }
    
    return render(request, 'payment_list.html', context)


@login_required
def payment_detail(request, pk):
    """입금 내역 상세"""
    payment = get_object_or_404(PaymentDepositModel, pk=pk)
    context = {'payment': payment}
    return render(request, 'payment_detail.html', context)


# ==================== API Views ====================

@login_required
def api_stats(request):
    """통계 API"""
    today = timezone.now().date()
    
    stats = {
        'total_orders': OrderModel.objects.exclude(status='pre_order').count(),
        'today_orders': OrderModel.objects.filter(order_date__date=today).exclude(status='pre_order').count(),
        'total_revenue': OrderModel.objects.exclude(status='pre_order').aggregate(
            Sum('pre_order_amount'))['pre_order_amount__sum'] or 0,
        'active_tables': TableModel.objects.count(),
        'sold_out_foods': FoodModel.objects.filter(sold_out=True).count(),
    }
    
    return JsonResponse(stats)


@login_required
def api_food_list(request):
    """음식 목록 API"""
    foods = FoodModel.objects.values('id', 'name', 'price', 'category', 'sold_out')
    return JsonResponse(list(foods), safe=False)