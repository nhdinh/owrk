"""
Event Publishing for CQRS Pattern
Publishes domain events to RabbitMQ for read model synchronization
"""

import json
import logging
from typing import Any, Dict
import pika
from pika.exceptions import AMQPConnectionError, AMQPChannelError

from app.core.config import settings

logger = logging.getLogger(__name__)


class EventPublisher:
    """
    RabbitMQ Event Publisher
    Handles publishing domain events to message queue
    """

    def __init__(self):
        self.connection = None
        self.channel = None
        self.exchange = "procurement_events"

    def connect(self):
        """Establish connection to RabbitMQ"""
        try:
            parameters = pika.URLParameters(settings.RABBITMQ_URL)
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()

            # Declare exchange
            self.channel.exchange_declare(
                exchange=self.exchange, exchange_type="topic", durable=True
            )

            logger.info("Connected to RabbitMQ successfully")
        except AMQPConnectionError as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def disconnect(self):
        """Close RabbitMQ connection"""
        if self.connection and not self.connection.is_closed:
            self.connection.close()
            logger.info("Disconnected from RabbitMQ")

    def publish_event(self, event_type: str, data: Dict[str, Any]):
        """
        Publish an event to RabbitMQ

        Args:
            event_type: Type of event (e.g., "VendorCreated", "PurchaseOrderApproved")
            data: Event payload as dictionary

        Example:
            publisher.publish_event("VendorCreated", {
                "id": 1,
                "vendor_code": "VND001",
                "company_name": "ABC Corp"
            })
        """
        if not self.channel or self.channel.is_closed:
            self.connect()

        try:
            # Create message with metadata
            message = {
                "event_type": event_type,
                "data": data,
                "timestamp": data.get("created_at") or data.get("updated_at"),
            }

            # Publish to exchange with routing key
            routing_key = f"procurement.{event_type.lower()}"
            self.channel.basic_publish(
                exchange=self.exchange,
                routing_key=routing_key,
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Make message persistent
                    content_type="application/json",
                ),
            )

            logger.info(
                f"Published event: {event_type} with routing key: {routing_key}"
            )

        except AMQPChannelError as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            # Attempt reconnection
            self.connect()
            raise


# Global event publisher instance
event_publisher = EventPublisher()


def publish_event(event_type: str, data: Dict[str, Any]):
    """
    Convenience function to publish events
    Automatically handles connection management

    Args:
        event_type: Type of event
        data: Event data

    Example:
        publish_event("VendorCreated", vendor_dict)
    """
    try:
        event_publisher.publish_event(event_type, data)
    except Exception as e:
        logger.error(f"Error publishing event {event_type}: {e}")
        # Don't fail the request if event publishing fails
        # Log the error and continue


# Event type constants for consistency
class EventTypes:
    """Event type constants"""

    # Vendor events
    VENDOR_CREATED = "VendorCreated"
    VENDOR_UPDATED = "VendorUpdated"
    VENDOR_DELETED = "VendorDeleted"
    VENDOR_ACTIVATED = "VendorActivated"
    VENDOR_DEACTIVATED = "VendorDeactivated"
    VENDOR_BLACKLISTED = "VendorBlacklisted"

    # Framework Contract events
    CONTRACT_CREATED = "ContractCreated"
    CONTRACT_UPDATED = "ContractUpdated"
    CONTRACT_EXPIRED = "ContractExpired"
    CONTRACT_TERMINATED = "ContractTerminated"

    # Purchase Request events
    PURCHASE_REQUEST_CREATED = "PurchaseRequestCreated"
    PURCHASE_REQUEST_UPDATED = "PurchaseRequestUpdated"
    PURCHASE_REQUEST_SUBMITTED = "PurchaseRequestSubmitted"
    PURCHASE_REQUEST_APPROVED_LEVEL1 = "PurchaseRequestApprovedLevel1"
    PURCHASE_REQUEST_APPROVED_LEVEL2 = "PurchaseRequestApprovedLevel2"
    PURCHASE_REQUEST_APPROVED = "PurchaseRequestApproved"
    PURCHASE_REQUEST_REJECTED = "PurchaseRequestRejected"
    PURCHASE_REQUEST_CANCELLED = "PurchaseRequestCancelled"

    # Quotation events
    QUOTATION_CREATED = "QuotationCreated"
    QUOTATION_UPDATED = "QuotationUpdated"
    QUOTATION_APPROVED = "QuotationApproved"
    QUOTATION_REJECTED = "QuotationRejected"

    # Purchase Order events
    PURCHASE_ORDER_CREATED = "PurchaseOrderCreated"
    PURCHASE_ORDER_UPDATED = "PurchaseOrderUpdated"
    PURCHASE_ORDER_CONFIRMED = "PurchaseOrderConfirmed"
    PURCHASE_ORDER_SHIPPED = "PurchaseOrderShipped"
    PURCHASE_ORDER_DELIVERED = "PurchaseOrderDelivered"
    PURCHASE_ORDER_COMPLETED = "PurchaseOrderCompleted"
    PURCHASE_ORDER_CANCELLED = "PurchaseOrderCancelled"


# Startup and shutdown event handlers
def startup_event_publisher():
    """Initialize event publisher on application startup"""
    try:
        event_publisher.connect()
        logger.info("Event publisher initialized")
    except Exception as e:
        logger.error(f"Failed to initialize event publisher: {e}")


def shutdown_event_publisher():
    """Close event publisher on application shutdown"""
    try:
        event_publisher.disconnect()
        logger.info("Event publisher closed")
    except Exception as e:
        logger.error(f"Error closing event publisher: {e}")
