"""Type definitions for the billing service.

This module provides TypedDict classes and Protocol interfaces to improve
type safety throughout the billing service. These replace generic dict[str, Any]
types with more specific and documented type structures.

This module now imports modern, infrastructure-agnostic types from event_types
while maintaining backward compatibility with the old names.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, NotRequired, Protocol, TypedDict

# Import new event processing types


# Stripe-related TypedDict definitions
class StripeCustomerDict(TypedDict):
    """Type definition for Stripe customer objects."""

    id: str
    email: str | None
    name: str | None
    metadata: dict[str, str]
    created: int
    currency: str | None
    default_source: str | None
    invoice_settings: dict[str, Any]
    subscriptions: dict[str, Any]


class StripeInvoiceDict(TypedDict):
    """Type definition for Stripe invoice objects."""

    id: str
    customer: str
    amount_due: int
    amount_paid: int
    amount_remaining: int
    currency: str
    status: str
    created: int
    due_date: int | None
    paid: bool
    metadata: dict[str, str]
    lines: dict[str, Any]
    payment_intent: str | None


class StripePaymentIntentDict(TypedDict):
    """Type definition for Stripe payment intent objects."""

    id: str
    amount: int
    currency: str
    status: str
    customer: str | None
    metadata: dict[str, str]
    created: int
    last_payment_error: dict[str, Any] | None


# Usage and billing calculation TypedDict definitions
class UsageBreakdownDict(TypedDict):
    """Type definition for usage breakdown in calculations."""

    tier: int
    usage: int  # Number of units used in this tier
    rate: float  # Price per unit as float for compatibility
    charges: float  # Total charges for this tier as float
    currency: str  # Currency code (e.g., "USD")
    description: NotRequired[str]  # Optional tier description
    tier_name: NotRequired[str]  # Optional tier name
    cumulative_units: NotRequired[int]  # Optional cumulative usage


class UsagePeriodDict(TypedDict):
    """Type definition for usage data by period."""

    customer_id: str
    period: str
    total_usage: int
    endpoint_breakdown: dict[str, int]
    record_count: int
    start_date: str
    end_date: str


class ChargeCalculationDict(TypedDict):
    """Type definition for charge calculation results."""

    customer_id: str
    total_usage: int
    total_charges: Decimal
    breakdown: list[UsageBreakdownDict]
    plan_type: str
    calculation_date: datetime
    currency: str


class ChargeEstimateDict(TypedDict):
    """Type definition for charge estimation results."""

    plan_type: str
    usage_count: int
    estimated_charges: float
    currency: str
    breakdown: list[UsageBreakdownDict]
    is_estimate: bool


class PeriodChargesDict(TypedDict):
    """Type definition for period charge calculations."""

    customer_id: str
    plan_type: str
    usage_count: int
    total_charges: float
    currency: str
    breakdown: list[UsageBreakdownDict]
    calculated_at: str
    period_start: str
    period_end: str
    year: int
    month: int


class PlanComparisonDict(TypedDict):
    """Type definition for plan comparison results."""

    plan_type: str
    estimated_cost: Decimal
    potential_savings: Decimal | None
    recommended: bool
    tier_breakdown: list[UsageBreakdownDict]


# Report generation TypedDict definitions
class UsageReportDict(TypedDict):
    """Type definition for usage reports."""

    report_type: str
    period: str
    customer_id: str | None
    total_requests: int
    unique_customers: int
    top_endpoints: list[dict[str, str | int]]
    usage_by_day: list[dict[str, str | int]]
    generated_at: datetime
    filters_applied: dict[str, Any]


class RevenueReportDict(TypedDict):
    """Type definition for revenue reports."""

    report_type: str
    period: str
    total_revenue: Decimal
    total_customers: int
    average_revenue_per_customer: Decimal
    revenue_by_plan: list[dict[str, str | Decimal | int]]
    growth_metrics: dict[str, Decimal | float]
    generated_at: datetime


class CustomerReportDict(TypedDict):
    """Type definition for customer reports."""

    report_type: str
    customer_id: str
    period: str
    total_usage: int
    total_charges: Decimal
    plan_type: str
    billing_history: list[dict[str, Any]]
    usage_trends: dict[str, int | float | list[dict[str, Any]]]
    generated_at: datetime


# Billing service operation result TypedDict definitions
class BillingStatusDict(TypedDict):
    """Type definition for billing status responses."""

    customer_id: str
    billing_status: str
    plan_type: str  # Customer's plan type
    current_usage: int
    current_charges: Decimal
    last_invoice_date: datetime | None
    next_billing_date: datetime | None
    payment_method_status: str | None
    outstanding_balance: Decimal


class InvoiceGenerationDict(TypedDict):
    """Type definition for invoice generation results."""

    invoice_id: str
    stripe_invoice_id: str | None
    customer_id: str
    amount: Decimal
    currency: str
    status: str
    due_date: datetime
    line_items: list[dict[str, str | int | Decimal]]
    generated_at: datetime


# Database operation TypedDict definitions
class DynamoDBItemDict(TypedDict):
    """Type definition for DynamoDB items."""

    pk: str
    sk: str
    gsi1pk: NotRequired[str]
    gsi1sk: NotRequired[str]
    # Additional fields are flexible since different item types have different schemas


# Protocol definitions for dependency injection and testing
class DatabaseClientProtocol(Protocol):
    """Protocol for database client implementations."""

    def put_item(self, item: dict[str, Any]) -> dict[str, Any]:
        """Store an item in the database."""
        ...

    def get_item(self, pk: str, sk: str) -> dict[str, Any] | None:
        """Retrieve an item from the database."""
        ...

    def query(self, **kwargs: Any) -> list[dict[str, Any]]:
        """Query items from the database."""
        ...

    def batch_write(self, items: list[dict[str, Any]], operation: str = "put") -> None:
        """Batch write items to the database."""
        ...


class PaymentProviderProtocol(Protocol):
    """Protocol for payment provider implementations."""

    def create_customer(
        self,
        email: str,
        name: str,
        metadata: dict[str, str] | None = None,
    ) -> StripeCustomerDict:
        """Create a customer in the payment provider."""
        ...

    def create_invoice(
        self,
        customer_id: str,
        amount: Decimal,
        currency: str = "USD",
        metadata: dict[str, str] | None = None,
    ) -> StripeInvoiceDict:
        """Create an invoice in the payment provider."""
        ...

    def get_customer(self, customer_id: str) -> StripeCustomerDict | None:
        """Get customer from payment provider."""
        ...


class EventPublisherProtocol(Protocol):
    """Protocol for event publishing implementations."""

    def publish_event(
        self,
        source: str,
        detail_type: str,
        detail: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Publish an event to the event bus."""
        ...


class ReportGeneratorProtocol(Protocol):
    """Protocol for report generator implementations."""

    def generate_usage_report(
        self,
        start_date: datetime,
        end_date: datetime,
        customer_id: str | None = None,
        group_by: str = "day",
    ) -> UsageReportDict:
        """Generate usage report."""
        ...

    def generate_revenue_report(
        self,
        year: int,
        month: int,
        group_by: str = "customer",
    ) -> RevenueReportDict:
        """Generate revenue report."""
        ...


# Utility type aliases for commonly used complex types
UsageBreakdownList = list[UsageBreakdownDict]
PlanComparisonList = list[PlanComparisonDict]
