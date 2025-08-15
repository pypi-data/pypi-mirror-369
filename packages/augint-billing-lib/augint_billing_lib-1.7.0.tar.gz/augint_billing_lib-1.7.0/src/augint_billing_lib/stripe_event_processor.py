"""Stripe event processor for payment events.

This module handles processing Stripe payment events regardless of
delivery mechanism (webhooks, EventBridge, queues, direct calls, etc.),
updating billing status, and triggering appropriate actions.

Core Architecture:
- Infrastructure-agnostic event processing
- Webhook validation only when needed (delivery-specific)
- Clean separation between "what" (event processing) and "how" (delivery)
"""

import logging
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from typing import Any

from .config import get_settings
from .db import DynamoDBClient
from .event_types import (
    EventProcessingResult,
    InvoiceEventResult,
    PaymentEventResult,
    PaymentIntentEventResult,
    StripeEventData,
    SubscriptionEventResult,
)
from .models import Invoice

logger = logging.getLogger(__name__)


class StripeEventProcessor:
    """Processes Stripe payment events and updates billing status.

    This class handles Stripe event processing and updating billing
    records based on payment events. Events can come from any source
    (webhooks, EventBridge, queues, etc.). Webhook signature validation
    is available but optional.
    """

    def __init__(
        self,
        stripe_manager: Any | None = None,
        db_client: DynamoDBClient | None = None,
        signature_secret: str | None = None,
    ):
        """Initialize Stripe event processor.

        Args:
            stripe_manager: StripeManager instance for Stripe operations
            db_client: DynamoDBClient instance for database operations
            signature_secret: Stripe secret for signature validation (optional,
                only for utility functions)
        """
        settings = get_settings()
        self.stripe_manager = stripe_manager
        self.db_client = db_client or DynamoDBClient(table_name=settings.dynamodb_table)
        self.signature_secret = signature_secret or settings.stripe_webhook_secret

        # Event handlers mapping
        self.event_handlers: dict[str, Callable[..., Any]] = {
            "invoice.payment_succeeded": self._handle_payment_succeeded,
            "invoice.payment_failed": self._handle_payment_failed,
            "invoice.created": self._handle_invoice_created,
            "invoice.finalized": self._handle_invoice_finalized,
            "invoice.voided": self._handle_invoice_voided,
            "customer.subscription.created": self._handle_subscription_created,
            "customer.subscription.updated": self._handle_subscription_updated,
            "customer.subscription.deleted": self._handle_subscription_deleted,
            "payment_intent.succeeded": self._handle_payment_intent_succeeded,
            "payment_intent.payment_failed": self._handle_payment_intent_failed,
        }

        logger.info(f"Initialized StripeEventProcessor with table: {self.db_client.table_name}")

    def process_stripe_event(
        self,
        event_type: str,
        event_data: dict[str, Any],
        event_id: str | None = None,
    ) -> EventProcessingResult:
        """Process a Stripe event from any source.

        This is the primary interface for processing Stripe events. Events can
        come from webhooks, EventBridge, queues, or any other source.

        Args:
            event_type: Type of Stripe event (e.g., "invoice.payment_succeeded")
            event_data: Event data object from Stripe
            event_id: Optional event ID for tracking

        Returns:
            Processing result dictionary with status and details

        Example:
            >>> processor = StripeEventProcessor()
            >>> result = processor.process_stripe_event(
            ...     event_type="invoice.payment_succeeded",
            ...     event_data={"id": "inv_123", "amount_paid": 5000},
            ...     event_id="evt_123"
            ... )
        """
        logger.info(f"Processing Stripe event: {event_type} (ID: {event_id})")

        # Create canonical event structure for handlers
        event = self._create_canonical_event(
            event_type=event_type, event_data=event_data, event_id=event_id
        )

        # Use the actual event ID from the canonical event (might be generated)
        actual_event_id = event["id"]

        # Check if we have a handler for this event type
        handler = self.event_handlers.get(event_type)

        if handler:
            try:
                result = handler(event)
                logger.info(f"Successfully processed {event_type} event")
                return {
                    "status": "success",
                    "event_id": actual_event_id,
                    "event_type": event_type,
                    "result": result,
                }

            except Exception as e:
                logger.exception(f"Error processing {event_type} event: ")
                return {
                    "status": "error",
                    "event_id": actual_event_id,
                    "event_type": event_type,
                    "error": str(e),
                }
        else:
            logger.debug(f"No handler for event type: {event_type}")
            return {
                "status": "ignored",
                "event_id": actual_event_id,
                "event_type": event_type,
                "message": "No handler configured for this event type",
            }

    def _create_canonical_event(
        self, event_type: str, event_data: dict[str, Any], event_id: str | None = None
    ) -> StripeEventData:
        """Create canonical event structure for processing.

        This method standardizes event data from any source into the
        canonical StripeEventData format expected by event handlers.

        Args:
            event_type: Type of Stripe event (e.g., "invoice.payment_succeeded")
            event_data: Event data object from Stripe
            event_id: Optional event ID for tracking

        Returns:
            Standardized event data structure
        """
        return {
            "type": event_type,
            "id": event_id or f"evt_{uuid.uuid4().hex[:8]}",
            "data": {"object": event_data},
        }

    def _handle_payment_succeeded(self, event: StripeEventData) -> PaymentEventResult:
        """Handle successful payment event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)
        amount_paid = invoice["amount_paid"] / 100  # Convert from cents

        # Update invoice record
        self._update_invoice_status(
            stripe_invoice_id=invoice_id, status="paid", amount_paid=amount_paid
        )

        # Update billing period if linked
        if customer_id and "billing_period" in invoice.get("metadata", {}):
            period = invoice["metadata"]["billing_period"]
            self._update_billing_period_status(
                customer_id=customer_id, period=period, status="paid", invoice_id=invoice_id
            )

        # Update customer billing status
        if customer_id:
            self._update_customer_billing_status(customer_id, "active")

        logger.info(f"Payment succeeded for invoice {invoice_id}, amount: {amount_paid}")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount_paid": amount_paid,
            "status": "paid",
        }

    def _handle_payment_failed(self, event: StripeEventData) -> PaymentEventResult:
        """Handle failed payment event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)
        attempt_count = invoice.get("attempt_count", 1)

        # Update invoice record
        self._update_invoice_status(
            stripe_invoice_id=invoice_id,
            status="open",
            metadata={"payment_failed": True, "attempt_count": attempt_count},
        )

        # Update billing period if linked
        if customer_id and "billing_period" in invoice.get("metadata", {}):
            period = invoice["metadata"]["billing_period"]
            self._update_billing_period_status(
                customer_id=customer_id, period=period, status="failed"
            )

        # Update customer billing status
        if customer_id:
            self._update_customer_billing_status(customer_id, "past_due")

        logger.warning(f"Payment failed for invoice {invoice_id}, attempt: {attempt_count}")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount_paid": 0,  # Failed payment, so amount paid is 0
            "attempt_count": attempt_count,
            "status": "failed",
        }

    def _handle_invoice_created(self, event: StripeEventData) -> InvoiceEventResult:
        """Handle invoice created event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)

        # Create invoice record in database
        clean_invoice_id = invoice_id.replace("in_", "")  # Remove Stripe prefix
        invoice_record = Invoice(
            pk=f"INVOICE#{clean_invoice_id}",
            invoice_id=clean_invoice_id,
            customer_id=customer_id or "unknown",
            stripe_invoice_id=invoice_id,
            amount=Decimal(str(invoice["amount_due"])) / 100,
            currency=invoice["currency"].upper(),
            status="draft",
            due_date=datetime.fromtimestamp(invoice.get("due_date", 0), tz=UTC),
            line_items=self._extract_line_items(invoice),
        )

        try:
            self.db_client.put_item(invoice_record.model_dump())
            logger.info(f"Created invoice record for {invoice_id}")
        except Exception:
            logger.exception("Failed to create invoice record: ")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount": Decimal(str(invoice["amount_due"])) / 100,
            "status": "created",
        }

    def _handle_invoice_finalized(self, event: StripeEventData) -> InvoiceEventResult:
        """Handle invoice finalized event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)

        # Update invoice status to open
        self._update_invoice_status(stripe_invoice_id=invoice_id, status="open")

        logger.info(f"Invoice {invoice_id} finalized")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount": Decimal(str(invoice.get("amount_due", 0))) / 100,
            "status": "finalized",
        }

    def _handle_invoice_voided(self, event: StripeEventData) -> InvoiceEventResult:
        """Handle invoice voided event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        invoice = event["data"]["object"]
        invoice_id = invoice["id"]
        customer_id = self._get_customer_id_from_metadata(invoice)

        # Update invoice status to void
        self._update_invoice_status(stripe_invoice_id=invoice_id, status="void")

        logger.info(f"Invoice {invoice_id} voided")

        return {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "amount": Decimal(str(invoice.get("amount_due", 0))) / 100,
            "status": "voided",
        }

    def _handle_subscription_created(self, event: StripeEventData) -> SubscriptionEventResult:
        """Handle subscription created event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        customer_id = self._get_customer_id_from_metadata(subscription)

        logger.info(f"Subscription {subscription_id} created for customer {customer_id}")

        return {"subscription_id": subscription_id, "customer_id": customer_id, "status": "created"}

    def _handle_subscription_updated(self, event: StripeEventData) -> SubscriptionEventResult:
        """Handle subscription updated event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        status = subscription["status"]
        customer_id = self._get_customer_id_from_metadata(subscription)

        logger.info(f"Subscription {subscription_id} updated to status: {status}")

        return {"subscription_id": subscription_id, "customer_id": customer_id, "status": status}

    def _handle_subscription_deleted(self, event: StripeEventData) -> SubscriptionEventResult:
        """Handle subscription deleted event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        subscription = event["data"]["object"]
        subscription_id = subscription["id"]
        customer_id = self._get_customer_id_from_metadata(subscription)

        # Update customer billing status
        if customer_id:
            self._update_customer_billing_status(customer_id, "cancelled")

        logger.info(f"Subscription {subscription_id} deleted")

        return {"subscription_id": subscription_id, "customer_id": customer_id, "status": "deleted"}

    def _handle_payment_intent_succeeded(self, event: StripeEventData) -> PaymentIntentEventResult:
        """Handle payment intent succeeded event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        payment_intent = event["data"]["object"]
        intent_id = payment_intent["id"]
        amount = payment_intent["amount"] / 100

        logger.info(f"Payment intent {intent_id} succeeded, amount: {amount}")

        return {"payment_intent_id": intent_id, "amount": amount, "status": "succeeded"}

    def _handle_payment_intent_failed(self, event: StripeEventData) -> PaymentIntentEventResult:
        """Handle payment intent failed event.

        Args:
            event: Stripe event data

        Returns:
            Processing result
        """
        payment_intent = event["data"]["object"]
        intent_id = payment_intent["id"]
        error_message = payment_intent.get("last_payment_error", {}).get("message")

        logger.warning(f"Payment intent {intent_id} failed: {error_message}")

        return {
            "payment_intent_id": intent_id,
            "amount": 0.0,
            "status": "failed",
            "error": error_message,
        }

    def _get_customer_id_from_metadata(
        self, stripe_object: dict[str, Any]
    ) -> str | None:  # stripe_object is from Stripe API
        """Extract internal customer ID from Stripe metadata.

        Args:
            stripe_object: Stripe object with metadata

        Returns:
            Customer ID or None
        """
        metadata = stripe_object.get("metadata", {})
        return metadata.get("internal_customer_id") or metadata.get("customer_id")  # type: ignore[no-any-return]

    def _extract_line_items(self, invoice: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract line items from Stripe invoice.

        Args:
            invoice: Stripe invoice object

        Returns:
            List of line items
        """
        line_items = []

        if "lines" in invoice and "data" in invoice["lines"]:
            for item in invoice["lines"]["data"]:
                line_items.append(
                    {
                        "description": item.get("description", ""),
                        "amount": Decimal(str(item.get("amount", 0))) / 100,
                        "quantity": item.get("quantity", 1),
                        "currency": item.get("currency", "usd").upper(),
                    }
                )

        return line_items

    def _update_invoice_status(
        self,
        stripe_invoice_id: str,
        status: str,
        amount_paid: float | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Update invoice status in database.

        Args:
            stripe_invoice_id: Stripe invoice ID
            status: New status
            amount_paid: Amount paid (optional)
            metadata: Additional metadata (optional)
        """
        # Find invoice by Stripe ID
        invoice_id = stripe_invoice_id.replace("in_", "")
        invoice = self.db_client.get_invoice(invoice_id)

        if invoice:
            update_expr = "SET #status = :status, updated_at = :updated_at"
            expr_values = {":status": status, ":updated_at": datetime.now(UTC).isoformat()}

            if amount_paid is not None:
                update_expr += ", amount_paid = :amount_paid"
                expr_values[":amount_paid"] = Decimal(str(amount_paid))  # type: ignore[assignment]

            if metadata:
                update_expr += ", metadata = :metadata"
                expr_values[":metadata"] = metadata  # type: ignore[assignment]

            try:
                self.db_client.update_item(
                    pk=f"INVOICE#{invoice_id}",
                    sk="METADATA",
                    update_expression=update_expr,
                    expression_attribute_names={"#status": "status"},
                    expression_values=expr_values,
                )
            except Exception:
                logger.exception("Failed to update invoice status: ")

    def _update_billing_period_status(
        self, customer_id: str, period: str, status: str, invoice_id: str | None = None
    ) -> None:
        """Update billing period status in database.

        Args:
            customer_id: Customer ID
            period: Billing period (YYYY-MM)
            status: New status
            invoice_id: Associated invoice ID (optional)
        """
        year, month = map(int, period.split("-"))

        update_expr = "SET payment_status = :status"
        expr_values = {":status": status}

        if invoice_id:
            update_expr += ", invoice_id = :invoice_id"
            expr_values[":invoice_id"] = invoice_id

        try:
            self.db_client.update_item(
                pk=f"BILLING#{customer_id}",
                sk=f"PERIOD#{year:04d}-{month:02d}",
                update_expression=update_expr,
                expression_values=expr_values,
            )
        except Exception:
            logger.exception("Failed to update billing period status: ")

    def _update_customer_billing_status(self, customer_id: str, status: str) -> None:
        """Update customer billing status.

        Args:
            customer_id: Customer ID
            status: New billing status
        """
        try:
            self.db_client.update_item(
                pk=f"CUSTOMER#{customer_id}",
                sk="METADATA",
                update_expression="SET billing_status = :status, updated_at = :updated_at",
                expression_values={
                    ":status": status,
                    ":updated_at": datetime.now(UTC).isoformat(),
                },
            )
        except Exception:
            logger.exception("Failed to update customer billing status: ")
