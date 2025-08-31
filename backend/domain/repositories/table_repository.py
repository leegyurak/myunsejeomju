from abc import ABC, abstractmethod
from typing import List, Optional

from ..entities.table import Table


class TableRepository(ABC):
    @abstractmethod
    def get_all(self) -> List[Table]:
        pass
    
    @abstractmethod
    def get_by_id(self, table_id: str) -> Optional[Table]:
        pass
    
    @abstractmethod
    def create(self, table: Table) -> Table:
        pass
    
    @abstractmethod
    def delete(self, table_id: str) -> bool:
        pass