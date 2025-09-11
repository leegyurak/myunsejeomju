from typing import List, Optional

from domain.entities.food import Food, FoodCategory
from domain.entities.table import Table
from domain.entities.order import Order, OrderItem, MinusOrderItem
from domain.repositories.food_repository import FoodRepository
from domain.repositories.table_repository import TableRepository
from domain.repositories.order_repository import OrderRepository

from .models import FoodModel, TableModel, OrderModel, OrderItemModel, MinusOrderItemModel


class DjangoFoodRepository(FoodRepository):
    def get_all(self) -> List[Food]:
        foods = FoodModel.objects.all()
        return [self._model_to_entity(food) for food in foods]
    
    def get_by_id(self, food_id: int) -> Optional[Food]:
        try:
            food = FoodModel.objects.get(id=food_id)
            return self._model_to_entity(food)
        except FoodModel.DoesNotExist:
            return None
    
    def get_by_category(self, category: FoodCategory) -> List[Food]:
        foods = FoodModel.objects.filter(category=category.value)
        return [self._model_to_entity(food) for food in foods]
    
    def get_by_ids_for_update(self, food_ids: List[int]) -> List[Food]:
        """
        주문 생성 시 동시성 이슈 방지를 위해 select_for_update로 음식들을 조회합니다.
        트랜잭션 내에서만 호출되어야 합니다.
        """
        foods = FoodModel.objects.select_for_update().filter(id__in=food_ids)
        return [self._model_to_entity(food) for food in foods]
    
    def create(self, food: Food) -> Food:
        food_model = FoodModel(
            name=food.name,
            price=food.price,
            category=food.category.value,
            description=food.description,
            image=food.image,
            sold_out=food.sold_out
        )
        food_model.save()
        food.id = food_model.id
        return food
    
    def update(self, food: Food) -> Food:
        try:
            food_model = FoodModel.objects.get(id=food.id)
            food_model.name = food.name
            food_model.price = food.price
            food_model.category = food.category.value
            food_model.description = food.description
            food_model.image = food.image
            food_model.sold_out = food.sold_out
            food_model.save()
            return food
        except FoodModel.DoesNotExist:
            raise ValueError(f"Food with id {food.id} not found")
    
    def delete(self, food_id: int) -> bool:
        try:
            food = FoodModel.objects.get(id=food_id)
            food.delete()
            return True
        except FoodModel.DoesNotExist:
            return False
    
    def _model_to_entity(self, food_model: FoodModel) -> Food:
        return Food(
            id=food_model.id,
            name=food_model.name,
            price=food_model.price,
            category=FoodCategory(food_model.category),
            description=food_model.description,
            image=food_model.image,
            sold_out=food_model.sold_out
        )


class DjangoTableRepository(TableRepository):
    def get_all(self) -> List[Table]:
        tables = TableModel.objects.all()
        return [self._model_to_entity(table) for table in tables]
    
    def get_by_id(self, table_id: str) -> Optional[Table]:
        try:
            table = TableModel.objects.get(id=table_id)
            return self._model_to_entity(table)
        except TableModel.DoesNotExist:
            return None
    
    def create(self, table: Table) -> Table:
        table_model = TableModel(id=table.id, name=table.name)
        table_model.save()
        return table
    
    def delete(self, table_id: str) -> bool:
        try:
            table = TableModel.objects.get(id=table_id)
            table.delete()
            return True
        except TableModel.DoesNotExist:
            return False
    
    def _model_to_entity(self, table_model: TableModel) -> Table:
        return Table(
            id=str(table_model.id),
            name=table_model.name,
            created_at=table_model.created_at,
            updated_at=table_model.updated_at
        )


class DjangoOrderRepository(OrderRepository):
    def get_all(self) -> List[Order]:
        orders = OrderModel.objects.filter(is_visible=True)
        return [order for order in [self._model_to_entity(order_model) for order_model in orders] if order is not None]
    
    def get_by_id(self, order_id: str) -> Optional[Order]:
        try:
            order = OrderModel.objects.get(id=order_id)
            return self._model_to_entity(order)
        except OrderModel.DoesNotExist:
            return None
    
    def create(self, order: Order) -> Order:
        # Get table model
        table_model = TableModel.objects.get(id=order.table.id)
        
        order_model = OrderModel(
            id=order.id,
            table=table_model,
            payer_name=order.payer_name,
            status=order.status,
            pre_order_amount=order.pre_order_amount,
            order_date=order.order_date,
            is_visible=order.is_visible
        )
        order_model.save()
        
        # Create order items
        for item in order.items:
            try:
                food_model = FoodModel.objects.get(id=item.food.id)
                OrderItemModel.objects.create(
                    order=order_model,
                    food=food_model,
                    quantity=item.quantity,
                    price=item.price
                )
            except FoodModel.DoesNotExist:
                raise ValueError(f"Food with id {item.food.id} not found")
        
        # Create minus order items if they exist
        if order.minus_items:
            for minus_item in order.minus_items:
                try:
                    food_model = FoodModel.objects.get(id=minus_item.food.id)
                    MinusOrderItemModel.objects.create(
                        order=order_model,
                        food=food_model,
                        quantity=minus_item.quantity,
                        price=minus_item.price,
                        reason=minus_item.reason
                    )
                except FoodModel.DoesNotExist:
                    raise ValueError(f"Food with id {minus_item.food.id} not found")
        
        return order
    
    def create_with_stock_validation(self, order: Order) -> Order:
        """재고 검증과 함께 주문을 생성합니다. (트랜잭션 내에서 호출되어야 함)"""
        # Get table model
        table_model = TableModel.objects.get(id=order.table.id)
        
        # 주문할 음식들의 ID 수집
        food_ids = [item.food.id for item in order.items]
        if order.minus_items:
            food_ids.extend([minus_item.food.id for minus_item in order.minus_items])
        
        # select_for_update로 음식들을 락하고 조회 (동시성 제어)
        food_models = FoodModel.objects.select_for_update().filter(id__in=food_ids)
        food_dict = {food.id: food for food in food_models}
        
        # 품절된 음식 체크
        sold_out_foods = []
        for item in order.items:
            food_model = food_dict.get(item.food.id)
            if not food_model:
                raise ValueError(f"Food with id {item.food.id} not found")
            if food_model.sold_out:
                sold_out_foods.append(food_model.name)
        
        # 품절된 음식이 있으면 예외 발생
        if sold_out_foods:
            raise ValueError(f"다음 음식들이 품절되었습니다: {', '.join(sold_out_foods)}")
        
        # 주문 생성 (기존 create 로직 재사용)
        order_model = OrderModel(
            id=order.id,
            table=table_model,
            payer_name=order.payer_name,
            status=order.status,
            pre_order_amount=order.pre_order_amount,
            order_date=order.order_date,
            is_visible=order.is_visible
        )
        order_model.save()
        
        # Create order items
        for item in order.items:
            food_model = food_dict[item.food.id]
            OrderItemModel.objects.create(
                order=order_model,
                food=food_model,
                quantity=item.quantity,
                price=item.price
            )
        
        # Create minus order items if they exist
        if order.minus_items:
            for minus_item in order.minus_items:
                food_model = food_dict[minus_item.food.id]
                MinusOrderItemModel.objects.create(
                    order=order_model,
                    food=food_model,
                    quantity=minus_item.quantity,
                    price=minus_item.price,
                    reason=minus_item.reason
                )
        
        return order
    
    def update(self, order: Order) -> Order:
        try:
            order_model = OrderModel.objects.get(id=order.id)
            order_model.table_id = order.table.id
            order_model.order_date = order.order_date
            order_model.status = order.status
            order_model.payer_name = order.payer_name
            order_model.pre_order_amount = order.pre_order_amount
            order_model.is_visible = order.is_visible
            order_model.save()
            return order
        except OrderModel.DoesNotExist:
            raise ValueError(f"Order with id {order.id} not found")
    
    def delete(self, order_id: str) -> bool:
        try:
            order = OrderModel.objects.get(id=order_id)
            order.delete()
            return True
        except OrderModel.DoesNotExist:
            return False
    
    def get_by_table_id(self, table_id: str) -> List[Order]:
        orders = OrderModel.objects.filter(table_id=table_id, is_visible=True)
        return [order for order in [self._model_to_entity(order_model) for order_model in orders] if order is not None]
    
    def get_all_including_hidden_by_table_id(self, table_id: str) -> List[Order]:
        orders = OrderModel.objects.filter(table_id=table_id)
        return [order for order in [self._model_to_entity(order_model) for order_model in orders] if order is not None]
    
    def get_all_including_hidden(self) -> List[Order]:
        orders = OrderModel.objects.all()
        return [order for order in [self._model_to_entity(order_model) for order_model in orders] if order is not None]
    
    def update_discord_notification_status(self, order_id: str, notified: bool) -> bool:
        try:
            order_model = OrderModel.objects.get(id=order_id)
            order_model.discord_notified = notified
            order_model.save()
            return True
        except OrderModel.DoesNotExist:
            return False
    
    def _model_to_entity(self, order_model: OrderModel) -> Order:
        # Convert table directly from model to avoid circular dependency
        table = Table(
            id=str(order_model.table.id),
            name=order_model.table.name,
            created_at=order_model.table.created_at,
            updated_at=order_model.table.updated_at
        )
        
        # Convert order items, adjusting quantities based on minus order items
        items = []
        
        # Create a mapping of food_id to total minus quantity
        minus_quantities = {}
        for minus_item in order_model.minus_items.all():
            food_id = minus_item.food.id
            # minus_item.quantity는 음수이므로 절댓값을 사용
            minus_quantities[food_id] = minus_quantities.get(food_id, 0) + abs(minus_item.quantity)
        
        for item_model in order_model.items.all():
            # Calculate the effective quantity after subtracting minus items
            original_quantity = item_model.quantity
            minus_quantity = minus_quantities.get(item_model.food.id, 0)
            effective_quantity = original_quantity - minus_quantity
            
            # Only include the item if the effective quantity is positive
            if effective_quantity > 0:
                # Convert food directly from model to avoid circular dependency
                food = Food(
                    id=item_model.food.id,
                    name=item_model.food.name,
                    price=item_model.food.price,
                    category=FoodCategory(item_model.food.category),
                    description=item_model.food.description,
                    image=item_model.food.image,
                    sold_out=item_model.food.sold_out
                )
                items.append(OrderItem(
                    food=food,
                    quantity=effective_quantity,
                    price=item_model.price
                ))
        
        # Convert minus order items
        minus_items = []
        for minus_item_model in order_model.minus_items.all():
            # Convert food directly from model to avoid circular dependency
            food = Food(
                id=minus_item_model.food.id,
                name=minus_item_model.food.name,
                price=minus_item_model.food.price,
                category=FoodCategory(minus_item_model.food.category),
                description=minus_item_model.food.description,
                image=minus_item_model.food.image,
                sold_out=minus_item_model.food.sold_out
            )
            minus_items.append(MinusOrderItem(
                food=food,
                quantity=minus_item_model.quantity,
                price=minus_item_model.price,
                reason=minus_item_model.reason
            ))
        
        # Calculate effective total amount after minus items adjustment
        effective_total = None
        if order_model.status != 'pre_order' or order_model.pre_order_amount is None:
            effective_total = sum(item.total_price for item in items)
        
        order = Order(
            id=str(order_model.id),
            table=table,
            order_date=order_model.order_date,
            items=items,
            payer_name=order_model.payer_name,
            status=order_model.status,
            pre_order_amount=order_model.pre_order_amount,
            minus_items=minus_items if minus_items else None,
            is_visible=order_model.is_visible,
            discord_notified=order_model.discord_notified,
            effective_total_amount=effective_total
        )
        
        # 총액이 0원인 주문은 None 반환 (API에서 제외)
        if order.total_amount <= 0:
            return None
            
        return order