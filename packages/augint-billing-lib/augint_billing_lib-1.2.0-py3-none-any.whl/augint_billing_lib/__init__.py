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
    - WebhookProcessor: Processes Stripe webhook events
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
    The library uses the following environment variables for configuration:

    - DYNAMODB_TABLE: DynamoDB table name for billing data
    - AWS_REGION: AWS region for services (default: us-east-1)
    - STRIPE_SECRET_KEY: Stripe API secret key
    - STRIPE_WEBHOOK_SECRET: Stripe webhook signature secret
    - EVENTBRIDGE_BUS: EventBridge bus name for events (default: billing-events)
    - BILLING_ENABLE_EVENT_PUBLISHING: Enable/disable event publishing (default: true)
    - BILLING_EVENT_PUBLISHING_TIMEOUT: Event publish timeout in seconds (default: 5.0)
    - ENVIRONMENT: Deployment environment (dev/staging/prod)

For detailed documentation, see: https://docs.augint.ai/billing
"""

__version__ = "1.2.0"

# Import all public components for the library
from .billing_service import BillingService

# Import event publishing
from .event_publisher import EventPublisher

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
from .stripe_manager import StripeManager

# Import type definitions (for type annotations and documentation)
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
    StripeEventHandler,
    StripeInvoiceDict,
    StripePaymentIntentDict,
    StripeWebhookEventDict,
    UsageBreakdownDict,
    UsageBreakdownList,
    UsageReportDict,
    WebhookProcessingDict,
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
    verify_webhook_signature,
)
from .webhook_processor import WebhookProcessor

# Define public API
__all__ = [
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
    "EventPublisher",
    "EventPublisherProtocol",
    "Invoice",
    "InvoiceGenerationDict",
    "MaxRetriesExceededError",
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
    "ServiceRetryConfigs",
    "StripeCustomerDict",
    "StripeEventHandler",
    "StripeInvoiceDict",
    "StripeManager",
    "StripePaymentIntentDict",
    "StripeWebhookEventDict",
    "UsageBreakdownDict",
    "UsageBreakdownList",
    "UsageCollector",
    "UsageRecord",
    "UsageReportDict",
    "WebhookProcessingDict",
    "WebhookProcessor",
    "calculate_charges",
    "calculate_due_date",
    "calculate_proration",
    "format_currency",
    "generate_invoice_number",
    "get_billing_period_bounds",
    "retry_with_backoff",
    "validate_usage",
    "verify_webhook_signature",
]
