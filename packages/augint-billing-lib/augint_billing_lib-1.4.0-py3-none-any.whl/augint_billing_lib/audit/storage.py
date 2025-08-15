"""Audit storage with production-grade reliability.

This module provides DynamoDB storage for audit events with retry logic,
circuit breaker protection, and proper error handling.
"""

import gzip
import json
import logging
from typing import Any, Optional, Protocol

import boto3  # type: ignore[import-untyped]
from botocore.exceptions import ClientError  # type: ignore[import-untyped]

from ..config import get_settings
from ..exceptions import DynamoDBError
from ..retry import ServiceRetryConfigs, get_circuit_breaker, retry_with_backoff
from .events import AuditEvent, AuditEventDict

logger = logging.getLogger(__name__)


class AuditStorage(Protocol):
    """Protocol for audit storage backends."""

    is_critical: bool

    def store(self, event: AuditEvent) -> None:
        """Store a single audit event."""
        ...

    def store_batch(self, events: list[AuditEvent]) -> None:
        """Store multiple audit events."""
        ...

    def query_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: Optional[int] = None,
    ) -> list[AuditEvent]:
        """Query events by entity."""
        ...


class DynamoDBAuditStorage:
    """DynamoDB storage with production-grade reliability.

    Features:
    - Retry logic with exponential backoff
    - Circuit breaker protection
    - Compression for large events
    - Proper error handling
    - Graceful degradation
    """

    def __init__(
        self,
        table_name: str,
        is_critical: bool = False,
        compression_threshold: int = 10240,  # 10KB
        client: Optional[Any] = None,
    ):
        """Initialize DynamoDB audit storage.

        Args:
            table_name: DynamoDB table name
            is_critical: Whether failures should stop operations
            compression_threshold: Size threshold for compression (bytes)
            client: Optional DynamoDB client (for testing)
        """
        self.table_name = table_name
        self.is_critical = is_critical
        self.compression_threshold = compression_threshold

        # Use injected client or create default
        self._client = client or self._create_default_client()

        # Get circuit breaker for this service
        self._circuit_breaker = get_circuit_breaker(
            service_name=f"audit_storage_{table_name}",
            failure_threshold=5,
            timeout=60,
            expected_exception=ClientError,
        )

    def _create_default_client(self) -> Any:
        """Create default DynamoDB client."""
        settings = get_settings()
        return boto3.client("dynamodb", region_name=settings.aws_region)

    @retry_with_backoff(**ServiceRetryConfigs.DYNAMODB.to_dict())
    def store(self, event: AuditEvent) -> None:
        """Store a single audit event.

        Args:
            event: Audit event to store

        Raises:
            DynamoDBError: If storage fails and is_critical=True
        """
        try:
            with self._circuit_breaker:
                item = self._prepare_item(event)

                self._client.put_item(
                    TableName=self.table_name,
                    Item=item,
                    ConditionExpression="attribute_not_exists(pk)",  # Prevent overwrites
                )

                logger.debug(f"Stored audit event: {event.event_id}")

        except Exception as e:
            # Handle both ClientError and circuit breaker exceptions
            if isinstance(e, ClientError):
                error_code = e.response.get("Error", {}).get("Code", "")

                if error_code == "ConditionalCheckFailedException":
                    logger.warning(f"Duplicate audit event: {event.event_id}")
                    return

            logger.exception("Failed to store audit event")
            if self.is_critical:
                raise DynamoDBError(
                    f"Critical audit storage failed: {e}",
                    table_name=self.table_name,
                    operation="store_audit",
                    original_error=e,
                ) from e

    @retry_with_backoff(**ServiceRetryConfigs.DYNAMODB.to_dict())
    def store_batch(self, events: list[AuditEvent]) -> None:
        """Store multiple audit events efficiently.

        Args:
            events: List of audit events to store

        Raises:
            DynamoDBError: If batch storage fails and is_critical=True
        """
        if not events:
            return

        try:
            with self._circuit_breaker:
                # DynamoDB batch_write_item limit is 25 items
                batch_size = 25

                for i in range(0, len(events), batch_size):
                    batch = events[i : i + batch_size]

                    # Prepare batch request
                    request_items = {
                        self.table_name: [
                            {"PutRequest": {"Item": self._prepare_item(event)}} for event in batch
                        ]
                    }

                    # Execute batch write with retry for unprocessed items
                    unprocessed_items = request_items
                    max_retries = 3
                    retry_count = 0

                    while unprocessed_items and retry_count < max_retries:
                        response = self._client.batch_write_item(RequestItems=unprocessed_items)

                        unprocessed_items = response.get("UnprocessedItems", {})
                        if unprocessed_items:
                            retry_count += 1
                            logger.warning(
                                f"Batch write has unprocessed items, retry {retry_count}"
                            )

                    if unprocessed_items:
                        logger.error(
                            f"Failed to process {len(unprocessed_items)} items after retries"
                        )

                logger.debug(f"Stored batch of {len(events)} audit events")

        except Exception as e:
            logger.exception("Failed to store audit event batch")
            if self.is_critical:
                raise DynamoDBError(
                    f"Critical audit batch storage failed: {e}",
                    table_name=self.table_name,
                    operation="store_audit_batch",
                    original_error=e,
                ) from e

    @retry_with_backoff(**ServiceRetryConfigs.DYNAMODB.to_dict())
    def query_by_entity(
        self,
        entity_type: str,
        entity_id: str,
        limit: Optional[int] = None,
    ) -> list[AuditEvent]:
        """Query audit events by entity.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            limit: Maximum events to return

        Returns:
            List of audit events for the entity

        Raises:
            DynamoDBError: If query fails
        """
        try:
            # Query GSI1 for entity-based queries
            gsi1pk = f"ENTITY#{entity_type.upper()}#{entity_id}"

            query_params = {
                "TableName": self.table_name,
                "IndexName": "GSI1",
                "KeyConditionExpression": "gsi1pk = :pk",
                "ExpressionAttributeValues": {":pk": {"S": gsi1pk}},
                "ScanIndexForward": False,  # Most recent first
            }

            if limit:
                query_params["Limit"] = limit

            response = self._client.query(**query_params)

            events = []
            for item in response.get("Items", []):
                event_dict = self._parse_dynamodb_item(item)
                events.append(AuditEvent.from_dict(event_dict))

            logger.debug(f"Queried {len(events)} events for {entity_type}:{entity_id}")
            return events

        except ClientError as e:
            logger.exception("Failed to query audit events")
            raise DynamoDBError(
                f"Audit query failed: {e}",
                table_name=self.table_name,
                operation="query_by_entity",
                original_error=e,
            ) from e

    def _prepare_item(self, event: AuditEvent) -> dict[str, Any]:
        """Prepare audit event for DynamoDB storage.

        Args:
            event: Audit event to prepare

        Returns:
            DynamoDB item with proper keys and compressed data if needed
        """
        event_dict = event.to_dict()

        # Create DynamoDB keys
        keys = self._create_dynamodb_keys(event)

        # Handle state compression
        state_data, metadata = self._process_state_data(dict(event_dict))

        # Build base item
        item = self._build_base_item(event, dict(event_dict), keys)

        # Add optional fields
        self._add_optional_fields(item, event, state_data, metadata)

        return item

    def _create_dynamodb_keys(self, event: AuditEvent) -> dict[str, str]:
        """Create DynamoDB partition and sort keys."""
        event_date = event.timestamp.strftime("%Y-%m-%d")
        return {
            "pk": f"AUDIT#{event_date}",
            "sk": f"EVENT#{event.event_id}",
            "gsi1pk": f"ENTITY#{event.entity_type.upper()}#{event.entity_id}",
            "gsi1sk": f"TIMESTAMP#{event.timestamp.isoformat()}",
        }

    def _process_state_data(
        self, event_dict: dict[str, Any]
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Process and compress state data if needed."""
        state_data = {}
        compression_info = {}

        # Process before_state
        before_state = event_dict.get("before_state")
        if before_state:
            if self._should_compress(before_state):
                state_data["before_state"] = self._compress_data(before_state)
                compression_info["before_state"] = True
            else:
                state_data["before_state"] = before_state
                compression_info["before_state"] = False

        # Process after_state
        after_state = event_dict.get("after_state")
        if after_state:
            if self._should_compress(after_state):
                state_data["after_state"] = self._compress_data(after_state)
                compression_info["after_state"] = True
            else:
                state_data["after_state"] = after_state
                compression_info["after_state"] = False

        # Build metadata
        metadata = event_dict.get("metadata", {}).copy()
        if any(compression_info.values()):
            metadata["compressed"] = compression_info

        return state_data, metadata

    def _build_base_item(
        self, event: AuditEvent, event_dict: dict[str, Any], keys: dict[str, str]
    ) -> dict[str, Any]:
        """Build the base DynamoDB item with required fields."""
        # TTL for 2 years retention
        ttl = int(event.timestamp.timestamp() + (2 * 365 * 24 * 60 * 60))

        return {
            "pk": {"S": keys["pk"]},
            "sk": {"S": keys["sk"]},
            "gsi1pk": {"S": keys["gsi1pk"]},
            "gsi1sk": {"S": keys["gsi1sk"]},
            "event_id": {"S": event.event_id},
            "timestamp": {"S": event_dict["timestamp"]},
            "operation": {"S": event.operation},
            "entity_type": {"S": event.entity_type},
            "entity_id": {"S": event.entity_id},
            "ttl": {"N": str(ttl)},
        }

    def _add_optional_fields(
        self,
        item: dict[str, Any],
        event: AuditEvent,
        state_data: dict[str, Any],
        metadata: dict[str, Any],
    ) -> None:
        """Add optional fields to the DynamoDB item."""
        # Add correlation ID
        if event.correlation_id:
            item["correlation_id"] = {"S": event.correlation_id}

        # Add user ID
        if event.user_id is not None:
            item["user_id"] = {"S": event.user_id}

        # Add state data
        self._add_state_fields(item, state_data, metadata)

        # Add metadata
        if metadata:
            item["metadata"] = {"S": json.dumps(metadata, default=str)}

        # Add error
        if event.error:
            item["error"] = {"S": event.error}

        # Add duration
        if event.duration_ms:
            item["duration_ms"] = {"N": str(event.duration_ms)}

    def _add_state_fields(
        self, item: dict[str, Any], state_data: dict[str, Any], metadata: dict[str, Any]
    ) -> None:
        """Add state fields (before_state and after_state) to the item."""
        compression_info = metadata.get("compressed", {})

        # Add before_state
        if "before_state" in state_data:
            if compression_info.get("before_state"):
                item["before_state"] = {"B": state_data["before_state"]}
            else:
                item["before_state"] = {"S": json.dumps(state_data["before_state"], default=str)}

        # Add after_state
        if "after_state" in state_data:
            if compression_info.get("after_state"):
                item["after_state"] = {"B": state_data["after_state"]}
            else:
                item["after_state"] = {"S": json.dumps(state_data["after_state"], default=str)}

    def _should_compress(self, data: Any) -> bool:
        """Check if data should be compressed."""
        if not data:
            return False

        try:
            data_size = len(json.dumps(data, default=str).encode("utf-8"))
            return data_size > self.compression_threshold
        except (TypeError, ValueError):
            # If we can't serialize it, don't compress
            return False

    def _compress_data(self, data: Any) -> bytes:
        """Compress data using gzip."""
        json_data = json.dumps(data, default=str).encode("utf-8")
        return gzip.compress(json_data)

    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress gzipped data."""
        decompressed = gzip.decompress(compressed_data)
        return json.loads(decompressed.decode("utf-8"))

    def _parse_dynamodb_item(self, item: dict[str, Any]) -> AuditEventDict:
        """Parse DynamoDB item back to AuditEventDict."""
        result: dict[str, Any] = {
            "event_id": item["event_id"]["S"],
            "timestamp": item["timestamp"]["S"],
            "operation": item["operation"]["S"],
            "entity_type": item["entity_type"]["S"],
            "entity_id": item["entity_id"]["S"],
            "metadata": {},
        }

        # Handle optional fields
        if "correlation_id" in item:
            result["correlation_id"] = item["correlation_id"]["S"]

        if "user_id" in item:
            result["user_id"] = item["user_id"]["S"]

        if "error" in item:
            result["error"] = item["error"]["S"]

        if "duration_ms" in item:
            result["duration_ms"] = int(item["duration_ms"]["N"])

        # Parse metadata
        if "metadata" in item:
            metadata = json.loads(item["metadata"]["S"])
            result["metadata"] = metadata

            # Check for compression info
            compression_info = metadata.get("compressed", {})
        else:
            compression_info = {}

        # Handle before_state
        if "before_state" in item:
            if compression_info.get("before_state"):
                result["before_state"] = self._decompress_data(item["before_state"]["B"])
            else:
                result["before_state"] = json.loads(item["before_state"]["S"])

        # Handle after_state
        if "after_state" in item:
            if compression_info.get("after_state"):
                result["after_state"] = self._decompress_data(item["after_state"]["B"])
            else:
                result["after_state"] = json.loads(item["after_state"]["S"])

        return result  # type: ignore[return-value]
