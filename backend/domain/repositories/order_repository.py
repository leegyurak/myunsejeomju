from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Order]:
        pass
    
    @abstractmethod
    def get_by_id(self, order_id: str) -> Optional[Order]:
        pass
    
    @abstractmethod
    def create(self, order: Order) -> Order:
        pass
    
    @abstractmethod
    def update(self, order: Order) -> Order:
        pass
    
    @abstractmethod
    def delete(self, order_id: str) -> bool:
        pass
    
    @abstractmethod
    def get_by_table_id(self, table_id: str) -> List[Order]:
        pass
    
    @abstractmethod
    def get_all_including_hidden_by_table_id(self, table_id: str) -> List[Order]:
        pass
    
    @abstractmethod
    def get_all_including_hidden(self) -> List[Order]:
        pass
    
    @abstractmethod
    def update_discord_notification_status(self, order_id: str, notified: bool) -> bool:
        pass