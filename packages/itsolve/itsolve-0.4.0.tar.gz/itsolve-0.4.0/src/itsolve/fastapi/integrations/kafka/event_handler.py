import json
from typing import Protocol, cast

from aiokafka import ConsumerRecord


class IEventHandler(Protocol):
    @classmethod
    async def handle(cls, message: ConsumerRecord) -> None:
        pass


class EventHandler[T](IEventHandler):
    @classmethod
    async def handle(cls, message: ConsumerRecord) -> None:
        data: T = json.loads(cast(bytes, message.value))
        await cls.process_data(data)

    @classmethod
    async def process_data(cls, data: T) -> None:
        pass
