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
        return [self._model_to_entity(order) for order in orders]
    
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
        return [self._model_to_entity(order) for order in orders]
    
    def get_all_including_hidden_by_table_id(self, table_id: str) -> List[Order]:
        orders = OrderModel.objects.filter(table_id=table_id)
        return [self._model_to_entity(order) for order in orders]
    
    def get_all_including_hidden(self) -> List[Order]:
        orders = OrderModel.objects.all()
        return [self._model_to_entity(order) for order in orders]
    
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
        
        # Convert order items
        items = []
        for item_model in order_model.items.all():
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
                quantity=item_model.quantity,
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
        
        return Order(
            id=str(order_model.id),
            table=table,
            order_date=order_model.order_date,
            items=items,
            payer_name=order_model.payer_name,
            status=order_model.status,
            pre_order_amount=order_model.pre_order_amount,
            minus_items=minus_items if minus_items else None,
            is_visible=order_model.is_visible,
            discord_notified=order_model.discord_notified
        )