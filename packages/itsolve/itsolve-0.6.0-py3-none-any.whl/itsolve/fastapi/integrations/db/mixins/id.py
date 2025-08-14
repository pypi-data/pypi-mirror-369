from sqlalchemy.orm import Mapped

from src.itsolve.fastapi.integrations.db.column_types import intpk


class IDMixin:
    id: Mapped[intpk]
