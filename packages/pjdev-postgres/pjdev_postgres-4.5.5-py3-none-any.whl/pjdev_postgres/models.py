from datetime import datetime, timezone
from typing import Optional, Annotated
from uuid import UUID, uuid4

from pydantic import BaseModel
from sqlmodel import SQLModel, Field

from pjdev_postgres.model_validators import date_validator


class ConnectionOptions(BaseModel):
    echo: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class Versioned(BaseModel):
    concurrency_token: Optional[UUID] = None


class Auditable(BaseModel):
    created_by_id: Optional[str] = None
    created_by: Optional[str] = None
    created_datetime: Annotated[
        datetime, date_validator, Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    ]
    last_modified_by_id: Optional[str] = None
    last_modified_by: Optional[str] = None
    last_modified_datetime: Annotated[Optional[datetime], date_validator] = None


class TableModel(SQLModel):
    id: Annotated[UUID, Field(default_factory=uuid4, primary_key=True)]


class Savable(Versioned, Auditable, TableModel):
    pass


class History(TableModel, table=True):
    entity_name: Annotated[str, Field(index=True)]
    entity_id: Annotated[UUID, Field(index=True)]
    value: str
    timestamp: Annotated[
        datetime, date_validator, Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
    ]


class ConcurrencyException(BaseException):
    def __init__(self, message: str):
        super().__init__(message)
