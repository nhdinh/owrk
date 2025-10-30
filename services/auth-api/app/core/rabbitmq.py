"""
RabbitMQ connection and event publishing for CQRS
"""

import aio_pika
import json
from typing import Callable
from app.core.config import settings


class RabbitMQConnection:
    """
    RabbitMQ connection manager - Singleton pattern
    """
    _instance = None
    _connection = None
    _channel = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self):
        """Establish connection to RabbitMQ"""
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(
                settings.RABBITMQ_URL
            )
            self._channel = await self._connection.channel()
            print("✅ Connected to RabbitMQ")

    async def close(self):
        """Close connection"""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()
        print("✅ RabbitMQ connection closed")

    async def get_channel(self):
        """Get channel for publishing/consuming"""
        if not self._channel or self._channel.is_closed:
            await self.connect()
        return self._channel


# Global instance
rabbitmq = RabbitMQConnection()


async def publish_event(routing_key: str, event_data: dict, exchange_name: str = "auth.events"):
    """
    Publish event to RabbitMQ

    Args:
        routing_key: Event routing key (e.g., "user.created")
        event_data: Event payload data
        exchange_name: Exchange to publish to
    """
    from datetime import datetime

    channel = await rabbitmq.get_channel()

    # Declare exchange (idempotent)
    exchange = await channel.declare_exchange(
        exchange_name,
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    # Construct full event object
    event = {
        "event_type": routing_key,
        "timestamp": datetime.utcnow().isoformat(),
        "data": event_data
    }

    # Publish message
    message = aio_pika.Message(
        body=json.dumps(event).encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT
    )

    await exchange.publish(message, routing_key=routing_key)
    print(f"📤 Published event: {routing_key}")


async def consume_events(
    exchange_name: str,
    queue_name: str,
    routing_keys: list,
    callback: Callable
):
    """
    Consume events from RabbitMQ

    Args:
        exchange_name: Exchange to consume from
        queue_name: Queue name
        routing_keys: List of routing keys to bind
        callback: Async function to handle messages
    """
    channel = await rabbitmq.get_channel()

    # Declare exchange
    exchange = await channel.declare_exchange(
        exchange_name,
        aio_pika.ExchangeType.TOPIC,
        durable=True
    )

    # Declare queue
    queue = await channel.declare_queue(queue_name, durable=True)

    # Bind queue to exchange with routing keys
    for routing_key in routing_keys:
        await queue.bind(exchange, routing_key=routing_key)

    # Start consuming
    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                event_data = json.loads(message.body.decode())
                await callback(event_data)
