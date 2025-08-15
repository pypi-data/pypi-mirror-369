"""Augint Billing Library.

A comprehensive billing service library for API usage tracking, tiered pricing
calculations, Stripe payment integration, and billing analytics. This library
provides all the components needed to implement usage-based billing for SaaS
applications.

The library is designed for serverless environments (AWS Lambda) but can be
used in any Python application. It integrates with AWS DynamoDB for data
storage, Stripe for payment processing, and EventBridge for event publishing.

Key Features:
    - Real-time API usage tracking with rate limiting
    - Tiered pricing calculations with multiple plan types
    - Stripe integration for payment processing and invoicing
    - Webhook processing for payment status updates
    - EventBridge integration for real-time billing events
    - Comprehensive usage and billing reports
    - Full type hints and async support

Components:
    - BillingService: Main coordinator for all billing operations
    - UsageCollector: Tracks and aggregates API usage
    - PricingCalculator: Applies tiered pricing rules
    - StripeManager: Handles Stripe API operations
    - StripeEventProcessor: Processes Stripe payment events (infrastructure-agnostic)
    - ReportGenerator: Creates usage and billing reports
    - EventPublisher: Publishes billing events to AWS EventBridge

Data Models:
    - Customer: Customer account information
    - UsageRecord: Individual usage tracking records
    - BillingPeriod: Monthly billing period data
    - PricingTier: Pricing tier configurations
    - Invoice: Invoice records and metadata

Utility Functions:
    - calculate_charges: Calculate charges with tiered pricing
    - validate_usage: Validate usage records before storage
    - format_currency: Format decimal amounts as currency

Example:
    Basic usage tracking and billing:

    >>> from augint_billing_lib import BillingService
    >>>
    >>> # Initialize service (uses environment variables)
    >>> service = BillingService()
    >>>
    >>> # Track API usage (publishes billing.usage.tracked event)
    >>> service.track_usage("CUST123", "/api/v1/process", usage_count=100)
    >>>
    >>> # Calculate monthly charges
    >>> charges = service.calculate_monthly_charges("CUST123", 2024, 1)
    >>> print(f"Total charges: ${charges['total_charges']}")
    >>>
    >>> # Generate and send invoice (publishes billing.invoice.created event)
    >>> invoice = service.generate_invoice("CUST123", "2024-01")

    Direct component usage:

    >>> from augint_billing_lib import UsageCollector, PricingCalculator, EventPublisher
    >>>
    >>> # Track usage directly
    >>> collector = UsageCollector()
    >>> collector.track_usage("CUST123", "/api/endpoint", 50)
    >>>
    >>> # Calculate charges directly
    >>> calculator = PricingCalculator()
    >>> charges = calculator.calculate_customer_charges("CUST123", 5000)
    >>>
    >>> # Publish custom billing events
    >>> publisher = EventPublisher()
    >>> publisher.publish_event("billing.service", "CustomEvent", {"data": "value"})

Environment Variables:
    The library uses the following TEST_ prefixed environment variables for configuration:

    - TEST_DYNAMODB_TABLE: DynamoDB table name for billing data
    - TEST_AWS_REGION: AWS region for services (default: us-east-1)
    - TEST_STRIPE_SECRET_KEY: Stripe API secret key
    - TEST_STRIPE_WEBHOOK_SECRET: Stripe webhook signature secret
    - TEST_EVENTBRIDGE_BUS: EventBridge bus name for events (default: billing-events)
    - TEST_ENVIRONMENT: Environment name (default: dev)
    - BILLING_EVENT_PUBLISHING_TIMEOUT: Event publish timeout in seconds (default: 5.0)
    - ENVIRONMENT: Deployment environment (dev/staging/prod)

For detailed documentation, see: https://docs.augint.ai/billing
"""

__version__ = "1.7.0"

# Import audit logging
from .audit import (
    AuditContext,
    AuditEvent,
    AuditLogger,
    AuditOperation,
    DynamoDBAuditStorage,
    SensitiveDataRedactor,
    audited,
)

# Import all public components for the library
from .billing_service import BillingService

# Import event publishing
from .event_publisher import EventPublisher

# Import modern event processing types
from .event_types import (
    EventHandler,
    EventHandlerMap,
    EventMetadata,
    EventProcessingResult,
    EventProcessor,
    EventResultUnion,
    EventSource,
    EventStore,
    EventValidator,
    InvoiceEventResult,
    PaymentEventResult,
    PaymentIntentEventResult,
    SignatureValidator,
    StripeEventData,
    SubscriptionEventResult,
    is_invoice_event,
    is_payment_event,
    is_subscription_event,
)

# Import data models
from .models import BillingPeriod, Customer, Invoice, PricingTier, UsageRecord
from .pricing_calculator import PricingCalculator
from .report_generator import ReportGenerator

# Import retry functionality
from .retry import (
    CircuitBreaker,
    CircuitBreakerError,
    CircuitState,
    MaxRetriesExceededError,
    RetryableError,
    RetryConfig,
    RetryError,
    ServiceRetryConfigs,
    retry_with_backoff,
)
from .stripe_event_processor import StripeEventProcessor
from .stripe_manager import StripeManager

# Import other type definitions (for type annotations and documentation)
from .types import (
    BillingStatusDict,
    ChargeCalculationDict,
    CustomerReportDict,
    DatabaseClientProtocol,
    EventPublisherProtocol,
    InvoiceGenerationDict,
    PaymentProviderProtocol,
    PeriodChargesDict,
    PlanComparisonDict,
    ReportGeneratorProtocol,
    RevenueReportDict,
    StripeCustomerDict,
    StripeInvoiceDict,
    StripePaymentIntentDict,
    UsageBreakdownDict,
    UsageBreakdownList,
    UsageReportDict,
)
from .usage_collector import UsageCollector

# Import utility functions
from .utils import (
    calculate_charges,
    calculate_due_date,
    calculate_proration,
    format_currency,
    generate_invoice_number,
    get_billing_period_bounds,
    validate_usage,
    verify_stripe_signature,
)

# Define public API
__all__ = [
    "AuditContext",
    "AuditEvent",
    "AuditLogger",
    "AuditOperation",
    "BillingPeriod",
    "BillingService",
    "BillingStatusDict",
    "ChargeCalculationDict",
    "CircuitBreaker",
    "CircuitBreakerError",
    "CircuitState",
    "Customer",
    "CustomerReportDict",
    "DatabaseClientProtocol",
    "DynamoDBAuditStorage",
    "EventHandler",
    "EventHandlerMap",
    "EventMetadata",
    "EventProcessingResult",
    "EventProcessor",
    "EventPublisher",
    "EventPublisherProtocol",
    "EventResultUnion",
    "EventSource",
    "EventStore",
    "EventValidator",
    "Invoice",
    "InvoiceEventResult",
    "InvoiceGenerationDict",
    "MaxRetriesExceededError",
    "PaymentEventResult",
    "PaymentIntentEventResult",
    "PaymentProviderProtocol",
    "PeriodChargesDict",
    "PlanComparisonDict",
    "PricingCalculator",
    "PricingTier",
    "ReportGenerator",
    "ReportGeneratorProtocol",
    "RetryConfig",
    "RetryError",
    "RetryableError",
    "RevenueReportDict",
    "SensitiveDataRedactor",
    "ServiceRetryConfigs",
    "SignatureValidator",
    "StripeCustomerDict",
    "StripeEventData",
    "StripeEventProcessor",
    "StripeInvoiceDict",
    "StripeManager",
    "StripePaymentIntentDict",
    "SubscriptionEventResult",
    "UsageBreakdownDict",
    "UsageBreakdownList",
    "UsageCollector",
    "UsageRecord",
    "UsageReportDict",
    "audited",
    "calculate_charges",
    "calculate_due_date",
    "calculate_proration",
    "format_currency",
    "generate_invoice_number",
    "get_billing_period_bounds",
    "is_invoice_event",
    "is_payment_event",
    "is_subscription_event",
    "retry_with_backoff",
    "validate_usage",
    "verify_stripe_signature",
]
