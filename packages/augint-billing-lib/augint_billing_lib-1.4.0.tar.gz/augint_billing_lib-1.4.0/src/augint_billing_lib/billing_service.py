"""Main billing service coordinator module.

This module provides the BillingService class which orchestrates all billing
operations including usage tracking, charge calculations, Stripe integration,
and report generation. It serves as the primary entry point for the library.

The BillingService aggregates functionality from specialized components:
- UsageCollector for tracking API usage
- PricingCalculator for tiered pricing calculations
- StripeManager for payment processing
- ReportGenerator for analytics and reporting
- WebhookProcessor for handling Stripe events
- EventPublisher for publishing billing events to EventBridge

Typical usage example:
    from augint_billing_lib import BillingService

    # Initialize with environment variables
    service = BillingService()

    # Track usage (publishes billing.usage.tracked event)
    service.track_usage("CUST123", "/api/endpoint", 100)

    # Calculate charges for a customer
    charges = service.calculate_charges("CUST123", usage_count=5000)

    # Generate invoice (publishes billing.invoice.created event)
    invoice = service.generate_invoice("CUST123", "2024-01")
"""

import json
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional, Union

from .audit import AuditLogger, AuditOperation, DynamoDBAuditStorage, audited
from .config import get_settings
from .db import DynamoDBClient
from .event_publisher import EventPublisher
from .exceptions import BillingServiceError, CustomerNotFoundError, StripeError
from .models import (
    Customer,
    CustomerCreatedEvent,
    Invoice,
    InvoiceCreatedEvent,
    UsageTrackedEvent,
)
from .pricing_calculator import PricingCalculator
from .report_generator import ReportGenerator
from .stripe_manager import StripeManager
from .types import (
    PeriodChargesDict,
    WebhookEventResultDict,
)
from .usage_collector import UsageCollector
from .utils import (
    calculate_due_date,
    generate_invoice_number,
    get_billing_period_bounds,
)
from .webhook_processor import WebhookProcessor

# Sentinel value to distinguish between "not provided" and "explicitly None"
_EVENTBRIDGE_UNSET = object()

logger = logging.getLogger(__name__)


class BillingService:
    """Main billing service coordinator for all billing operations.

    This class provides a unified interface to all billing functionality,
    coordinating between usage tracking, pricing calculation, payment
    processing, event publishing, and reporting components.

    Attributes:
        table_name: DynamoDB table name for billing data
        stripe_key: Stripe API secret key
        event_bus: EventBridge bus name for billing events
        event_publisher: Component for publishing billing events to EventBridge
        usage_collector: Component for tracking API usage
        pricing_calculator: Component for calculating charges
        stripe_manager: Component for Stripe integration
        webhook_processor: Component for webhook handling
        report_generator: Component for generating reports
        db_client: DynamoDB client for direct database operations

    Example:
        >>> # Initialize with default environment variables
        >>> service = BillingService()

        >>> # Or with explicit configuration
        >>> service = BillingService(
        ...     table_name="billing-data-prod",
        ...     stripe_secret_key="sk_live_..."
        ... )

        >>> # Track API usage
        >>> service.track_usage("CUST123", "/api/v1/process", 50)

        >>> # Calculate monthly charges
        >>> charges = service.calculate_monthly_charges("CUST123", 2024, 1)
        >>> print(f"Total charges: ${charges['total_charges']}")
    """

    # Class attributes with type annotations
    table_name: str
    stripe_key: Optional[str]
    event_bus: Optional[str]
    event_publisher: Optional[Any]
    usage_collector: Any
    pricing_calculator: Any
    stripe_manager: Any
    webhook_processor: Any
    report_generator: Any
    db_client: Any
    settings: Any
    audit_logger: Optional[AuditLogger]

    def __init__(
        self,
        table_name: Optional[str] = None,
        stripe_secret_key: Optional[str] = None,
        eventbridge_bus: Union[str, None, object] = _EVENTBRIDGE_UNSET,
        enable_events: bool = True,
        audit_logger: Optional[AuditLogger] = None,
    ) -> None:
        """Initialize the billing service with configuration.

        All parameters are optional and will fall back to environment variables
        if not provided. This allows for flexible configuration in different
        deployment environments.

        Args:
            table_name: DynamoDB table name for billing data.
                Falls back to TEST_DYNAMODB_TABLE environment variable.
            stripe_secret_key: Stripe API secret key for payment processing.
                Falls back to TEST_STRIPE_SECRET_KEY environment variable.
            eventbridge_bus: EventBridge bus name for publishing billing events.
                Falls back to TEST_EVENTBRIDGE_BUS environment variable.
            enable_events: Whether to enable event publishing. Defaults to True.
            audit_logger: Optional audit logger for compliance logging.
                Defaults to DynamoDB-based logger with graceful degradation.

        Raises:
            BillingServiceError: If required configuration is missing or invalid.

        Example:
            >>> # Use environment variables
            >>> service = BillingService()

            >>> # Override specific settings
            >>> service = BillingService(table_name="billing-data-test")
        """
        settings = get_settings()

        # Configuration
        self.table_name = table_name or settings.dynamodb_table
        self.stripe_key = (
            stripe_secret_key if stripe_secret_key is not None else settings.stripe_secret_key
        )
        # Handle EventBridge bus parameter: use None if explicitly provided,
        # otherwise use settings fallback
        if eventbridge_bus is _EVENTBRIDGE_UNSET:
            self.event_bus = settings.eventbridge_bus
        else:
            self.event_bus = (
                eventbridge_bus if isinstance(eventbridge_bus, (str, type(None))) else None
            )
        self.settings = settings

        # Validate required configuration
        if not self.table_name:
            raise BillingServiceError("DynamoDB table name is required")

        # Initialize components
        try:
            self.db_client = DynamoDBClient(table_name=self.table_name)
            self.usage_collector = UsageCollector(table_name=self.table_name)
            self.pricing_calculator = PricingCalculator(table_name=self.table_name)
            self.stripe_manager = StripeManager(api_key=self.stripe_key)
            self.webhook_processor = WebhookProcessor(
                stripe_manager=self.stripe_manager, db_client=self.db_client
            )
            self.report_generator = ReportGenerator(
                table_name=self.table_name, stripe_manager=self.stripe_manager
            )

            # Initialize event publisher if enabled
            self.event_publisher = None
            if enable_events and self.event_bus:
                try:
                    self.event_publisher = EventPublisher(
                        enabled=True,
                        bus_name=self.event_bus,
                        region_name=settings.aws_region,
                    )
                    logger.debug("EventPublisher initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize EventPublisher: {e}")
                    self.event_publisher = None

            # Initialize audit logger with graceful degradation
            self.audit_logger = audit_logger
            if self.audit_logger is None:
                try:
                    audit_storage = DynamoDBAuditStorage(
                        table_name=self.table_name,
                        is_critical=False,  # Graceful degradation
                    )
                    self.audit_logger = AuditLogger(storage=audit_storage)
                    logger.debug("Audit logger initialized successfully")
                except Exception as e:
                    logger.warning(f"Failed to initialize audit logger: {e}")
                    self.audit_logger = None

            logger.info(
                f"Initialized BillingService with table: {self.table_name}, "
                f"event bus: {self.event_bus}, events enabled: {self.event_publisher is not None}, "
                f"audit enabled: {self.audit_logger is not None}"
            )

        except Exception as e:
            logger.exception("Failed to initialize BillingService")
            raise BillingServiceError(f"Service initialization failed: {e!s}") from e

    @audited(AuditOperation.USAGE_TRACK, "usage", "customer_id", capture_after_state=True)
    def track_usage(
        self,
        customer_id: str,
        api_endpoint: str,
        usage_count: int = 1,
        timestamp: Optional[datetime] = None,
        check_rate_limit: bool = True,
    ) -> dict[str, Any]:
        """Track API usage for a customer.

        Records API usage in DynamoDB with automatic rate limit checking
        and validation. Usage records are aggregated for billing calculations.

        Args:
            customer_id: Unique identifier for the customer.
            api_endpoint: API endpoint that was called (e.g., "/api/v1/process").
            usage_count: Number of API calls to record. Defaults to 1.
            timestamp: When the usage occurred. Defaults to current time.
            check_rate_limit: Whether to enforce rate limits. Defaults to True.

        Returns:
            Dictionary containing the created usage record details including:
            - usage_id: Unique identifier for this usage record
            - customer_id: Customer identifier
            - api_endpoint: API endpoint called
            - usage_count: Number of calls recorded
            - timestamp: When usage was recorded
            - daily_total: Current daily usage total for customer

        Raises:
            CustomerNotFoundError: If customer doesn't exist in the system.
            RateLimitError: If customer has exceeded their rate limit.
            UsageValidationError: If usage data is invalid.
            DynamoDBError: If database operation fails.

        Example:
            >>> # Track single API call
            >>> result = service.track_usage("CUST123", "/api/v1/process")

            >>> # Track batch of calls
            >>> result = service.track_usage("CUST123", "/api/v1/process", 100)

            >>> # Track with specific timestamp
            >>> from datetime import datetime
            >>> result = service.track_usage(
            ...     "CUST123",
            ...     "/api/v1/process",
            ...     timestamp=datetime(2024, 1, 15, 10, 30, 0)
            ... )
        """
        usage_record = self.usage_collector.track_usage(
            customer_id=customer_id,
            api_endpoint=api_endpoint,
            usage_count=usage_count,
            timestamp=timestamp,
            check_rate_limit=check_rate_limit,
        )

        # Publish usage tracked event after successful operation
        if self.event_publisher:
            try:
                # Determine billing period for the usage
                usage_timestamp = timestamp or datetime.now(timezone.utc)
                period = usage_timestamp.strftime("%Y-%m")

                event = UsageTrackedEvent(
                    customer_id=customer_id,
                    endpoint=api_endpoint,
                    usage_count=usage_count,
                    period=period,
                    environment=self.settings.environment,
                )
                self.event_publisher.publish_event(
                    source=event.source,
                    detail_type="billing.usage.tracked",
                    detail=event.model_dump(mode="json"),
                )
            except Exception as e:
                logger.warning(f"Failed to publish usage tracked event: {e}")

        return usage_record.model_dump()  # type: ignore[no-any-return]

    def calculate_charges(
        self,
        customer_id: str,
        usage_count: Optional[int] = None,
        period: Optional[str] = None,
        save_to_db: bool = False,
    ) -> dict[str, Any]:
        """Calculate charges for customer usage.

        Applies tiered pricing rules based on the customer's plan to calculate
        charges. Can calculate for specific usage amount or entire billing period.

        Args:
            customer_id: Customer to calculate charges for.
            usage_count: Specific usage amount to calculate. If None, calculates
                for entire period.
            period: Billing period in YYYY-MM format. Required if usage_count
                is None.
            save_to_db: Whether to save the billing period to database.
                Defaults to False.

        Returns:
            Dictionary containing charge calculation details:
            - customer_id: Customer identifier
            - plan_type: Customer's billing plan
            - usage_count: Total usage calculated
            - total_charges: Total charges in decimal
            - currency: Currency code (e.g., "USD")
            - breakdown: List of charges by pricing tier
            - calculated_at: Timestamp of calculation

        Raises:
            CustomerNotFoundError: If customer doesn't exist.
            PricingConfigurationError: If pricing configuration is invalid.
            BillingPeriodError: If period data is invalid.

        Example:
            >>> # Calculate charges for specific usage
            >>> charges = service.calculate_charges("CUST123", usage_count=5000)
            >>> print(f"Total: ${charges['total_charges']}")

            >>> # Calculate for entire billing period
            >>> charges = service.calculate_charges(
            ...     "CUST123",
            ...     period="2024-01",
            ...     save_to_db=True
            ... )
        """
        if usage_count is None and period:
            # Get usage for the period
            year, month = map(int, period.split("-"))
            usage_data = self.usage_collector.get_usage_by_period(customer_id, year, month)
            usage_count = usage_data["total_usage"]

        return self.pricing_calculator.calculate_customer_charges(  # type: ignore[no-any-return]
            customer_id=customer_id,
            usage_count=usage_count or 0,
            period=period,
            save_to_db=save_to_db,
        )

    def calculate_monthly_charges(
        self, customer_id: str, year: int, month: int
    ) -> PeriodChargesDict:
        """Calculate charges for a complete monthly billing period.

        Aggregates all usage for the specified month and calculates charges
        using the customer's pricing plan.

        Args:
            customer_id: Customer to calculate charges for.
            year: Billing year (e.g., 2024).
            month: Billing month (1-12).

        Returns:
            Dictionary containing monthly charge details:
            - customer_id: Customer identifier
            - period_start: Start of billing period
            - period_end: End of billing period
            - usage_count: Total usage in period
            - total_charges: Total charges calculated
            - breakdown: Detailed charge breakdown by tier
            - year: Billing year
            - month: Billing month

        Raises:
            CustomerNotFoundError: If customer doesn't exist.
            BillingPeriodError: If period data is invalid.

        Example:
            >>> # Calculate January 2024 charges
            >>> charges = service.calculate_monthly_charges("CUST123", 2024, 1)
            >>> print(f"January total: ${charges['total_charges']}")
        """
        return self.pricing_calculator.calculate_period_charges(  # type: ignore[no-any-return]
            customer_id=customer_id, year=year, month=month
        )

    @audited(AuditOperation.INVOICE_CREATE, "invoice", "customer_id", capture_after_state=True)
    def generate_invoice(
        self,
        customer_id: str,
        period: str,
        send_to_stripe: bool = True,
        stripe_idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        """Generate an invoice for a billing period.

        Creates an invoice for the specified billing period, optionally
        sending it to Stripe for payment collection. Uses natural key
        deduplication to prevent duplicate invoices for the same period.

        Args:
            customer_id: Customer to invoice.
            period: Billing period in YYYY-MM format.
            send_to_stripe: Whether to create invoice in Stripe.
                Defaults to True.
            stripe_idempotency_key: Optional Stripe idempotency key for safe retries.
                If not provided, generates deterministic key from customer_id and period.

        Returns:
            Dictionary containing invoice details:
            - invoice_id: Unique invoice identifier
            - customer_id: Customer identifier
            - stripe_invoice_id: Stripe's invoice ID (if sent)
            - amount: Invoice amount
            - currency: Currency code
            - status: Invoice status
            - due_date: Payment due date
            - line_items: Detailed line items

        Raises:
            CustomerNotFoundError: If customer doesn't exist.
            StripeIntegrationError: If Stripe operation fails.
            BillingPeriodError: If period data is invalid.

        Example:
            >>> # Generate and send invoice to Stripe
            >>> invoice = service.generate_invoice("CUST123", "2024-01")
            >>> print(f"Invoice {invoice['invoice_id']}: ${invoice['amount']}")

            >>> # Generate draft invoice without sending
            >>> invoice = service.generate_invoice(
            ...     "CUST123",
            ...     "2024-01",
            ...     send_to_stripe=False
            ... )

            >>> # Generate with idempotency key for safe retries
            >>> invoice = service.generate_invoice(
            ...     "CUST123",
            ...     "2024-01",
            ...     stripe_idempotency_key="invoice_CUST123_2024_01"
            ... )
        """
        # Natural key deduplication - check if invoice already exists for this period
        invoice_id = generate_invoice_number(customer_id, period)

        # Check for existing invoice using natural business key
        try:
            existing_invoice_data = self.db_client.get_item(
                pk=f"INVOICE#{invoice_id}", sk="METADATA"
            )
            if existing_invoice_data:
                logger.info(
                    f"Invoice {invoice_id} already exists for period {period}, returning cached"
                )
                return existing_invoice_data  # type: ignore[no-any-return]
        except Exception as e:
            logger.debug(f"No existing invoice found for {invoice_id}: {e}")

        # Calculate charges for the period
        year, month = map(int, period.split("-"))
        charges = self.calculate_monthly_charges(customer_id, year, month)

        # Generate invoice through Stripe manager
        if send_to_stripe and self.stripe_key:
            # Get customer's Stripe customer ID
            customer_data = self.db_client.get_customer(customer_id)
            if not customer_data:
                raise CustomerNotFoundError(customer_id)

            stripe_customer_id = customer_data.get("stripe_customer_id")
            if not stripe_customer_id:
                raise StripeError(
                    f"Customer {customer_id} has no Stripe customer ID",
                    stripe_error_code="no_stripe_customer_id",
                )

            # Generate or use provided idempotency key
            if not stripe_idempotency_key:
                stripe_idempotency_key = f"invoice_{invoice_id}"

            # Create invoice in Stripe with idempotency key
            stripe_result = self.stripe_manager.create_invoice(
                customer_id=stripe_customer_id,  # Pass stripe customer ID
                amount=Decimal(str(charges["total_charges"])),
                description=f"Usage charges for {period}",
                metadata={
                    "period": period,
                    "usage_count": charges["usage_count"],
                    "internal_invoice_id": invoice_id,
                },
                idempotency_key=stripe_idempotency_key,
            )

            # Create local record with Stripe invoice ID
            invoice = Invoice(
                pk=f"INVOICE#{invoice_id}",
                invoice_id=invoice_id,
                customer_id=customer_id,
                stripe_invoice_id=stripe_result["id"],
                amount=Decimal(str(charges["total_charges"])),
                currency=str(charges.get("currency", "USD")),
                status=stripe_result["status"],
                due_date=calculate_due_date(datetime.now(timezone.utc)),
                line_items=[
                    {
                        "description": f"API usage for {period}",
                        "quantity": charges["usage_count"],
                        "amount": Decimal(str(charges["total_charges"])),
                    }
                ],
            )

            # Save to database
            self.db_client.put_item(invoice.model_dump())

            # Publish invoice created event after successful operation
            if self.event_publisher:
                try:
                    event = InvoiceCreatedEvent(
                        customer_id=customer_id,
                        invoice_id=invoice_id,
                        amount=invoice.amount,
                        period=period,
                        due_date=invoice.due_date,
                        environment=self.settings.environment,
                    )
                    self.event_publisher.publish_event(
                        source=event.source,
                        detail_type="billing.invoice.created",
                        detail=event.model_dump(mode="json"),
                    )
                except Exception as e:
                    logger.warning(f"Failed to publish invoice created event: {e}")

            return invoice.model_dump()
        # Create local invoice only

        invoice_id = generate_invoice_number(customer_id, period)
        invoice = Invoice(
            pk=f"INVOICE#{invoice_id}",
            invoice_id=invoice_id,
            customer_id=customer_id,
            stripe_invoice_id="",
            amount=Decimal(str(charges["total_charges"])),
            currency=str(charges.get("currency", "USD")),
            status="draft",
            due_date=calculate_due_date(datetime.now(timezone.utc)),
            line_items=[
                {
                    "description": f"API usage for {period}",
                    "quantity": charges["usage_count"],
                    "amount": Decimal(str(charges["total_charges"])),
                }
            ],
        )

        # Save to database
        self.db_client.put_item(invoice.model_dump())

        # Publish invoice created event after successful operation (draft invoice)
        if self.event_publisher:
            try:
                event = InvoiceCreatedEvent(
                    customer_id=customer_id,
                    invoice_id=invoice_id,
                    amount=invoice.amount,
                    period=period,
                    due_date=invoice.due_date,
                    environment=self.settings.environment,
                )
                self.event_publisher.publish_event(
                    source=event.source,
                    detail_type="billing.invoice.created",
                    detail=event.model_dump(mode="json"),
                )
            except Exception as e:
                logger.warning(f"Failed to publish invoice created event: {e}")

        return invoice.model_dump()

    def process_webhook(
        self,
        event_type: str,
        event_data: dict[str, Any],
        signature: Optional[str] = None,
        validate_signature: bool = True,
    ) -> WebhookEventResultDict:
        """Process incoming webhook events from Stripe.

        Handles Stripe webhook events for payment status updates, subscription
        changes, and other billing events.

        Args:
            event_type: Type of webhook event (e.g., "payment_intent.succeeded").
            event_data: Event payload from Stripe.
            signature: Webhook signature for validation.
            validate_signature: Whether to validate the signature.
                Defaults to True.

        Returns:
            Dictionary containing processing result:
            - processed: Whether event was successfully processed
            - action_taken: Description of action taken
            - updated_records: Number of records updated

        Raises:
            WebhookValidationError: If signature validation fails.
            WebhookProcessingError: If event processing fails.

        Example:
            >>> # Process payment success webhook
            >>> result = service.process_webhook(
            ...     "payment_intent.succeeded",
            ...     {"id": "pi_123", "amount": 5000},
            ...     signature="whsec_..."
            ... )
        """
        # Convert event to JSON payload
        payload_dict = {"type": event_type, "data": {"object": event_data}}
        payload = json.dumps(payload_dict).encode()

        return self.webhook_processor.process_webhook(  # type: ignore[no-any-return]
            payload=payload,
            signature=signature or "",
            validate_signature=validate_signature,
        )

    def generate_usage_report(
        self,
        customer_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        group_by: str = "day",
    ) -> dict[str, Any]:
        """Generate a usage report for analysis.

        Creates detailed usage reports with aggregation and filtering options.

        Args:
            customer_id: Filter by specific customer. None for all customers.
            start_date: Report start date. Defaults to 30 days ago.
            end_date: Report end date. Defaults to today.
            group_by: Aggregation level - "day", "week", or "month".
                Defaults to "day".

        Returns:
            Dictionary containing report data:
            - report_id: Unique report identifier
            - period: Report period details
            - total_usage: Total usage in period
            - total_customers: Number of unique customers
            - usage_by_period: Usage aggregated by time period
            - top_customers: Highest usage customers
            - top_endpoints: Most called API endpoints

        Example:
            >>> # Generate monthly report for specific customer
            >>> report = service.generate_usage_report(
            ...     customer_id="CUST123",
            ...     start_date=datetime(2024, 1, 1),
            ...     end_date=datetime(2024, 1, 31),
            ...     group_by="week"
            ... )
        """
        return self.report_generator.generate_usage_report(  # type: ignore[no-any-return]
            customer_id=customer_id, start_date=start_date, end_date=end_date, group_by=group_by
        )

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer details from database.

        Args:
            customer_id: Customer identifier to retrieve.

        Returns:
            Customer object if found, None otherwise.

        Example:
            >>> customer = service.get_customer("CUST123")
            >>> if customer:
            ...     print(f"Customer: {customer.name} ({customer.plan_type})")
        """
        data = self.db_client.get_customer(customer_id)
        if data:
            return Customer(**data)
        return None

    @audited(AuditOperation.CUSTOMER_CREATE, "customer", "customer_id", capture_after_state=True)
    def create_customer(
        self,
        customer_id: str,
        email: str,
        name: str,
        plan_type: str = "free",
        create_in_stripe: bool = True,
        stripe_idempotency_key: Optional[str] = None,
    ) -> Customer:
        """Create a new customer in the billing system.

        Args:
            customer_id: Unique customer identifier.
            email: Customer email address.
            name: Customer full name.
            plan_type: Billing plan - "free", "paid", or "enterprise".
                Defaults to "free".
            create_in_stripe: Whether to create customer in Stripe.
                Defaults to True.
            stripe_idempotency_key: Optional Stripe idempotency key for safe retries.

        Returns:
            Created Customer object.

        Raises:
            DynamoDBError: If database operation fails.
            StripeIntegrationError: If Stripe creation fails.

        Example:
            >>> customer = service.create_customer(
            ...     "CUST123",
            ...     "customer@example.com",
            ...     "John Doe",
            ...     plan_type="paid"
            ... )

            >>> # Create with idempotency key for safe retries
            >>> customer = service.create_customer(
            ...     "CUST123",
            ...     "customer@example.com",
            ...     "John Doe",
            ...     stripe_idempotency_key="customer_CUST123"
            ... )
        """
        # Create in Stripe if requested
        stripe_customer_id = None
        if create_in_stripe and self.stripe_key:
            # Generate or use provided idempotency key
            if not stripe_idempotency_key:
                stripe_idempotency_key = f"customer_{customer_id}"

            stripe_customer = self.stripe_manager.create_customer(
                customer_id=customer_id,
                email=email,
                name=name,
                idempotency_key=stripe_idempotency_key,
            )
            stripe_customer_id = stripe_customer.get("id")

        # Create customer model
        customer = Customer(
            pk=f"CUSTOMER#{customer_id}",
            customer_id=customer_id,
            stripe_customer_id=stripe_customer_id,
            email=email,
            name=name,
            plan_type=plan_type,
            billing_status="active",
        )

        # Save to database
        self.db_client.put_item(customer.model_dump())

        # Publish customer created event after successful operation
        if self.event_publisher:
            try:
                event = CustomerCreatedEvent(
                    customer_id=customer_id,
                    stripe_customer_id=stripe_customer_id or "",
                    email=email,
                    plan_type=plan_type,
                    environment=self.settings.environment,
                )
                self.event_publisher.publish_event(
                    source=event.source,
                    detail_type="billing.customer.created",
                    detail=event.model_dump(mode="json"),
                )
            except Exception as e:
                logger.warning(f"Failed to publish customer created event: {e}")

        logger.info(f"Created customer {customer_id} with plan {plan_type}")
        return customer

    def update_customer_plan(self, customer_id: str, new_plan_type: str) -> Customer:
        """Update a customer's billing plan.

        Args:
            customer_id: Customer to update.
            new_plan_type: New plan type - "free", "paid", or "enterprise".

        Returns:
            Updated Customer object.

        Raises:
            CustomerNotFoundError: If customer doesn't exist.
            DynamoDBError: If database operation fails.

        Example:
            >>> # Upgrade customer to paid plan
            >>> customer = service.update_customer_plan("CUST123", "paid")
            >>> print(f"Updated to {customer.plan_type} plan")
        """
        # Get existing customer
        customer = self.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)
        # Update plan
        customer.plan_type = new_plan_type
        customer.updated_at = datetime.now(timezone.utc)

        # Save changes
        self.db_client.put_item(customer.model_dump())

        logger.info(f"Updated customer {customer_id} to plan {new_plan_type}")
        return customer

    def get_billing_status(self, customer_id: str) -> dict[str, Any]:
        """Get comprehensive billing status for a customer.

        Args:
            customer_id: Customer to check status for.

        Returns:
            Dictionary containing billing status:
            - customer_id: Customer identifier
            - plan_type: Current billing plan
            - billing_status: Active, past_due, or cancelled
            - current_usage: Usage in current period
            - estimated_charges: Estimated charges for current period
            - last_invoice: Details of most recent invoice
            - payment_method: Configured payment method info

        Raises:
            CustomerNotFoundError: If customer doesn't exist.

        Example:
            >>> status = service.get_billing_status("CUST123")
            >>> print(f"Current usage: {status['current_usage']}")
            >>> print(f"Estimated charges: ${status['estimated_charges']}")
        """
        # Get customer
        customer = self.get_customer(customer_id)
        if not customer:
            raise CustomerNotFoundError(customer_id)

        # Get current period usage
        period_start, _ = get_billing_period_bounds()
        now = datetime.now(timezone.utc)

        current_usage = self.usage_collector.get_usage_by_period(
            customer_id=customer_id, year=now.year, month=now.month
        )

        # Estimate charges
        estimated = self.pricing_calculator.estimate_charges(
            plan_type=customer.plan_type, usage_count=current_usage["total_usage"]
        )

        # Get last invoice
        last_invoice = None
        try:
            invoices = self.db_client.query_invoices_by_customer(customer_id, limit=1)
            if invoices:
                last_invoice = invoices[0]
        except Exception as e:
            logger.warning(f"Could not retrieve last invoice: {e}")

        # Get payment method from Stripe
        payment_method = None
        if customer.stripe_customer_id and self.stripe_key:
            try:
                payment_method = self.stripe_manager.get_payment_method(customer.stripe_customer_id)
            except Exception as e:
                logger.warning(f"Could not retrieve payment method: {e}")

        return {
            "customer_id": customer_id,
            "billing_status": customer.billing_status,
            "plan_type": customer.plan_type,
            "current_usage": current_usage["total_usage"],
            "current_charges": Decimal(str(estimated["estimated_charges"])),
            "estimated_charges": Decimal(
                str(estimated["estimated_charges"])
            ),  # For backward compatibility
            "currency": estimated.get("currency", "USD"),
            "last_invoice": last_invoice,
            "last_invoice_date": datetime.fromisoformat(last_invoice["created_at"])
            if last_invoice and "created_at" in last_invoice
            else None,
            "next_billing_date": period_start.replace(month=period_start.month + 1)
            if period_start.month < 12
            else period_start.replace(year=period_start.year + 1, month=1),
            "payment_method": payment_method,
            "payment_method_status": "configured" if payment_method else "missing",
            "outstanding_balance": Decimal("0.00"),  # TODO: Calculate from unpaid invoices
            "period_start": period_start.isoformat(),
            "checked_at": datetime.now(timezone.utc).isoformat(),
        }

    def close(self) -> None:
        """Close connections and clean up resources.

        Should be called when the service is no longer needed to ensure
        proper cleanup of connections and resources.

        Example:
            >>> service = BillingService()
            >>> try:
            ...     # Use service
            ...     service.track_usage("CUST123", "/api/endpoint")
            >>> finally:
            ...     service.close()
        """
        # Clean up any connections or resources
        logger.info("Closing BillingService")
        # Components handle their own cleanup if needed
