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
        # 현재 테이블 수를 기반으로 이름 생성
        existing_tables = self.table_repository.get_all()
        table_number = len(existing_tables) + 1
        table_name = f"테이블{table_number}"
        
        table = Table.create(name=table_name)
        return self.table_repository.create(table)