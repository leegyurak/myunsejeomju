from typing import List, Optional

from ..entities.table import Table
from ..repositories.table_repository import TableRepository


class GetAllTablesUseCase:
    def __init__(self, table_repository: TableRepository):
        self.table_repository = table_repository
    
    def execute(self) -> List[Table]:
        return self.table_repository.get_all()


class GetTableByIdUseCase:
    def __init__(self, table_repository: TableRepository):
        self.table_repository = table_repository
    
    def execute(self, table_id: str) -> Optional[Table]:
        return self.table_repository.get_by_id(table_id)


class CreateTableUseCase:
    def __init__(self, table_repository: TableRepository):
        self.table_repository = table_repository
    
    def execute(self) -> Table:
        table = Table.create()
        return self.table_repository.create(table)