from abc import ABC, abstractmethod
from typing import Any
from pydantic.dataclasses import dataclass
from pydantic.fields import Field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Executable
from sqlalchemy.orm import DeclarativeBase


@dataclass
class SQLQuery[ReturnType](ABC):
    """
    Example:

    ```python
    class UpdateProductQuery(SQLQuery[None]):
        product_id: int
        query: Executable = select(User)
        name: str

        async def load(
            self, *args: Any, **kwargs: Any
        ) -> None:
            await self.transaction.execute(self.query)
            await self.transaction.flush()

    async with async_session_factory.begin() as tx:
        q = UpdateProductQuery(tx).load()
    ```
    """

    transaction: AsyncSession
    query: Executable = Field(init=False)
    table: type[DeclarativeBase] = Field(init=False)

    @abstractmethod
    async def load(self, *args: Any, **kwargs: Any) -> ReturnType: ...
