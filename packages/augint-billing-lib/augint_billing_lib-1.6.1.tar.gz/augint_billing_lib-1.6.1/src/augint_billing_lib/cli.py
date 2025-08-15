"""CLI interface for augint-billing-lib library.

Command-line interface for billing operations including usage tracking,
charge calculation, invoice generation, and billing management.
"""

import csv
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click

from .config import get_settings
from .db import DynamoDBClient
from .event_types import EventProcessingResult
from .exceptions import (
    CustomerNotFoundError,
    DynamoDBError,
    EventValidationError,
    InvoiceGenerationError,
    PricingConfigurationError,
    RateLimitError,
    SignatureVerificationError,
    StripeError,
    UsageValidationError,
)
from .models import Customer
from .pricing_calculator import PricingCalculator
from .report_generator import ReportGenerator
from .stripe_event_processor import StripeEventProcessor
from .stripe_manager import StripeManager
from .types import PeriodChargesDict
from .usage_collector import UsageCollector
from .utils import verify_stripe_signature


def validate_customer_id(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate customer ID format and length."""
    _ = ctx, param  # Unused but required by click callback signature
    if not value:
        raise click.BadParameter("Customer ID cannot be empty")
    max_customer_id_length = 100
    if len(value) > max_customer_id_length:
        raise click.BadParameter("Customer ID must be 100 characters or less")
    if not value.replace("-", "").replace("_", "").isalnum():
        raise click.BadParameter(
            "Customer ID must contain only alphanumeric characters, hyphens, and underscores"
        )
    return value


def validate_date(ctx: click.Context, param: click.Parameter, value: str | None) -> datetime | None:
    """Validate and parse date string."""
    _ = ctx, param  # Unused but required by click callback signature
    if not value:
        return None
    try:
        # Support multiple date formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"]:
            try:
                return datetime.strptime(value, fmt).replace(tzinfo=UTC)
            except ValueError:
                continue
        raise ValueError("Invalid date format")
    except ValueError as e:
        raise click.BadParameter("Date must be in format YYYY-MM-DD or ISO 8601 format") from e


def validate_api_endpoint(ctx: click.Context, param: click.Parameter, value: str) -> str:
    """Validate API endpoint format."""
    _ = ctx, param  # Unused but required by click callback signature
    if not value:
        raise click.BadParameter("API endpoint cannot be empty")
    max_endpoint_length = 255
    if len(value) > max_endpoint_length:
        raise click.BadParameter(f"API endpoint must be {max_endpoint_length} characters or less")
    if not value.startswith("/"):
        value = f"/{value}"
    return value


def validate_positive_int(ctx: click.Context, param: click.Parameter, value: int) -> int:
    """Validate positive integer values."""
    _ = ctx  # Unused but required by click callback signature
    if value <= 0:
        raise click.BadParameter(f"{param.name} must be a positive integer")
    return value


@click.group()
@click.option("--config-file", type=click.Path(exists=True), help="Path to configuration file")
@click.option("--table-name", help="DynamoDB table name (overrides environment)")
@click.option("--region", help="AWS region (overrides environment)")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.pass_context
def cli(
    ctx: click.Context,
    config_file: str | None,
    table_name: str | None,
    region: str | None,
    verbose: bool,
) -> None:
    """Augint Billing CLI - Manage billing operations and usage tracking.

    The CLI publishes billing events to EventBridge when enabled. Configure event
    publishing with environment variables:

    - TEST_EVENTBRIDGE_BUS: EventBridge bus name (default: billing-events)
    - BILLING_ENABLE_EVENT_PUBLISHING: Enable/disable events (default: true)
    - BILLING_EVENT_PUBLISHING_TIMEOUT: Event publish timeout (default: 5.0)
    """
    ctx.ensure_object(dict)

    # Load settings
    settings = get_settings()

    # Override with CLI options
    if table_name:
        settings.dynamodb_table = table_name
    if region:
        settings.aws_region = region

    # Store in context
    ctx.obj["settings"] = settings
    ctx.obj["verbose"] = verbose

    if verbose:
        click.echo(f"Using DynamoDB table: {settings.dynamodb_table}")
        click.echo(f"AWS Region: {settings.aws_region}")
        click.echo(f"Environment: {settings.environment}")


@cli.command("track-usage")
@click.option("--customer-id", required=True, callback=validate_customer_id, help="Customer ID")
@click.option(
    "--api-endpoint", required=True, callback=validate_api_endpoint, help="API endpoint called"
)
@click.option(
    "--usage-count",
    default=1,
    callback=validate_positive_int,
    help="Number of API calls (default: 1)",
)
@click.option("--timestamp", callback=validate_date, help="When usage occurred (default: now)")
@click.option("--skip-validation", is_flag=True, help="Skip usage validation")
@click.option("--skip-rate-limit", is_flag=True, help="Skip rate limit checking")
@click.pass_context
def track_usage(
    ctx: click.Context,
    customer_id: str,
    api_endpoint: str,
    usage_count: int,
    timestamp: datetime | None,
    skip_validation: bool,
    skip_rate_limit: bool,
) -> None:
    """Track API usage for a customer.

    This command tracks API usage and publishes a 'billing.usage.tracked' event
    to EventBridge if event publishing is enabled.
    """
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    try:
        collector = UsageCollector(table_name=settings.dynamodb_table)

        if verbose:
            click.echo(f"Tracking {usage_count} calls to {api_endpoint} for customer {customer_id}")

        usage_record = collector.track_usage(
            customer_id=customer_id,
            api_endpoint=api_endpoint,
            usage_count=usage_count,
            timestamp=timestamp,
            validate=not skip_validation,
            check_rate_limit=not skip_rate_limit,
        )

        click.secho("✓ Successfully tracked usage", fg="green")

        if verbose:
            click.echo(f"  Record ID: {usage_record.sk}")
            click.echo(f"  Timestamp: {usage_record.timestamp.isoformat()}")
            click.echo(f"  Total usage: {usage_record.usage_count}")

    except CustomerNotFoundError as e:
        click.secho(
            f"✗ Customer not found: {e.details.get('customer_id', 'unknown')}", fg="red", err=True
        )
        ctx.exit(1)
    except RateLimitError as e:
        click.secho(f"✗ Rate limit exceeded: {e.message}", fg="red", err=True)
        if verbose:
            click.echo(f"  Current: {e.current_usage}/{e.limit}", err=True)
            click.echo(f"  Reset at: {e.reset_time}", err=True)
        ctx.exit(1)
    except UsageValidationError as e:
        click.secho(f"✗ Validation error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except DynamoDBError as e:
        click.secho(f"✗ Database error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.command("calculate-charges")
@click.option("--customer-id", required=True, callback=validate_customer_id, help="Customer ID")
@click.option("--year", type=int, help="Billing year (default: current)")
@click.option("--month", type=int, help="Billing month (default: current)")
@click.option("--usage-count", type=int, help="Override usage count (for estimation)")
@click.option("--save", is_flag=True, help="Save billing period to database")
@click.option(
    "--output-format", type=click.Choice(["json", "text"]), default="text", help="Output format"
)
@click.pass_context
def calculate_charges(
    ctx: click.Context,
    customer_id: str,
    year: int | None,
    month: int | None,
    usage_count: int | None,
    save: bool,
    output_format: str,
) -> None:
    """Calculate charges for a customer's usage."""
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    # Default to current month if not specified
    now = datetime.now(UTC)
    year = year or now.year
    month = month or now.month

    # Validate year and month
    min_year, max_year = 2020, 2100
    if not (min_year <= year <= max_year):
        click.secho(
            f"✗ Invalid year (must be between {min_year} and {max_year})", fg="red", err=True
        )
        ctx.exit(1)
    min_month, max_month = 1, 12
    if not (min_month <= month <= max_month):
        click.secho("✗ Invalid month (must be between 1 and 12)", fg="red", err=True)
        ctx.exit(1)

    try:
        result: dict[str, Any] | PeriodChargesDict
        calculator = PricingCalculator(table_name=settings.dynamodb_table)

        if usage_count is not None:
            # Direct calculation with provided usage
            result = calculator.calculate_customer_charges(
                customer_id=customer_id,
                usage_count=usage_count,
                period=f"{year:04d}-{month:02d}" if save else None,
                save_to_db=save,
            )
        else:
            # Calculate for full billing period
            result = calculator.calculate_period_charges(
                customer_id=customer_id,
                year=year,
                month=month,
            )

        if output_format == "json":
            click.echo(json.dumps(result, indent=2, default=str))
        else:
            click.secho(f"✓ Charges calculated for {customer_id}", fg="green")
            click.echo(f"  Period: {year:04d}-{month:02d}")
            click.echo(f"  Plan Type: {result['plan_type']}")
            click.echo(f"  Usage Count: {result['usage_count']:,}")
            click.echo(f"  Total Charges: {result['currency']} {result['total_charges']:.2f}")

            if verbose and "breakdown" in result:
                click.echo("\n  Pricing Breakdown:")
                for tier in result["breakdown"]:
                    click.echo(
                        f"    Tier {tier['tier']}: {tier['usage']} units @ {tier['rate']} = {tier['charges']:.2f}"
                    )

    except CustomerNotFoundError as e:
        click.secho(
            f"✗ Customer not found: {e.details.get('customer_id', 'unknown')}", fg="red", err=True
        )
        ctx.exit(1)
    except PricingConfigurationError as e:
        click.secho(f"✗ Pricing configuration error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.command("generate-invoice")
@click.option("--customer-id", required=True, callback=validate_customer_id, help="Customer ID")
@click.option("--year", type=int, required=True, help="Billing year")
@click.option("--month", type=int, required=True, help="Billing month")
@click.option("--due-days", type=int, default=30, help="Days until payment due (default: 30)")
@click.option("--send", is_flag=True, help="Send invoice to customer via Stripe")
@click.option(
    "--output-format", type=click.Choice(["json", "text"]), default="text", help="Output format"
)
@click.pass_context
def generate_invoice(  # noqa: PLR0915
    ctx: click.Context,
    customer_id: str,
    year: int,
    month: int,
    due_days: int,
    send: bool,
    output_format: str,
) -> None:
    """Generate an invoice for a customer's billing period.

    This command generates an invoice and publishes a 'billing.invoice.created' event
    to EventBridge if event publishing is enabled.
    """
    settings = ctx.obj["settings"]
    ctx.obj["verbose"]

    # Validate year and month
    min_year, max_year = 2020, 2100
    if not (min_year <= year <= max_year):
        click.secho(
            f"✗ Invalid year (must be between {min_year} and {max_year})", fg="red", err=True
        )
        ctx.exit(1)
    min_month, max_month = 1, 12
    if not (min_month <= month <= max_month):
        click.secho("✗ Invalid month (must be between 1 and 12)", fg="red", err=True)
        ctx.exit(1)

    try:
        # Get billing period data
        db_client = DynamoDBClient(table_name=settings.dynamodb_table)
        billing_period = db_client.get_billing_period(customer_id, year, month)

        if not billing_period:
            click.secho(f"✗ No billing period found for {year:04d}-{month:02d}", fg="red", err=True)
            click.echo("  Run 'calculate-charges' first to create billing period", err=True)
            ctx.exit(1)

        # Get customer data
        customer = db_client.get_customer(customer_id)
        if not customer:
            click.secho(f"✗ Customer not found: {customer_id}", fg="red", err=True)
            ctx.exit(1)

        # Check for Stripe customer ID
        stripe_customer_id = customer.get("stripe_customer_id")
        if not stripe_customer_id:
            click.secho(f"✗ Customer {customer_id} has no Stripe customer ID", fg="red", err=True)
            click.echo("  Customer must be synced with Stripe first", err=True)
            ctx.exit(1)

        # Generate invoice via Stripe
        stripe_manager = StripeManager()

        invoice_data = stripe_manager.create_invoice(
            customer_id=stripe_customer_id,  # Pass Stripe customer ID as customer_id
            amount=float(billing_period.get("charges_calculated", 0)),
            description=f"Usage charges for {year:04d}-{month:02d}",
            metadata={
                "customer_id": customer_id,
                "billing_period": f"{year:04d}-{month:02d}",
                "usage_total": str(billing_period.get("usage_total", 0)),
            },
            days_until_due=due_days,
            auto_advance=send,  # Auto-finalize and send if requested
        )

        # Update billing period with invoice ID
        db_client.update_billing_period_invoice(
            customer_id=customer_id,
            year=year,
            month=month,
            invoice_id=invoice_data["id"],
        )

        if output_format == "json":
            click.echo(json.dumps(invoice_data, indent=2, default=str))
        else:
            click.secho("✓ Invoice generated successfully", fg="green")
            click.echo(f"  Invoice ID: {invoice_data['id']}")
            click.echo(f"  Customer: {customer.get('name')} ({customer.get('email')})")
            click.echo(f"  Period: {year:04d}-{month:02d}")
            click.echo(
                f"  Amount: {settings.default_currency} {invoice_data['amount_due'] / 100:.2f}"
            )
            click.echo(f"  Status: {invoice_data['status']}")

            if send:
                click.echo(f"  Invoice URL: {invoice_data.get('hosted_invoice_url', 'N/A')}")
            else:
                click.echo("  Note: Invoice created as draft. Use --send to finalize and send.")

    except StripeError as e:
        click.secho(f"✗ Stripe error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except InvoiceGenerationError as e:
        click.secho(f"✗ Invoice generation error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.command("get-usage")
@click.option(
    "--customer-id",
    callback=validate_customer_id,
    help="Customer ID (optional, all if not specified)",
)
@click.option("--start-date", callback=validate_date, help="Start date (default: 30 days ago)")
@click.option("--end-date", callback=validate_date, help="End date (default: now)")
@click.option(
    "--group-by", type=click.Choice(["day", "week", "month"]), default="day", help="Grouping period"
)
@click.option(
    "--output-format",
    type=click.Choice(["json", "text", "csv"]),
    default="text",
    help="Output format",
)
@click.option("--limit", type=int, help="Maximum records to return")
@click.pass_context
def get_usage(  # noqa: PLR0912
    ctx: click.Context,
    customer_id: str | None,
    start_date: datetime | None,
    end_date: datetime | None,
    group_by: str,
    output_format: str,
    limit: int | None,
) -> None:
    """Get usage data for a customer or all customers."""
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    try:
        report_generator = ReportGenerator(table_name=settings.dynamodb_table)

        # Generate usage report
        report = report_generator.generate_usage_report(
            customer_id=customer_id,
            start_date=start_date,
            end_date=end_date,
            group_by=group_by,
        )

        if output_format == "json":
            click.echo(json.dumps(report, indent=2, default=str))
        elif output_format == "csv":
            # Output as CSV
            writer = csv.writer(sys.stdout)

            # Header
            if group_by == "day":
                writer.writerow(["Date", "Customer ID", "Total Usage", "Unique Endpoints"])
            else:
                writer.writerow(["Period", "Customer ID", "Total Usage", "Unique Endpoints"])

            # Data rows
            for period_data in report["aggregated_data"]:
                for customer_data in period_data.get("customers", [period_data]):
                    writer.writerow(
                        [
                            period_data["period"],
                            customer_data.get("customer_id", customer_id or "ALL"),
                            customer_data["total_usage"],
                            customer_data["unique_endpoints"],
                        ]
                    )
        else:
            # Text output
            click.secho("✓ Usage Report", fg="green")
            click.echo(
                f"  Period: {report['period']['start'][:10]} to {report['period']['end'][:10]}"
            )
            click.echo(f"  Total Usage: {report['total_usage']:,}")
            click.echo(f"  Unique Endpoints: {report['unique_endpoints']}")

            if customer_id:
                click.echo(f"  Customer: {customer_id}")
            else:
                click.echo(f"  Unique Customers: {report.get('unique_customers', 'N/A')}")

            if verbose and "aggregated_data" in report:
                click.echo(f"\n  {group_by.capitalize()}ly Breakdown:")
                for period_data in (
                    report["aggregated_data"][:limit] if limit else report["aggregated_data"]
                ):
                    click.echo(f"    {period_data['period']}: {period_data['total_usage']:,} calls")

    except CustomerNotFoundError as e:
        click.secho(
            f"✗ Customer not found: {e.details.get('customer_id', 'unknown')}", fg="red", err=True
        )
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.command("get-status")
@click.option("--customer-id", required=True, callback=validate_customer_id, help="Customer ID")
@click.option("--include-usage", is_flag=True, help="Include recent usage statistics")
@click.option("--include-billing", is_flag=True, help="Include billing periods")
@click.option(
    "--output-format", type=click.Choice(["json", "text"]), default="text", help="Output format"
)
@click.pass_context
def get_status(
    ctx: click.Context,
    customer_id: str,
    include_usage: bool,
    include_billing: bool,
    output_format: str,
) -> None:
    """Get billing status for a customer."""
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    try:
        db_client = DynamoDBClient(table_name=settings.dynamodb_table)

        # Get customer data
        customer = db_client.get_customer(customer_id)
        if not customer:
            click.secho(f"✗ Customer not found: {customer_id}", fg="red", err=True)
            ctx.exit(1)

        status_data: dict[str, Any] = {
            "customer": {
                "customer_id": customer.get("customer_id"),
                "name": customer.get("name"),
                "email": customer.get("email"),
                "plan_type": customer.get("plan_type"),
                "billing_status": customer.get("billing_status"),
                "stripe_customer_id": customer.get("stripe_customer_id"),
                "created_at": customer.get("created_at"),
            }
        }

        # Include usage statistics if requested
        if include_usage:
            collector = UsageCollector(table_name=settings.dynamodb_table)
            now = datetime.now(UTC)

            # Get current month usage
            current_month_usage = collector.get_usage_by_period(
                customer_id=customer_id,
                year=now.year,
                month=now.month,
            )

            status_data["current_month_usage"] = {
                "period": current_month_usage["period"],
                "total_usage": current_month_usage["total_usage"],
                "endpoint_breakdown": current_month_usage["endpoint_breakdown"],
            }

        # Include billing periods if requested
        if include_billing:
            # Get recent billing periods
            billing_periods = db_client.get_customer_billing_periods(customer_id, limit=6)

            status_data["billing_periods"] = [
                {
                    "period": bp.get("sk", "").replace("PERIOD#", ""),
                    "usage_total": bp.get("usage_total"),
                    "charges_calculated": float(bp.get("charges_calculated", 0)),
                    "payment_status": bp.get("payment_status"),
                    "invoice_id": bp.get("invoice_id"),
                }
                for bp in billing_periods
            ]

        if output_format == "json":
            click.echo(json.dumps(status_data, indent=2, default=str))
        else:
            click.secho(f"✓ Billing Status for {customer_id}", fg="green")
            click.echo("\n  Customer Information:")
            click.echo(f"    Name: {status_data['customer']['name']}")
            click.echo(f"    Email: {status_data['customer']['email']}")
            click.echo(f"    Plan: {status_data['customer']['plan_type']}")
            click.echo(f"    Status: {status_data['customer']['billing_status']}")

            if status_data["customer"].get("stripe_customer_id"):
                click.echo(f"    Stripe ID: {status_data['customer']['stripe_customer_id']}")

            if include_usage and "current_month_usage" in status_data:
                usage = status_data["current_month_usage"]
                click.echo(f"\n  Current Month Usage ({usage['period']}):")
                click.echo(f"    Total: {usage['total_usage']:,} calls")

                if verbose and usage.get("endpoint_breakdown"):
                    click.echo("    Endpoints:")
                    breakdown = usage["endpoint_breakdown"] or {}
                    for endpoint, count in breakdown.items():
                        click.echo(f"      {endpoint}: {count:,}")

            if include_billing and "billing_periods" in status_data:
                click.echo("\n  Recent Billing Periods:")
                for period in status_data["billing_periods"]:
                    payment_status = str(period.get("payment_status", "unknown"))
                    period_name = str(period.get("period", "unknown"))
                    status_icon = "✓" if payment_status == "paid" else "○"
                    click.echo(
                        f"    {status_icon} {period_name}: {settings.default_currency} {period['charges_calculated']:.2f} ({payment_status})"
                    )

    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.command("update-pricing")
@click.option(
    "--plan-type",
    required=True,
    type=click.Choice(["free", "paid", "enterprise"]),
    help="Plan type to update",
)
@click.option(
    "--tiers-file", type=click.Path(exists=True), help="JSON file with tier configurations"
)
@click.option("--tier", multiple=True, help="Tier definition (format: limit:price_per_unit)")
@click.option(
    "--effective-date", callback=validate_date, help="When pricing becomes effective (default: now)"
)
@click.option("--dry-run", is_flag=True, help="Preview changes without applying")
@click.pass_context
def update_pricing(  # noqa: PLR0912, PLR0915
    ctx: click.Context,
    plan_type: str,
    tiers_file: str | None,
    tier: tuple[str, ...],
    effective_date: datetime | None,
    dry_run: bool,
) -> None:
    """Update pricing tiers for a plan type (admin function)."""
    settings = ctx.obj["settings"]
    ctx.obj["verbose"]

    # Check for production environment warning
    if (
        settings.is_production()
        and not dry_run
        and not click.confirm("⚠️  WARNING: You are updating pricing in PRODUCTION. Continue?")
    ):
        click.echo("Aborted.")
        return

    try:
        # Load tiers from file or command line
        if tiers_file:
            with Path(tiers_file).open() as f:
                tiers_data = json.load(f)
        elif tier:
            # Parse tier definitions from command line
            tiers_data = []
            for tier_def in tier:
                parts = tier_def.split(":")
                expected_tier_parts = 2
                if len(parts) != expected_tier_parts:
                    click.secho(f"✗ Invalid tier format: {tier_def}", fg="red", err=True)
                    click.echo("  Expected format: limit:price_per_unit", err=True)
                    ctx.exit(1)

                limit_str, price_str = parts
                try:
                    usage_limit = None if limit_str.lower() == "unlimited" else int(limit_str)
                    price_per_unit = float(price_str)
                except ValueError:
                    click.secho(f"✗ Invalid tier values: {tier_def}", fg="red", err=True)
                    ctx.exit(1)

                tiers_data.append(
                    {
                        "usage_limit": usage_limit,
                        "price_per_unit": price_per_unit,
                    }
                )
        else:
            click.secho("✗ Must provide either --tiers-file or --tier options", fg="red", err=True)
            ctx.exit(1)

        # Validate tiers
        if not tiers_data:
            click.secho("✗ At least one pricing tier is required", fg="red", err=True)
            ctx.exit(1)

        # Display preview
        click.echo(f"Pricing Update Preview for {plan_type.upper()} plan:")
        click.echo("  New Tiers:")
        for i, tier_config in enumerate(tiers_data, 1):
            limit = tier_config.get("usage_limit")
            limit_str = "Unlimited" if limit is None else f"{limit:,}"
            price = tier_config["price_per_unit"]
            click.echo(
                f"    Tier {i}: Up to {limit_str} units @ {settings.default_currency} {price:.4f}/unit"
            )

        if effective_date:
            click.echo(f"  Effective Date: {effective_date.isoformat()}")
        else:
            click.echo("  Effective Date: Immediately")

        if dry_run:
            click.echo("\n  DRY RUN - No changes applied")
            return

        # Apply pricing updates
        if not click.confirm("\nApply these pricing changes?"):
            click.echo("Aborted.")
            return

        calculator = PricingCalculator(table_name=settings.dynamodb_table)

        success = calculator.update_pricing_tiers(
            plan_type=plan_type,
            tiers=tiers_data,
            effective_date=effective_date,
        )

        if success:
            click.secho(f"✓ Successfully updated pricing for {plan_type} plan", fg="green")
        else:
            click.secho("✗ Failed to update pricing", fg="red", err=True)
            ctx.exit(1)

    except PricingConfigurationError as e:
        click.secho(f"✗ Pricing configuration error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


def _load_and_validate_event(
    payload_file: str, ctx: click.Context
) -> tuple[bytes, dict[str, Any], str, str]:
    """Load and validate event data from file."""
    with Path(payload_file).open("rb") as f:
        payload = f.read()

    try:
        event_data = json.loads(payload)
    except json.JSONDecodeError:
        click.secho("✗ Invalid JSON in payload file", fg="red", err=True)
        ctx.exit(1)

    event_type = event_data.get("type", "unknown")
    event_id = event_data.get("id", "unknown")
    return payload, event_data, event_type, event_id


def _handle_dry_run(event_type: str, settings: Any) -> None:
    """Handle dry run mode for webhook processing."""
    click.echo("\n  DRY RUN - Not processing")
    db_client = DynamoDBClient(table_name=settings.dynamodb_table)
    processor = StripeEventProcessor(
        db_client=db_client, signature_secret=settings.stripe_webhook_secret
    )
    if event_type in processor.event_handlers:
        click.echo(f"  Handler: {processor.event_handlers[event_type].__name__}")
        click.echo("  Would update billing records based on event data")
    else:
        click.echo(f"  No handler for event type: {event_type}")


def _display_result(result: EventProcessingResult, verbose: bool) -> None:
    """Display processing result."""
    status = result.get("status")
    if status == "success":
        click.secho("✓ Successfully processed webhook", fg="green")
        if verbose:
            click.echo(f"  Event Type: {result.get('event_type', 'N/A')}")
            click.echo(f"  Event ID: {result.get('event_id', 'N/A')}")
            if result.get("result"):
                click.echo(f"  Result: {json.dumps(result['result'], indent=2)}")
    elif status == "ignored":
        click.secho("○ Webhook acknowledged but not processed", fg="yellow")
        click.echo(f"  Reason: {result.get('message', 'No handler for event type')}")
    else:
        click.secho("✗ Error processing webhook", fg="red")
        click.echo(f"  Error: {result.get('error', 'Unknown error')}")


@cli.command("process-webhook")
@click.option(
    "--payload-file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file with webhook payload",
)
@click.option("--signature", help="Stripe signature header (for validation)")
@click.option("--skip-validation", is_flag=True, help="Skip signature validation")
@click.option("--dry-run", is_flag=True, help="Process without updating database")
@click.pass_context
def process_webhook(
    ctx: click.Context,
    payload_file: str,
    signature: str | None,
    skip_validation: bool,
    dry_run: bool,
) -> None:
    """Process a webhook event (for testing)."""
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    try:
        # Load and validate event
        payload, event_data, event_type, event_id = _load_and_validate_event(payload_file, ctx)

        click.echo("Processing webhook event:")
        click.echo(f"  Type: {event_type}")
        click.echo(f"  ID: {event_id}")

        if dry_run:
            _handle_dry_run(event_type, settings)
            return

        # Process webhook
        db_client = DynamoDBClient(table_name=settings.dynamodb_table)
        processor = StripeEventProcessor(
            db_client=db_client, signature_secret=settings.stripe_webhook_secret
        )

        # Validate signature if needed
        if not skip_validation and signature:
            validated_event: dict[str, Any] = verify_stripe_signature(
                payload=payload,
                signature=signature,
                signature_secret=settings.stripe_webhook_secret or "",
            )  # type: ignore[assignment]
            # Use validated event data
            event_type = validated_event.get("type", event_type)
            event_id = validated_event.get("id", event_id)
            event_data = validated_event

        # Process the event
        result = processor.process_stripe_event(
            event_type=event_type,
            event_data=event_data.get("data", {}).get("object", {}),
            event_id=event_id,
        )

        _display_result(result, verbose)

    except (SignatureVerificationError, EventValidationError) as e:
        click.secho(f"✗ Event validation error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.command("process-stripe-event")
@click.option(
    "--event-file",
    type=click.Path(exists=True),
    required=True,
    help="JSON file with Stripe event data",
)
@click.option(
    "--event-type", required=True, help="Stripe event type (e.g., invoice.payment_succeeded)"
)
@click.option("--event-id", help="Optional event ID for tracking")
@click.option("--dry-run", is_flag=True, help="Process without updating database")
@click.pass_context
def process_stripe_event(
    ctx: click.Context,
    event_file: str,
    event_type: str,
    event_id: str | None,
    dry_run: bool,
) -> None:
    """Process a Stripe event directly (infrastructure-agnostic).

    This command processes Stripe events without webhook signature validation,
    making it useful for testing events from EventBridge, queues, or other sources.
    """
    settings = ctx.obj["settings"]
    verbose = ctx.obj["verbose"]

    try:
        # Load event data
        with Path(event_file).open("r") as f:
            event_data = json.load(f)

        if dry_run:
            click.secho("DRY RUN: Would process event", fg="yellow")
            click.echo(f"  Event Type: {event_type}")
            click.echo(f"  Event ID: {event_id or 'auto-generated'}")
            if verbose:
                click.echo(f"  Event Data: {json.dumps(event_data, indent=2)}")
            return

        # Process event
        db_client = DynamoDBClient(table_name=settings.dynamodb_table)
        processor = StripeEventProcessor(db_client=db_client)

        result = processor.process_stripe_event(
            event_type=event_type, event_data=event_data, event_id=event_id
        )

        if result.get("status") == "success":
            click.secho("✓ Successfully processed Stripe event", fg="green")
            if verbose:
                click.echo(f"  Event Type: {event_type}")
                click.echo(f"  Event ID: {result.get('event_id', 'N/A')}")
                click.echo(f"  Result: {result.get('result', {})}")
        elif result.get("status") == "ignored":
            click.secho("○ Event acknowledged but not processed", fg="yellow")
            click.echo(f"  Reason: {result.get('message', 'No handler for event type')}")
        else:
            click.secho("✗ Event processing failed", fg="red")
            click.echo(f"  Error: {result.get('error', 'Unknown error')}")
            ctx.exit(1)

    except FileNotFoundError:
        click.secho(f"✗ File not found: {event_file}", fg="red", err=True)
        ctx.exit(1)
    except json.JSONDecodeError as e:
        click.secho(f"✗ Invalid JSON in event file: {e}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@cli.group("admin")
@click.pass_context
def admin(ctx: click.Context) -> None:
    """Administrative commands for billing management."""


@admin.command("create-customer")
@click.option("--customer-id", required=True, callback=validate_customer_id, help="Customer ID")
@click.option("--email", required=True, help="Customer email")
@click.option("--name", required=True, help="Customer name")
@click.option(
    "--plan-type",
    type=click.Choice(["free", "paid", "enterprise"]),
    default="free",
    help="Plan type",
)
@click.option("--create-stripe", is_flag=True, help="Also create Stripe customer")
@click.pass_context
def create_customer(
    ctx: click.Context,
    customer_id: str,
    email: str,
    name: str,
    plan_type: str,
    create_stripe: bool,
) -> None:
    """Create a new customer record.

    This command creates a new customer and publishes a 'billing.customer.created' event
    to EventBridge if event publishing is enabled.
    """
    settings = ctx.obj["settings"]

    try:
        db_client = DynamoDBClient(table_name=settings.dynamodb_table)

        # Check if customer already exists
        existing = db_client.get_customer(customer_id)
        if existing:
            click.secho(f"✗ Customer {customer_id} already exists", fg="red", err=True)
            ctx.exit(1)

        # Create Stripe customer if requested
        stripe_customer_id = None
        if create_stripe:
            stripe_manager = StripeManager()
            stripe_customer_data = stripe_manager.create_customer(
                email=email,
                name=name,
                customer_id=customer_id,
            )
            stripe_customer_id = stripe_customer_data["id"]
            click.echo(f"  Created Stripe customer: {stripe_customer_id}")

        # Create customer record
        customer = Customer(
            pk=f"CUSTOMER#{customer_id}",
            customer_id=customer_id,
            email=email,
            name=name,
            plan_type=plan_type,
            stripe_customer_id=stripe_customer_id,
        )

        db_client.put_item(customer.model_dump())

        click.secho(f"✓ Successfully created customer {customer_id}", fg="green")
        click.echo(f"  Name: {name}")
        click.echo(f"  Email: {email}")
        click.echo(f"  Plan: {plan_type}")

    except StripeError as e:
        click.secho(f"✗ Stripe error: {e.message}", fg="red", err=True)
        ctx.exit(1)
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


@admin.command("list-customers")
@click.option(
    "--plan-type", type=click.Choice(["free", "paid", "enterprise"]), help="Filter by plan type"
)
@click.option("--limit", type=int, default=20, help="Maximum customers to list")
@click.option(
    "--output-format", type=click.Choice(["json", "text"]), default="text", help="Output format"
)
@click.pass_context
def list_customers(
    ctx: click.Context,
    plan_type: str | None,
    limit: int,
    output_format: str,
) -> None:
    """List all customers."""
    settings = ctx.obj["settings"]

    try:
        db_client = DynamoDBClient(table_name=settings.dynamodb_table)

        # Get all customers (simplified - in production would use pagination)
        customers = db_client.list_customers(limit=limit)

        # Filter by plan type if specified
        if plan_type:
            customers = [c for c in customers if c.get("plan_type") == plan_type]

        if output_format == "json":
            click.echo(json.dumps(customers, indent=2, default=str))
        else:
            if not customers:
                click.echo("No customers found")
                return

            click.echo(f"Customers ({len(customers)} found):")
            click.echo("-" * 80)

            for customer in customers:
                status_icon = "✓" if customer.get("billing_status") == "active" else "○"
                stripe_icon = "💳" if customer.get("stripe_customer_id") else "  "
                click.echo(
                    f"{status_icon} {customer['customer_id']:20} "
                    f"{customer.get('name', 'N/A'):25} "
                    f"{customer.get('plan_type', 'N/A'):10} "
                    f"{stripe_icon}"
                )

    except Exception as e:
        click.secho(f"✗ Unexpected error: {e!s}", fg="red", err=True)
        ctx.exit(1)


if __name__ == "__main__":
    cli()
