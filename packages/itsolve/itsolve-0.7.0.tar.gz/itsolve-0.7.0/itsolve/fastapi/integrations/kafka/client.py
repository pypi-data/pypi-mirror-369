from __future__ import annotations

import asyncio
import json
import time
from typing import Any, Callable, NotRequired, TypedDict

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord
from loguru import logger

from src.itsolve.fastapi.settings import KafkaSettings

from .event_handler import EventHandler
from .exceptions import KafkaSendMessageAppException


class KafkaNotInitializedError(Exception):
    def __init__(self) -> None:
        super().__init__("Kafka client not initialized")


class KafkaProducerNotInitializedError(Exception):
    def __init__(self) -> None:
        super().__init__("Kafka producer client not initialized")


class Kafka:
    handlers: dict[str, type[EventHandler]] = {}
    topics: set[str] = set()

    def __init__(
        self,
        settings: KafkaSettings,
    ) -> None:
        self.settings = settings
        self.topics = set(self.settings.TOPICS.split(","))
        logger.info(
            "Initializing Kafka client",
            ctx={
                "topics": self.settings.TOPICS,
                "url": self.settings.URL,
            },
        )
        self.consumer = None
        self.producer = None

    async def init_producer(self) -> None:
        if not self.producer:
            event_loop = asyncio.get_running_loop()
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.settings.URL, loop=event_loop
            )
            await self.producer.start()  # type: ignore
            logger.info("Kafka producer initialized")
        else:
            logger.warning("Kafka producer already initialized")

    async def init_consumer(self) -> None:
        if not self.consumer:
            event_loop = asyncio.get_running_loop()
            self.consumer = AIOKafkaConsumer(
                *self.topics,
                bootstrap_servers=self.settings.URL,
                loop=event_loop,
            )
            await self.consumer.start()  # type: ignore
            logger.info("Kafka consumer initialized")
        else:
            logger.warning("Kafka consumer already initialized")

    async def stop(self) -> None:
        if not self.consumer or not self.producer:
            raise KafkaNotInitializedError
        await self.consumer.stop()
        await self.producer.stop()
        logger.info("Kafka client stopped")

    async def listen(self) -> None:
        logger.info("Kafka client listening")
        if not self.consumer:
            raise KafkaNotInitializedError
        async for msg in self.consumer:
            logger.info(
                f"Received message from Kafka: {msg.topic}",
                ctx={
                    "topic": msg.topic,
                    "partition": msg.partition,
                    "offset": msg.offset,
                    "timestamp": msg.timestamp,
                    "key": msg.key,
                    "value": msg.value,
                },
            )
            await self.dispatch(msg)

    async def __aenter__(self) -> Kafka:
        await self.init_consumer()
        asyncio.create_task(self.listen())
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        await self.stop()

    async def dispatch(self, message: ConsumerRecord) -> None:
        handler = self.handlers.get(message.topic)
        if handler:
            await handler.handle(message)

    @classmethod
    def register(cls, topic: str) -> Callable[[type[EventHandler]], type[EventHandler]]:
        def wrapper(event_handler: type[EventHandler]) -> type[EventHandler]:
            cls.handlers[topic] = event_handler
            logger.info(
                f"Registered handler for topic \
                {topic} - {event_handler.__name__}"
            )
            return event_handler

        return wrapper

    async def send(
        self, data: EventMessageDataType, throw_exception: bool = False
    ) -> bool:
        if self.producer:
            try:
                bytes_data = json.dumps(data["value"]).encode("utf-8")
                logger.info(
                    "Sending event message to kafka",
                    ctx={**data, "bytes": bytes_data},
                )
                await self.producer.send_and_wait(
                    data["topic"],
                    bytes_data,
                    key=data.get("key", None),
                    partition=data.get("partition", None),
                    timestamp_ms=data.get("timestamp_ms", int(time.time() * 1000)),
                    headers=data.get("headers", None),
                )
                logger.info("Message was sent to kafka")
            except Exception as e:
                logger.info(str(e))
                logger.warning(
                    "Failed to send register user event message to kafka",
                    ctx=data,
                )
                if throw_exception:
                    raise KafkaSendMessageAppException from e
                return False
            return True
        else:
            msg = f"""Can not send {data["topic"]} event message to kafka.
            Producer is not initialized"""
            logger.warning(msg)
            return False


class EventMessageDataType(TypedDict):
    topic: str
    value: dict[Any, Any] | str | list[Any] | int
    key: NotRequired[str | int]
    partition: NotRequired[int]
    timestamp_ms: NotRequired[int]
    headers: NotRequired[list[tuple[str, bytes]]]
