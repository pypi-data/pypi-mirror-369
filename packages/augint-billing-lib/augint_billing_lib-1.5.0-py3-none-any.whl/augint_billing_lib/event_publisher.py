"""EventBridge event publishing for billing operations.

This module provides the EventPublisher class for publishing billing-related
events to AWS EventBridge with retry logic and error handling. Events are
published asynchronously to avoid blocking billing operations.
"""

import json
import logging
from typing import Any, Optional

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from .config import get_settings
from .retry import ServiceRetryConfigs, retry_with_backoff

logger = logging.getLogger(__name__)


class EventPublisher:
    """Publisher for billing events to AWS EventBridge.

    This class handles publishing billing-related events to EventBridge with
    proper retry logic and error handling. Events are published with retry
    but failures don't block main operations.

    Attributes:
        enabled: Whether event publishing is enabled
        events_client: AWS EventBridge client
        bus_name: EventBridge bus name for publishing events
    """

    def __init__(
        self,
        enabled: Optional[bool] = None,
        events_client: Optional[Any] = None,
        bus_name: Optional[str] = None,
        region_name: Optional[str] = None,
    ) -> None:
        """Initialize EventPublisher.

        Args:
            enabled: Whether to enable event publishing (defaults to True)
            events_client: Optional EventBridge client for dependency injection
            bus_name: EventBridge bus name (defaults from config)
            region_name: AWS region (defaults from config)
        """
        settings = get_settings()

        # Event publishing is enabled by default but can be disabled
        self.enabled = enabled if enabled is not None else True

        # Use provided client or create new one
        if events_client is not None:
            self.events_client = events_client
        else:
            self.events_client = boto3.client(
                "events",
                region_name=region_name or settings.aws_region,
            )

        # Set bus name from parameter or config
        self.bus_name = bus_name or settings.eventbridge_bus

        logger.debug(
            "EventPublisher initialized: enabled=%s, bus_name=%s",
            self.enabled,
            self.bus_name,
        )

    @retry_with_backoff(**ServiceRetryConfigs.EVENTBRIDGE.to_dict())
    def publish_event(
        self,
        source: str,
        detail_type: str,
        detail: dict[str, Any],
        metadata: Optional[dict[str, Any]] = None,
    ) -> Optional[dict[str, Any]]:
        """Publish a single event to EventBridge.

        Args:
            source: Event source identifier (e.g., "billing.service")
            detail_type: Event detail type (e.g., "UsageTracked")
            detail: Event detail data as dictionary
            metadata: Optional metadata dict (can include resources, tags, etc.)

        Returns:
            EventBridge response on success, None if disabled or on failure

        Example:
            >>> publisher = EventPublisher()
            >>> result = publisher.publish_event(
            ...     source="billing.service",
            ...     detail_type="UsageTracked",
            ...     detail={"customer_id": "CUST123", "usage_count": 100},
            ...     metadata={"resources": ["arn:aws:dynamodb:us-east-1:123:table/billing"]}
            ... )
        """
        if not self.enabled:
            logger.debug("Event publishing disabled, skipping event: %s", detail_type)
            return None

        try:
            # Prepare event entry
            entry = {
                "Source": source,
                "DetailType": detail_type,
                "Detail": json.dumps(detail),
                "EventBusName": self.bus_name,
            }

            # Add metadata if provided
            if metadata:
                # Extract standard EventBridge fields from metadata
                if "resources" in metadata:
                    entry["Resources"] = metadata["resources"]
                if "trace_header" in metadata:
                    entry["TraceHeader"] = metadata["trace_header"]

            # Publish to EventBridge
            response: dict[str, Any] = self.events_client.put_events(Entries=[entry])

            # Check for failed entries
            if response.get("FailedEntryCount", 0) > 0:
                failed_entries = response.get("Entries", [])
                failed_details = [
                    entry
                    for entry in failed_entries
                    if "ErrorCode" in entry or "ErrorMessage" in entry
                ]
                logger.warning(
                    "Event publishing partially failed: %s failed entries: %s",
                    response["FailedEntryCount"],
                    failed_details,
                )
                return None

            logger.debug(
                "Successfully published event: source=%s, detail_type=%s",
                source,
                detail_type,
            )
            return response

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.warning(
                "Failed to publish event to EventBridge: %s - %s (source=%s, detail_type=%s)",
                error_code,
                str(e),
                source,
                detail_type,
            )
            return None
        except Exception as e:
            logger.warning(
                "Unexpected error publishing event: %s (source=%s, detail_type=%s)",
                str(e),
                source,
                detail_type,
            )
            return None

    def _prepare_batch_entries(self, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Prepare event entries for EventBridge batch publishing.

        Args:
            events: List of event dictionaries

        Returns:
            List of EventBridge-formatted entries
        """
        entries = []
        for event in events:
            entry = {
                "Source": event["source"],
                "DetailType": event["detail_type"],
                "Detail": json.dumps(event["detail"]),
                "EventBusName": self.bus_name,
            }

            # Add metadata if provided
            if event.get("metadata"):
                metadata = event["metadata"]
                if "resources" in metadata:
                    entry["Resources"] = metadata["resources"]
                if "trace_header" in metadata:
                    entry["TraceHeader"] = metadata["trace_header"]

            entries.append(entry)
        return entries

    def _process_batch_response(
        self,
        response: dict[str, Any],
        chunk: list[dict[str, Any]],
        events: list[dict[str, Any]],
        chunk_start_index: int,
    ) -> dict[str, Any]:
        """Process the response from EventBridge batch publish.

        Args:
            response: EventBridge response
            chunk: Current chunk of entries
            events: Original events list
            chunk_start_index: Starting index of current chunk

        Returns:
            Dictionary with chunk results
        """
        failed_count = response.get("FailedEntryCount", 0)
        successful_count = len(chunk) - failed_count

        chunk_results = {
            "successful_count": successful_count,
            "failed_count": failed_count,
            "failed_entries": [],
        }

        # Collect failed entry details
        if failed_count > 0:
            failed_entries = response.get("Entries", [])
            for j, entry_result in enumerate(failed_entries):
                if "ErrorCode" in entry_result or "ErrorMessage" in entry_result:
                    original_event_index = chunk_start_index + j
                    original_event = (
                        events[original_event_index] if original_event_index < len(events) else {}
                    )
                    chunk_results["failed_entries"].append(
                        {
                            "event": original_event,
                            "error_code": entry_result.get("ErrorCode"),
                            "error_message": entry_result.get("ErrorMessage"),
                        }
                    )

        return chunk_results

    @retry_with_backoff(**ServiceRetryConfigs.EVENTBRIDGE.to_dict())
    def publish_batch(
        self,
        events: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """Publish multiple events to EventBridge in a single batch.

        Args:
            events: List of event dictionaries, each containing:
                - source: Event source identifier
                - detail_type: Event detail type
                - detail: Event detail data as dictionary
                - metadata: Optional metadata dict (can include resources, etc.)

        Returns:
            Dictionary with batch results:
                - successful_count: Number of successfully published events
                - failed_count: Number of failed events
                - failed_entries: List of failed event details

        Example:
            >>> publisher = EventPublisher()
            >>> events = [
            ...     {
            ...         "source": "billing.service",
            ...         "detail_type": "UsageTracked",
            ...         "detail": {"customer_id": "CUST123"},
            ...         "metadata": {"resources": ["arn:aws:dynamodb:us-east-1:123:table/billing"]}
            ...     },
            ...     {
            ...         "source": "billing.service",
            ...         "detail_type": "InvoiceGenerated",
            ...         "detail": {"invoice_id": "INV123"},
            ...     }
            ... ]
            >>> results = publisher.publish_batch(events)
        """
        if not self.enabled:
            logger.debug("Event publishing disabled, skipping batch of %d events", len(events))
            return {
                "successful_count": 0,
                "failed_count": len(events),
                "failed_entries": [],
            }

        if not events:
            return {
                "successful_count": 0,
                "failed_count": 0,
                "failed_entries": [],
            }

        try:
            # Prepare batch entries
            entries = self._prepare_batch_entries(events)

            # Process in chunks (EventBridge limit: 10 entries per batch)
            all_results: dict[str, Any] = {
                "successful_count": 0,
                "failed_count": 0,
                "failed_entries": [],
            }

            chunk_size = 10
            for i in range(0, len(entries), chunk_size):
                chunk = entries[i : i + chunk_size]

                # Publish chunk to EventBridge
                response: dict[str, Any] = self.events_client.put_events(Entries=chunk)

                # Process chunk results
                chunk_results = self._process_batch_response(response, chunk, events, i)

                # Accumulate results
                all_results["successful_count"] += chunk_results["successful_count"]
                all_results["failed_count"] += chunk_results["failed_count"]
                all_results["failed_entries"].extend(chunk_results["failed_entries"])

            # Log results
            if all_results["failed_count"] > 0:
                logger.warning(
                    "Batch event publishing partially failed: %d successful, %d failed",
                    all_results["successful_count"],
                    all_results["failed_count"],
                )
            else:
                logger.debug(
                    "Successfully published batch: %d events",
                    all_results["successful_count"],
                )

            return all_results

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            logger.warning(
                "Failed to publish event batch to EventBridge: %s - %s",
                error_code,
                str(e),
            )
            return {
                "successful_count": 0,
                "failed_count": len(events),
                "failed_entries": [{"event": event, "error": str(e)} for event in events],
            }
        except Exception as e:
            logger.warning(
                "Unexpected error publishing event batch: %s",
                str(e),
            )
            return {
                "successful_count": 0,
                "failed_count": len(events),
                "failed_entries": [{"event": event, "error": str(e)} for event in events],
            }

    def publish_usage_tracked(
        self,
        customer_id: str,
        endpoint: str,
        usage_count: int,
        timestamp: Optional[str] = None,
    ) -> Optional[dict[str, Any]]:
        """Convenience method to publish usage tracking events.

        Args:
            customer_id: Customer identifier
            endpoint: API endpoint that was called
            usage_count: Number of API calls
            timestamp: Optional timestamp (defaults to current time)

        Returns:
            EventBridge response on success, None if disabled or on failure
        """
        detail = {
            "customer_id": customer_id,
            "endpoint": endpoint,
            "usage_count": usage_count,
        }

        if timestamp:
            detail["timestamp"] = timestamp

        return self.publish_event(
            source="billing.service",
            detail_type="UsageTracked",
            detail=detail,
        )

    def publish_invoice_generated(
        self,
        customer_id: str,
        invoice_id: str,
        amount: str,
        period: str,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        """Convenience method to publish invoice generation events.

        Args:
            customer_id: Customer identifier
            invoice_id: Generated invoice identifier
            amount: Invoice amount as string
            period: Billing period
            **kwargs: Additional invoice details

        Returns:
            EventBridge response on success, None if disabled or on failure
        """
        detail = {
            "customer_id": customer_id,
            "invoice_id": invoice_id,
            "amount": amount,
            "period": period,
        }
        detail.update(kwargs)

        return self.publish_event(
            source="billing.service",
            detail_type="InvoiceGenerated",
            detail=detail,
        )

    def publish_payment_processed(
        self,
        customer_id: str,
        payment_id: str,
        amount: str,
        status: str,
        **kwargs: Any,
    ) -> Optional[dict[str, Any]]:
        """Convenience method to publish payment processing events.

        Args:
            customer_id: Customer identifier
            payment_id: Payment identifier
            amount: Payment amount as string
            status: Payment status
            **kwargs: Additional payment details

        Returns:
            EventBridge response on success, None if disabled or on failure
        """
        detail = {
            "customer_id": customer_id,
            "payment_id": payment_id,
            "amount": amount,
            "status": status,
        }
        detail.update(kwargs)

        return self.publish_event(
            source="billing.service",
            detail_type="PaymentProcessed",
            detail=detail,
        )
