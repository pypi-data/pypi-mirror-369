from datetime import datetime
from typing import Annotated, TypeVar

from sqlalchemy import DateTime
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import func

T = TypeVar("T")

intpk = Annotated[
    int, mapped_column(primary_key=True, autoincrement=True, unique=True)
]
required = Annotated[T, mapped_column(nullable=False)]
timestamp = Annotated[
    datetime,
    mapped_column(DateTime(timezone=True), server_default=func.now()),
]
