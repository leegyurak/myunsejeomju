from dataclasses import dataclass
from datetime import datetime
import uuid


@dataclass
class Table:
    id: str  # UUID
    name: str | None
    created_at: datetime
    updated_at: datetime
    
    @classmethod
    def create(cls, name: str | None = None) -> 'Table':
        now = datetime.now()
        return cls(
            id=str(uuid.uuid4()),
            name=name,
            created_at=now,
            updated_at=now
        )