# Augint Billing Library

**Billing service library for API usage tracking, tiered pricing calculations, and Stripe integration.**

## Overview

This library provides the core business logic for:
- Tracking API usage per customer
- Calculating charges with tiered pricing models  
- Managing Stripe customers and payments
- Processing webhooks from Stripe
- Publishing billing events to AWS EventBridge
- Generating usage and billing reports

## EventBridge Integration

The library automatically publishes billing events to AWS EventBridge for real-time monitoring and integration:

- **Usage Tracking**: `billing.usage.tracked` events when API usage is recorded
- **Customer Creation**: `billing.customer.created` events for new customers  
- **Invoice Generation**: `billing.invoice.created` events when invoices are generated
- **Payment Processing**: `billing.payment.processed` events for payment status updates

Event publishing can be disabled via `BILLING_ENABLE_EVENT_PUBLISHING=false` environment variable.

[![CI Pipeline](https://github.com/svange/augint-billing-lib/actions/workflows/pipeline.yaml/badge.svg?branch=main)](https://github.com/svange/augint-billing-lib/actions/workflows/pipeline.yaml)
[![PyPI](https://img.shields.io/pypi/v/augint-billing-lib?style=flat-square)](https://pypi.org/project/augint-billing-lib/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/downloads/)

[![Poetry](https://img.shields.io/badge/dependency%20manager-poetry-blue?style=flat-square)](https://python-poetry.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)
[![Linting: Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json&style=flat-square)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?style=flat-square&logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Renovate](https://img.shields.io/badge/renovate-enabled-blue?style=flat-square&logo=renovatebot)](https://renovatebot.com)

[![pytest](https://img.shields.io/badge/testing-pytest-green?style=flat-square&logo=pytest)](https://pytest.org/)
[![GitHub Actions](https://img.shields.io/badge/CI-GitHub%20Actions-blue?style=flat-square&logo=github-actions)](https://github.com/features/actions)
[![Semantic Release](https://img.shields.io/badge/release-semantic--release-e10079?style=flat-square&logo=semantic-release)](https://github.com/semantic-release/semantic-release)
[![AWS SAM](https://img.shields.io/badge/Infrastructure-AWS%20SAM-orange?style=flat-square&logo=amazon-aws)](https://aws.amazon.com/serverless/sam/)
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL%20v3-blue.svg?style=flat-square)](https://www.gnu.org/licenses/agpl-3.0)


## 📊 Live Dashboards

| 📖 **[Documentation](https://svange.github.io/augint-billing-lib)** | 🧪 **[Unit Tests](https://svange.github.io/augint-billing-lib/unit-test-report.html)** | 🔬 **[Integration Tests](https://svange.github.io/augint-billing-lib/integration-test-report.html)** | 📊 **[Coverage](https://svange.github.io/augint-billing-lib/htmlcov/index.html)** | ⚡ **[Benchmarks](https://svange.github.io/augint-billing-lib/benchmark-report.html)** | 🔒 **[Security](https://svange.github.io/augint-billing-lib/security-reports.html)** | ⚖️ **[Compliance](https://svange.github.io/augint-billing-lib/license-compatibility.html)** |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|


## 🔑 Key Development Characteristics

| Characteristic | Details |
|:--------------|:--------|
| **Merge Strategy** | Configurable (see .env) |
| **Deployment Model** | Tag-based to PyPI |
| **Environments** | Local → PyPI |
| **Preview Environments** | N/A (library) |
| **Pipeline Features** | Semantic release, Auto-publish to PyPI |
| **Special Considerations** | 90% coverage requirement, Mutation testing |

---




## Project Structure

```
augint-billing-lib-library/
├── src/
│   └── augint_billing_lib/      # Core library code (to be implemented)
├── tests/                   # Test suite (to be implemented)
├── examples/                # Original template code for reference
├── pyproject.toml          # Project dependencies and configuration
├── Makefile                # Development commands
└── README.md               # This file
```

## Development Setup

```bash
# Install dependencies
make install

# Run tests
make test

# Check code quality
make lint
make type-check

# Generate documentation
make docs
```

## Implementation Status

The library is fully implemented with all core components. Current implementation includes:

### Library Exports (from planning spec)
- [x] BillingService - Main service class
- [x] UsageCollector - Track API usage
- [x] PricingCalculator - Apply tiered pricing
- [x] StripeManager - Stripe operations
- [x] WebhookProcessor - Process Stripe webhooks
- [x] ReportGenerator - Generate reports
- [x] EventPublisher - Publish billing events to EventBridge
- [x] Data models (Customer, UsageRecord, BillingPeriod, etc.)

### Key Features Removed (Minimal Version)
- ✅ Feature flags removed
- ✅ Telemetry/Sentry removed
- ✅ Mutation testing removed  
- ✅ Complex CLI structures removed

## Dependencies

Core dependencies:
- click - CLI framework
- boto3 - AWS SDK (to be added)
- stripe - Stripe SDK (to be added)
- pydantic - Data validation (to be added)

## Testing

The project uses pytest with pragmatic coverage targets:
- Library code: 70% coverage target
- Focus on core business logic
- Integration tests for AWS/Stripe interactions
