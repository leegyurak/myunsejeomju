from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from urllib.parse import quote

from domain.use_cases.food_use_cases import GetAllFoodsUseCase, GetFoodByIdUseCase, GetFoodsByCategoryUseCase
from domain.use_cases.table_use_cases import GetAllTablesUseCase, GetTableByIdUseCase, CreateTableUseCase
from domain.use_cases.order_use_cases import CreateOrderUseCase, GetAllOrdersUseCase, GetOrdersByTableUseCase, CreatePreOrderUseCase, UpdateOrderStatusUseCase, GetPreOrderByPaymentInfoUseCase, ResetOrdersByTableUseCase
from domain.entities.food import FoodCategory
from infrastructure.database.repositories import DjangoFoodRepository, DjangoTableRepository, DjangoOrderRepository
from infrastructure.database.models import PaymentDepositModel
from infrastructure.transaction.django_transaction_manager import DjangoTransactionManager
from presentation.serializers.food_serializers import FoodSerializer
from presentation.serializers.table_serializers import TableSerializer
from presentation.serializers.order_serializers import OrderSerializer, CreateOrderSerializer, OrderHistorySerializer, CreatePreOrderSerializer
from datetime import datetime
from django.utils.dateparse import parse_datetime
from infrastructure.external.discord_service import discord_service


# Dependency injection
food_repository = DjangoFoodRepository()
table_repository = DjangoTableRepository()
order_repository = DjangoOrderRepository()
transaction_manager = DjangoTransactionManager()

# Food use cases
get_all_foods_use_case = GetAllFoodsUseCase(food_repository)
get_food_by_id_use_case = GetFoodByIdUseCase(food_repository)
get_foods_by_category_use_case = GetFoodsByCategoryUseCase(food_repository)

# Table use cases
get_all_tables_use_case = GetAllTablesUseCase(table_repository)
get_table_by_id_use_case = GetTableByIdUseCase(table_repository)
create_table_use_case = CreateTableUseCase(table_repository)

# Order use cases
create_order_use_case = CreateOrderUseCase(order_repository, food_repository, table_repository, transaction_manager)
get_all_orders_use_case = GetAllOrdersUseCase(order_repository)
get_orders_by_table_use_case = GetOrdersByTableUseCase(order_repository)
create_pre_order_use_case = CreatePreOrderUseCase(order_repository, table_repository, food_repository)
update_order_status_use_case = UpdateOrderStatusUseCase(order_repository)
get_pre_order_by_payment_info_use_case = GetPreOrderByPaymentInfoUseCase(order_repository)
reset_orders_by_table_use_case = ResetOrdersByTableUseCase(order_repository)


@api_view(['GET'])
def food_list(request):
    """
    음식 목록을 조회합니다.
    카테고리별 필터링을 지원합니다.
    """
    category = request.query_params.get('category')
    
    if category:
        try:
            food_category = FoodCategory(category)
            foods = get_foods_by_category_use_case.execute(food_category)
        except ValueError:
            return Response(
                {'error': 'Invalid category. Must be "menu" or "drinks"'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        foods = get_all_foods_use_case.execute()
    
    serializer = FoodSerializer(foods, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def food_detail(request, food_id):
    """
    특정 음식의 상세 정보를 조회합니다.
    """
    food = get_food_by_id_use_case.execute(food_id)
    
    if not food:
        return Response(
            {'error': 'Food not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = FoodSerializer(food)
    return Response(serializer.data)


@api_view(['GET'])
def table_list(request):
    """
    테이블 목록을 조회합니다.
    """
    tables = get_all_tables_use_case.execute()
    serializer = TableSerializer(tables, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def table_detail(request, table_id):
    """
    특정 테이블의 상세 정보를 조회합니다.
    """
    table = get_table_by_id_use_case.execute(table_id)
    
    if not table:
        return Response(
            {'error': 'Table not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = TableSerializer(table)
    return Response(serializer.data)


@api_view(['POST'])
def create_table(request):
    """
    새 테이블을 생성합니다.
    """
    try:
        table = create_table_use_case.execute()
        table_serializer = TableSerializer(table)
        return Response(
            table_serializer.data, 
            status=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_order(request):
    """
    특정 테이블에 새 주문을 생성합니다.
    """
    serializer = CreateOrderSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        table_id = serializer.validated_data['table_id']
        items_data = serializer.validated_data['items']
        order = create_order_use_case.execute(table_id, items_data)
        
        order_serializer = OrderSerializer(order)
        return Response(
            order_serializer.data, 
            status=status.HTTP_201_CREATED
        )
    
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def order_history(request):
    """
    주문 내역을 조회합니다.
    table_id 파라미터로 특정 테이블의 주문만 조회할 수 있습니다.
    """
    table_id = request.query_params.get('table_id')
    
    if table_id:
        orders = get_orders_by_table_use_case.execute(table_id)
    else:
        orders = get_all_orders_use_case.execute()
    
    # pre_order 상태가 아닌 주문들만 total_spent에 포함
    completed_orders = [order for order in orders if order.status != 'pre_order']
    total_spent = sum(order.total_amount for order in completed_orders)
    
    history_data = {
        'orders': orders,
        'total_spent': total_spent
    }
    
    serializer = OrderHistorySerializer(history_data)
    return Response(serializer.data)


@api_view(['GET'])
def table_orders(request, table_id):
    """
    특정 테이블의 주문 내역을 조회합니다.
    """
    try:
        orders = get_orders_by_table_use_case.execute(table_id)
        
        # pre_order 상태가 아닌 주문들만 total_spent에 포함
        completed_orders = [order for order in orders if order.status != 'pre_order']
        total_spent = sum(order.total_amount for order in completed_orders)
        
        history_data = {
            'orders': orders,
            'total_spent': total_spent
        }
        
        serializer = OrderHistorySerializer(history_data)
        return Response(serializer.data)
    
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def create_pre_order(request, table_id):
    """
    선주문을 생성하고 SuperToss 결제 페이지로 리다이렉트합니다.
    """
    try:
        # 요청 데이터가 올바른 형식인지 확인
        if not hasattr(request, 'data') or request.data is None:
            return Response(
                {'error': 'Invalid request data'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        serializer = CreatePreOrderSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        payer_name = serializer.validated_data['payer_name']
        total_amount = serializer.validated_data['total_amount']
        items_data = serializer.validated_data['items']
        
        order = create_pre_order_use_case.execute(table_id, payer_name, total_amount, items_data)
        
        # SuperToss 결제 URL 생성
        supertoss_url = f"supertoss://send?amount={total_amount}&bank=%EC%BC%80%EC%9D%B4%EB%B1%85%ED%81%AC&accountNo=100148347666&origin=qr"
        
        return Response({
            'order_id': order.id,
            'redirect_url': supertoss_url,
            'message': 'Pre-order created successfully. Please redirect to payment URL.'
        }, status=status.HTTP_201_CREATED)
    
    except UnicodeDecodeError as e:
        return Response(
            {'error': 'Encoding error - please ensure request is sent with UTF-8 encoding'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except ValueError as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {'error': f'Internal server error: {str(e)}'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def payment_webhook(request):
    """
    PayAction 웹훅을 처리하여 입금 데이터를 저장하고 pre-order 상태를 완료로 변경합니다.
    """
    try:
        # 헤더 검증 (선택적으로 추가 가능)
        webhook_key = request.headers.get('x-webhook-key')
        mall_id = request.headers.get('x-mall-id')
        trace_id = request.headers.get('x-trace-id')
        
        if not request.data:
            return Response(
                {'status': 'error', 'message': 'No data received'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 입금 확인 시에만 처리 (transaction_type이 'deposited'인 경우)
        transaction_type = request.data.get('transaction_type')
        if transaction_type != 'deposited':
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        
        # 웹훅 데이터에서 필요한 정보 추출
        transaction_name = request.data.get('transaction_name')
        bank_account_number = request.data.get('bank_account_number')
        amount = request.data.get('amount')
        bank_code = request.data.get('bank_code')
        bank_account_id = request.data.get('bank_account_id')
        transaction_date = request.data.get('transaction_date')
        processing_date = request.data.get('processing_date')
        balance = request.data.get('balance')
        
        # 필수 필드 검증
        if not all([transaction_name, bank_account_number, amount]):
            return Response(
                {'status': 'error', 'message': 'Missing required fields'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 날짜 파싱
        parsed_transaction_date = parse_datetime(transaction_date) if transaction_date else datetime.now()
        parsed_processing_date = parse_datetime(processing_date) if processing_date else datetime.now()
        
        # 입금 데이터 저장
        PaymentDepositModel.objects.create(
            transaction_name=transaction_name,
            bank_account_number=bank_account_number,
            amount=amount,
            bank_code=bank_code or '',
            bank_account_id=bank_account_id or '',
            transaction_date=parsed_transaction_date,
            processing_date=parsed_processing_date,
            balance=balance or 0
        )
        
        # pre-order 상태의 주문 찾기 및 상태 변경
        pre_order = get_pre_order_by_payment_info_use_case.execute(transaction_name, amount)
        
        if pre_order:
            # 주문 상태를 completed로 변경
            update_order_status_use_case.execute(pre_order.id, 'completed')
        
        # PayAction 문서에 명시된 성공 응답 형식
        return Response({'status': 'success'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        # 실패 시에도 성공 응답을 반환 (웹훅 재전송 방지)
        return Response({'status': 'success'}, status=status.HTTP_200_OK)


@api_view(['GET'])
def check_payment_status(request, order_id):
    """
    주문 ID를 받아서 해당 주문의 결제 완료 상태를 확인합니다.
    결제가 완료된 경우 Discord 알림을 전송합니다.
    """
    try:
        # 주문 조회
        order = order_repository.get_by_id(order_id)
        
        if not order:
            return Response(
                {'error': 'Order not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 결제 완료 상태 확인
        is_completed = order.status == 'completed'
        
        # 결제가 완료되고 아직 Discord 알림을 보내지 않은 경우에만 알림 전송
        if is_completed and not order.discord_notified:
            try:
                # 테이블 정보 조회
                table_name = order.table.name if order.table and order.table.name else f"테이블 {order.table.id}"
                
                # 주문 메뉴 정보 준비
                order_items = []
                for item in order.items:
                    order_items.append({
                        'name': item.food.name,
                        'quantity': item.quantity,
                        'price': item.total_price
                    })
                
                # Discord 알림 전송
                success = discord_service.send_payment_completion_notification(
                    order_id=order_id,
                    payer_name=order.payer_name,
                    total_amount=order.total_amount,
                    table_name=table_name,
                    order_items=order_items
                )
                
                # 알림 전송 성공 시 상태 업데이트
                if success:
                    order_repository.update_discord_notification_status(order_id, True)
                    
            except Exception as discord_error:
                pass
        
        return Response({
            'order_id': order_id,
            'payment_completed': is_completed,
            'order_status': order.status,
            'payer_name': order.payer_name,
            'total_amount': order.total_amount
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['DELETE'])
def reset_table_orders(request, table_id):
    """
    특정 테이블의 모든 주문 내역을 초기화합니다.
    """
    try:
        # 테이블이 존재하는지 확인
        table = get_table_by_id_use_case.execute(table_id)
        if not table:
            return Response(
                {'error': 'Table not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # 해당 테이블의 모든 주문 삭제
        reset_orders_by_table_use_case.execute(table_id)
        
        return Response(
            {'message': f'All orders for table {table_id} have been reset successfully'}, 
            status=status.HTTP_200_OK
        )
    
    except Exception as e:
        return Response(
            {'error': 'Internal server error'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )