"""Infrastructure-agnostic event processing types.

This module defines the type system for event-driven processing,
independent of delivery mechanism (webhooks, EventBridge, etc.).

The types in this module are designed to be clean, consistent, and focused
on the "what" (event processing) rather than the "how" (delivery method).
They support multiple event sources and maintain backward compatibility.
"""

from __future__ import annotations

from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NotRequired,
    Protocol,
    TypedDict,
)

if TYPE_CHECKING:
    pass


# Core Event Processing Result Type
class EventProcessingResult(TypedDict):
    """Result from processing any Stripe event.

    This type is infrastructure-agnostic and works for events
    from any source (webhooks, EventBridge, queues, etc.).

    Replaces: WebhookEventResultDict, WebhookProcessingDict
    """

    status: Literal["success", "error", "ignored", "duplicate"]
    event_id: str | None
    event_type: str
    result: NotRequired[dict[str, Any]]
    error: NotRequired[str]
    message: NotRequired[str]
    processed_at: NotRequired[str]


# Canonical Stripe Event Structure
class StripeEventData(TypedDict):
    """Canonical structure for Stripe event data.

    This represents the standard Stripe event structure regardless
    of how it was received (webhook, EventBridge, etc.).

    Replaces: StripeWebhookEventDict
    """

    id: str
    type: str
    created: NotRequired[int]
    livemode: NotRequired[bool]
    pending_webhooks: NotRequired[int]
    request: NotRequired[dict[str, Any] | None]
    data: EventDataObject


class EventDataObject(TypedDict):
    """The data object within a Stripe event."""

    object: dict[str, Any]
    previous_attributes: NotRequired[dict[str, Any] | None]


# Event Metadata for Processing Context
class EventMetadata(TypedDict):
    """Metadata about event processing context.

    Tracks how and when an event was processed, regardless of
    the original delivery mechanism.
    """

    source: Literal["webhook", "eventbridge", "sqs", "direct", "test"]
    received_at: str
    processing_started_at: NotRequired[str]
    processing_completed_at: NotRequired[str]
    retry_count: NotRequired[int]
    idempotency_key: NotRequired[str]
    delivery_attempt: NotRequired[int]


# Handler Protocol Types for Type Safety
class EventHandler(Protocol):
    """Protocol for event handler functions.

    Defines the interface that event handler functions must implement.
    Handlers should be pure functions that take event data and return
    a result dictionary or None.
    """

    def __call__(self, event: StripeEventData) -> dict[str, Any] | None:
        """Handle a Stripe event.

        Args:
            event: Stripe event data structure

        Returns:
            Processing result or None if no action needed
        """
        ...


class EventProcessor(Protocol):
    """Protocol for event processor classes.

    Defines the interface for classes that can process Stripe events
    from any source.
    """

    def process_stripe_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        event_id: str | None = None,
    ) -> EventProcessingResult:
        """Process a Stripe event from any source.

        Args:
            event_type: Type of Stripe event (e.g., "invoice.payment_succeeded")
            event_data: Event data object from Stripe
            event_id: Optional event ID for tracking

        Returns:
            Processing result with status and details
        """
        ...


class EventValidator(Protocol):
    """Protocol for event validators.

    Defines the interface for validating event data structure
    and content.
    """

    def validate(self, event_data: dict[str, Any]) -> bool:
        """Validate event data structure.

        Args:
            event_data: Event data to validate

        Returns:
            True if valid, False otherwise
        """
        ...


class SignatureValidator(Protocol):
    """Protocol for signature validators.

    Defines the interface for validating delivery-specific signatures
    (e.g., webhook signatures).
    """

    def validate_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Validate delivery signature.

        Args:
            payload: Raw payload bytes
            signature: Signature header
            secret: Validation secret

        Returns:
            True if signature is valid
        """
        ...


# Specific Event Result Types
class PaymentEventResult(TypedDict):
    """Result from processing payment-related events."""

    invoice_id: str
    customer_id: str | None
    amount_paid: int | Decimal
    status: Literal["paid", "failed", "pending"]
    attempt_count: NotRequired[int]
    payment_method: NotRequired[str]


class InvoiceEventResult(TypedDict):
    """Result from processing invoice-related events."""

    invoice_id: str
    customer_id: NotRequired[str | None]
    amount: NotRequired[int | Decimal]
    status: str
    line_items: NotRequired[list[dict[str, Any]]]
    due_date: NotRequired[str | None]


class SubscriptionEventResult(TypedDict):
    """Result from processing subscription-related events."""

    subscription_id: str
    customer_id: str | None
    status: str
    plan_id: NotRequired[str]
    current_period_end: NotRequired[str]
    current_period_start: NotRequired[str]


class PaymentIntentEventResult(TypedDict):
    """Result from processing payment intent events."""

    payment_intent_id: str
    amount: int | float | Decimal
    status: str
    error: NotRequired[str | None]
    customer_id: NotRequired[str | None]


# Type Aliases for Complex Types
type EventHandlerMap = dict[str, EventHandler]
type EventResultUnion = (
    PaymentEventResult
    | InvoiceEventResult
    | SubscriptionEventResult
    | PaymentIntentEventResult
    | dict[str, Any]
)


# Event Source Abstraction Protocol
class EventSource(Protocol):
    """Protocol for event sources.

    Defines how different event delivery mechanisms should
    expose events for processing.
    """

    def get_events(self) -> list[StripeEventData]:
        """Retrieve events from source.

        Returns:
            List of events ready for processing
        """
        ...

    def acknowledge_event(self, event_id: str) -> None:
        """Mark event as processed.

        Args:
            event_id: ID of the processed event
        """
        ...


class EventStore(Protocol):
    """Protocol for event storage.

    Defines how events can be stored and retrieved for
    processing or replay.
    """

    def store_event(self, event: StripeEventData, metadata: EventMetadata | None = None) -> None:
        """Store event for processing.

        Args:
            event: Event data to store
            metadata: Optional processing metadata
        """
        ...

    def get_unprocessed_events(self) -> list[StripeEventData]:
        """Get events that need processing.

        Returns:
            List of unprocessed events
        """
        ...


# Helper Type Guards
def is_payment_event(event_type: str) -> bool:
    """Type guard for payment-related events.

    Args:
        event_type: Stripe event type

    Returns:
        True if event is payment-related
    """
    return event_type.startswith(("payment_intent.", "invoice.payment"))


def is_invoice_event(event_type: str) -> bool:
    """Type guard for invoice-related events.

    Args:
        event_type: Stripe event type

    Returns:
        True if event is invoice-related
    """
    return event_type.startswith("invoice.")


def is_subscription_event(event_type: str) -> bool:
    """Type guard for subscription-related events.

    Args:
        event_type: Stripe event type

    Returns:
        True if event is subscription-related
    """
    return event_type.startswith("customer.subscription.")
