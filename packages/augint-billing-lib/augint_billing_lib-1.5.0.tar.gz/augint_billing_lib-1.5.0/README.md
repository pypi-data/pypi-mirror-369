# Augint Billing Library

**Production-ready billing service library for API usage tracking, tiered pricing calculations, and Stripe integration.**

[![CI Pipeline](https://github.com/svange/augint-billing-lib/actions/workflows/pipeline.yaml/badge.svg?branch=main)](https://github.com/svange/augint-billing-lib/actions/workflows/pipeline.yaml)
[![PyPI](https://img.shields.io/pypi/v/augint-billing-lib?style=flat-square)](https://pypi.org/project/augint-billing-lib/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

[![Poetry](https://img.shields.io/badge/dependency%20manager-poetry-blue?style=flat-square)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit)](https://github.com/pre-commit/pre-commit)

[![pytest](https://img.shields.io/badge/testing-pytest-green?style=flat-square&logo=pytest)](https://pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue?style=flat-square&logo=github-actions)](https://github.com/features/actions)
[![Semantic Release](https://img.shields.io/badge/release-semantic--release-e10079?style=flat-square&logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0)

## 📊 Live Dashboards

| 📖 **[Documentation](https://svange.github.io/augint-billing-lib)** | 🧪 **[Unit Tests](https://svange.github.io/augint-billing-lib/unit-test-report.html)** | 🔬 **[Integration Tests](https://svange.github.io/augint-billing-lib/integration-test-report.html)** | 📊 **[Coverage](https://svange.github.io/augint-billing-lib/htmlcov/index.html)** | ⚡ **[Benchmarks](https://svange.github.io/augint-billing-lib/benchmark-report.html)** | 🔒 **[Security](https://svange.github.io/augint-billing-lib/security-reports.html)** | ⚖️ **[Compliance](https://svange.github.io/augint-billing-lib/license-compatibility.html)** |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|

## Overview

This library provides production-ready core business logic for:

- **Usage Tracking** - Track API usage per customer with high-performance caching
- **Tiered Pricing** - Calculate charges with flexible pricing models  
- **Stripe Integration** - Manage customers, invoices, and payments with full idempotency
- **Webhook Processing** - Process Stripe webhook events reliably
- **Event Publishing** - Publish billing events to AWS EventBridge for integration
- **Audit Logging** - Comprehensive audit trails for all billing operations
- **Report Generation** - Generate detailed usage and billing reports
- **Retry & Circuit Breaking** - Production-grade reliability patterns

## 🚀 Production Ready Features

### ⚡ High-Performance Caching Layer
- **In-memory cache** optimized for AWS Lambda environments
- **Decorator-based integration** with `@cached` and `@cache_invalidate`
- **Wildcard pattern invalidation** for efficient cache management
- **Thread-safe operations** with comprehensive metrics collection
- **94% test coverage** with production-grade error handling

### 🔒 Enterprise Security & Reliability
- **Retry mechanisms** with exponential backoff and circuit breakers
- **Idempotency keys** for all financial operations
- **Comprehensive audit logging** with PII redaction
- **Input validation** with Pydantic models
- **Error isolation** - cache failures don't impact core operations

### 📊 Observability & Monitoring
- **Built-in metrics collection** for cache performance and business operations
- **EventBridge integration** for real-time event publishing
- **Structured logging** with contextual information
- **Health check endpoints** and operational dashboards

## Quick Start

### Installation

```bash
pip install augint-billing-lib
```

### Basic Usage

```python
from augint_billing_lib import BillingService

# Initialize the service
service = BillingService(
    table_name="billing-data-prod",
    eventbridge_bus_name="billing-events"
)

# Track usage with automatic caching
service.track_usage(
    customer_id="customer_123",
    endpoint="/api/search",
    usage_count=1
)

# Get customer (cached for performance)
customer = service.get_customer("customer_123")

# Calculate charges with tiered pricing
charges = service.calculate_charges("customer_123", "2024-01")

# Create and send invoice via Stripe
invoice = service.create_invoice("customer_123", charges)
```

## Architecture

### Core Components

- **`BillingService`** - Main orchestrator for all billing operations
- **`UsageCollector`** - High-performance usage tracking with caching
- **`PricingCalculator`** - Flexible tiered pricing calculation engine
- **`StripeManager`** - Production Stripe integration with idempotency
- **`WebhookProcessor`** - Reliable webhook event processing
- **`ReportGenerator`** - Comprehensive reporting and analytics
- **`EventPublisher`** - EventBridge event publishing with retry logic
- **`CacheLayer`** - High-performance Lambda memory cache

### Data Storage

**Single DynamoDB Table Design** with optimized access patterns:
- **Customer Data**: `CUSTOMER#{id}` - Customer information and configuration
- **Usage Records**: `USAGE#{customer_id}#{date}` - API usage tracking
- **Billing Periods**: `BILLING#{customer_id}#{period}` - Monthly billing cycles
- **Pricing Tiers**: `PRICING#{plan_type}#{tier}` - Pricing configuration
- **Invoices**: `INVOICE#{id}` - Invoice records and status

## EventBridge Integration

The library publishes events for real-time monitoring and integration:

```python
# Events published automatically
{
    "source": "augint.billing",
    "detail-type": "billing.usage.tracked",
    "detail": {
        "customer_id": "customer_123",
        "endpoint": "/api/search",
        "usage_count": 1,
        "timestamp": "2024-01-15T10:30:00Z"
    }
}
```

**Event Types:**
- `billing.usage.tracked` - API usage recorded
- `billing.customer.created` - New customer onboarded
- `billing.invoice.created` - Invoice generated
- `billing.payment.processed` - Payment status updates
- `billing.webhook.processed` - Webhook events handled

Event publishing can be disabled via `BILLING_ENABLE_EVENT_PUBLISHING=false`.

## Development Setup

```bash
# Clone the repository
git clone https://github.com/svange/augint-billing-lib.git
cd augint-billing-lib

# Install dependencies
make install

# Run tests with coverage
make test

# Run specific test categories
make test-unit          # Unit tests only
make test-integration   # Integration tests only
make test-all          # All tests including slow ones

# Code quality checks
make lint               # Fix linting issues
make format            # Format code
make type-check        # Type checking with mypy
make security          # Security scanning

# Generate documentation
make docs              # Generate API documentation
```

## Testing Strategy

The library follows a **"Mock at the Boundaries, Not the Seams"** testing philosophy:

- **94% test coverage** across all modules
- **Real internal components** used in tests for authentic behavior
- **External services mocked** (AWS, Stripe) at API boundaries
- **State verification** over behavior verification
- **Comprehensive integration tests** with LocalStack and Stripe test mode

See [Testing Strategy Guide](documentation/testing-strategy.md) for detailed information.

## Configuration

### Environment Variables

```bash
# Required
DYNAMODB_TABLE=billing-data-prod
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Optional
AWS_REGION=us-east-1
EVENTBRIDGE_BUS=billing-events-prod
BILLING_ENABLE_EVENT_PUBLISHING=true
BILLING_ENABLE_AUDIT=true

# Cache Configuration
CACHE_TTL_SECONDS=300
CACHE_MAX_ITEMS=1000
```

### DynamoDB Setup

The library expects a single DynamoDB table with these key attributes:
- **Partition Key**: `pk` (String)
- **Sort Key**: `sk` (String)  
- **Global Secondary Index**: `gsi1pk` / `gsi1sk`

See [Architecture Guide](documentation/billing-spec.md) for detailed table design.

## Production Deployment

### 1. Infrastructure Requirements

- **DynamoDB Table** with on-demand or provisioned billing
- **EventBridge Custom Bus** for event publishing  
- **IAM Roles** with appropriate permissions
- **Secrets Manager** (recommended) for API keys

### 2. Performance Characteristics

- **Cache Hit Rate**: 85-95% typical for production workloads
- **Response Time**: <50ms for cached operations, <200ms for uncached
- **Throughput**: Handles 1000+ requests/second per Lambda instance
- **Memory Usage**: ~50MB baseline, ~100MB with full cache

### 3. Monitoring & Alerting

Monitor these key metrics in production:
- Cache hit rate and eviction rate
- DynamoDB read/write capacity utilization
- EventBridge publish success rate
- Stripe API error rates and latency

## Documentation

- **[Architecture Guide](documentation/billing-spec.md)** - System design and component architecture
- **[Troubleshooting Guide](documentation/TROUBLESHOOTING.md)** - Common issues and solutions
- **[Stripe Testing Guide](documentation/stripe-testing-guide.md)** - End-to-end Stripe integration testing
- **[Testing Strategy](documentation/testing-strategy.md)** - Testing philosophy and patterns
- **[API Documentation](https://svange.github.io/augint-billing-lib)** - Full API reference (generated)

## Contributing

### Branch Naming Conventions

Use descriptive branch names with these prefixes:

- **`feat/description`** - New features and enhancements
  - `feat/issue-43-caching-layer`
  - `feat/stripe-webhook-validation`

- **`fix/description`** - Bug fixes
  - `fix/issue-25-currency-formatting`
  - `fix/dynamo-connection-timeout`

- **`docs/description`** - Documentation updates
  - `docs/api-reference-update`
  - `docs/troubleshooting-guide`

- **`refactor/description`** - Code refactoring
  - `refactor/pricing-calculator-cleanup`
  - `refactor/extract-common-utilities`

- **`test/description`** - Test additions or improvements
  - `test/integration-coverage-improvement`
  - `test/unit-test-refactoring`

- **`chore/description`** - Maintenance tasks
  - `chore/update-dependencies`
  - `chore/ci-pipeline-optimization`

### Contribution Workflow

1. Fork the repository
2. Create a feature branch following naming conventions above
3. Make your changes with comprehensive tests
4. Ensure all tests pass (`make test-all`)
5. Run quality checks (`make lint type-check security`)
6. Commit using [conventional commits](https://conventionalcommits.org/) format
7. Push to your fork and create a Pull Request
8. Link related issues in your PR description using `Closes #123` or `Refs #123`

### Pull Request Guidelines

- Use the provided PR template
- Reference related issues with `Closes #123` (for issues resolved by the PR) or `Refs #123` (for related but not resolved issues)
- Ensure CI passes and address any feedback
- Maintain backward compatibility unless explicitly agreed otherwise

## License

This project is licensed under the [AGPL v3 License](LICENSE) - see the LICENSE file for details.

---

**Built for Production** • **Battle-tested** • **Fully Observable** • **Enterprise-ready**
