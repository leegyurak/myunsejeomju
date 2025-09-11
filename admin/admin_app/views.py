from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta

from .discord import DiscordNotificationService
from .models import (
    FoodModel, TableModel, OrderModel, OrderItemModel,
    MinusOrderItemModel, PaymentDepositModel
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
    # 통계 데이터 수집 (환불된 주문 제외)
    total_orders = OrderModel.objects.exclude(status='pre_order').exclude(status='refunded').count()
    total_foods = FoodModel.objects.count()
    total_tables = TableModel.objects.count()
    
    # 오늘 주문 수 (환불된 주문 제외)
    today = timezone.now().date()
    today_orders = OrderModel.objects.filter(order_date__date=today).exclude(status='pre_order').exclude(status='refunded').count()
    
    # 총 매출 (pre-order 제외, 환불 금액 반영)
    completed_orders = OrderModel.objects.exclude(status='pre_order').exclude(status='refunded')
    total_revenue = 0
    for order in completed_orders:
        total_revenue += order.total_amount
    
    # 최근 주문 5개 (pre-order, refunded, 0원 주문 제외)
    recent_orders_queryset = OrderModel.objects.select_related('table').exclude(
        status='pre_order'
    ).exclude(status='refunded').order_by('-order_date')
    
    # 0원이 아닌 주문만 필터링
    recent_orders = []
    for order in recent_orders_queryset:
        if order.total_amount > 0:
            recent_orders.append(order)
            if len(recent_orders) >= 5:
                break
    
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
        active_order_count=Count('ordermodel', filter=Q(ordermodel__is_visible=True))
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
    ).select_related('table').prefetch_related('items__food', 'minus_items__food').order_by('-order_date')
    
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 총 매출 계산 (환불 금액 반영)
    total_revenue = 0
    for order in orders:
        total_revenue += order.total_amount
    
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
    
    # 총 금액 계산 (환불 금액 반영)
    active_orders = OrderModel.objects.filter(table=table, is_visible=True)
    total_amount = 0
    for order in active_orders:
        total_amount += order.total_amount
    
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
    discord = DiscordNotificationService()
    
    if request.method == 'POST':
        if order.status == 'pre_order':
            order.status = 'completed'
            order.save()
            
            order_info = f"{str(order.id)[:8]}... (테이블: {table.name or str(table.id)[:8]}...)"
            messages.success(request, f'주문 {order_info}이(가) 완료 처리되었습니다.')
            discord.send_payment_completion_notification(order.id, order.payer_name, order.pre_order_amount, table.name, [{'name': item.food.name, 'quantity': item.quantity, 'price': item.price} for item in order.items.all()])
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
    
    # 총 매출 (환불 금액 반영)
    completed_orders = OrderModel.objects.exclude(status='pre_order').exclude(status='refunded')
    total_revenue = 0
    for order in completed_orders:
        total_revenue += order.total_amount
    
    stats = {
        'total_orders': OrderModel.objects.exclude(status='pre_order').exclude(status='refunded').count(),
        'today_orders': OrderModel.objects.filter(order_date__date=today).exclude(status='pre_order').exclude(status='refunded').count(),
        'total_revenue': total_revenue,
        'active_tables': TableModel.objects.count(),
        'sold_out_foods': FoodModel.objects.filter(sold_out=True).count(),
    }
    
    return JsonResponse(stats)


@login_required
def api_food_list(request):
    """음식 목록 API"""
    foods = FoodModel.objects.values('id', 'name', 'price', 'category', 'sold_out')
    return JsonResponse(list(foods), safe=False)


@login_required
def order_item_refund(request, order_id, item_id):
    """주문 아이템 환불 처리"""
    order = get_object_or_404(OrderModel, pk=order_id)
    order_item = get_object_or_404(OrderItemModel, pk=item_id, order=order)
    
    if request.method == 'POST':
        refund_quantity = int(request.POST.get('refund_quantity', 1))
        
        # 환불 수량 검증
        if refund_quantity <= 0 or refund_quantity > order_item.quantity:
            messages.error(request, '올바르지 않은 환불 수량입니다.')
            return redirect('admin_app:table_orders', pk=order.table.pk)
        
        # 이미 환불된 수량 확인
        already_refunded = MinusOrderItemModel.objects.filter(
            order=order,
            food=order_item.food,
            reason='refund'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        # 음수로 저장되므로 절댓값으로 계산
        already_refunded = abs(already_refunded)
        
        if already_refunded + refund_quantity > order_item.quantity:
            messages.error(request, f'환불 가능한 수량을 초과했습니다. (이미 환불됨: {already_refunded}개)')
            return redirect('admin_app:table_orders', pk=order.table.pk)
        
        # MinusOrderItem 생성 (환불 처리)
        MinusOrderItemModel.objects.create(
            order=order,
            food=order_item.food,
            quantity=-refund_quantity,  # 음수로 저장
            price=order_item.price,
            reason='refund'
        )
        
        messages.success(request, f'{order_item.food.name} {refund_quantity}개가 환불 처리되었습니다.')
        return redirect('admin_app:table_orders', pk=order.table.pk)
    
    # GET 요청일 때 - 이미 환불된 수량 확인
    already_refunded = MinusOrderItemModel.objects.filter(
        order=order,
        food=order_item.food,
        reason='refund'
    ).aggregate(total=Sum('quantity'))['total'] or 0
    
    already_refunded = abs(already_refunded)
    available_for_refund = order_item.quantity - already_refunded
    
    context = {
        'order': order,
        'order_item': order_item,
        'already_refunded': already_refunded,
        'available_for_refund': available_for_refund,
        'table': order.table,
    }
    
    return render(request, 'order_item_refund.html', context)


@login_required
def order_full_refund(request, order_id):
    """주문 전체 환불 처리"""
    order = get_object_or_404(OrderModel, pk=order_id)
    
    if request.method == 'POST':
        # 이미 환불 처리된 주문인지 확인
        if order.status != 'completed':
            messages.error(request, '완료된 주문만 환불 처리할 수 있습니다.')
            return redirect('admin_app:table_orders', pk=order.table.pk)
        
        # 선주문인 경우와 일반 주문인 경우 구분
        if not order.items.exists():
            # 선주문인 경우 - pre_order_amount 전체를 환불
            if order.pre_order_amount and order.pre_order_amount > 0:
                # 가상의 "선주문" 항목으로 MinusOrderItem 생성
                # 선주문의 경우 특별한 처리가 필요하므로, 주문 상태를 변경하는 방식 사용
                order.status = 'refunded'  # 새로운 상태 추가 필요
                order.save()
                
                messages.success(request, f'선주문 ₩{order.pre_order_amount:,}이 전체 환불 처리되었습니다.')
            else:
                messages.error(request, '환불할 금액이 없습니다.')
        else:
            # 일반 주문인 경우 - 모든 아이템을 MinusOrderItem으로 생성
            refunded_count = 0
            total_refund_amount = 0
            
            for item in order.items.all():
                # 이미 환불된 수량 확인
                already_refunded = MinusOrderItemModel.objects.filter(
                    order=order,
                    food=item.food,
                    reason='refund'
                ).aggregate(total=Sum('quantity'))['total'] or 0
                
                already_refunded = abs(already_refunded)
                available_for_refund = item.quantity - already_refunded
                
                if available_for_refund > 0:
                    # 남은 수량 전체 환불
                    MinusOrderItemModel.objects.create(
                        order=order,
                        food=item.food,
                        quantity=-available_for_refund,  # 음수로 저장
                        price=item.price,
                        reason='refund'
                    )
                    refunded_count += available_for_refund
                    total_refund_amount += item.price * available_for_refund
            
            if refunded_count > 0:
                messages.success(request, f'주문 전체가 환불 처리되었습니다. (총 {refunded_count}개 아이템, ₩{total_refund_amount:,})')
            else:
                messages.warning(request, '환불 가능한 아이템이 없습니다. (이미 모든 아이템이 환불 처리됨)')
        
        return redirect('admin_app:table_orders', pk=order.table.pk)
    
    # GET 요청일 때 - 환불 가능한 아이템 및 금액 계산
    if not order.items.exists():
        # 선주문인 경우
        refundable_amount = order.pre_order_amount or 0
        refundable_items = []
        is_pre_order = True
    else:
        # 일반 주문인 경우
        refundable_items = []
        refundable_amount = 0
        is_pre_order = False
        
        for item in order.items.all():
            already_refunded = MinusOrderItemModel.objects.filter(
                order=order,
                food=item.food,
                reason='refund'
            ).aggregate(total=Sum('quantity'))['total'] or 0
            
            already_refunded = abs(already_refunded)
            available_for_refund = item.quantity - already_refunded
            
            if available_for_refund > 0:
                item_refund_amount = item.price * available_for_refund
                refundable_items.append({
                    'item': item,
                    'available_quantity': available_for_refund,
                    'refund_amount': item_refund_amount
                })
                refundable_amount += item_refund_amount
    
    context = {
        'order': order,
        'table': order.table,
        'refundable_items': refundable_items,
        'refundable_amount': refundable_amount,
        'is_pre_order': is_pre_order,
        'has_refundable_items': len(refundable_items) > 0 or (is_pre_order and refundable_amount > 0),
    }
    
    return render(request, 'order_full_refund.html', context)