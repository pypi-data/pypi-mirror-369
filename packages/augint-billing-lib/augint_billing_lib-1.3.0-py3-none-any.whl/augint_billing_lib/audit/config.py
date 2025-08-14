"""Configuration management for audit system.

This module provides centralized configuration for audit logging
with environment variable support and validation.
"""

import os
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class AuditConfig:
    """Centralized configuration for audit system.

    This class consolidates all configuration options for the audit system,
    eliminating magic numbers and providing environment variable support.
    """

    # Storage configuration
    table_name: str = "billing-data-dev"
    storage_critical: bool = False  # Graceful degradation by default

    # Compression settings
    compression_enabled: bool = True
    compression_threshold: int = 10240  # 10KB

    # Redaction settings
    redaction_enabled: bool = True
    max_redaction_depth: int = 10

    # Performance settings
    batch_size: int = 100
    flush_interval: float = 5.0  # seconds

    # Retention settings
    retention_days: int = 730  # 2 years

    # Circuit breaker settings
    circuit_breaker_enabled: bool = True
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 60  # seconds

    @classmethod
    def from_env(cls) -> "AuditConfig":
        """Create configuration from environment variables.

        Returns:
            AuditConfig instance with values from environment
        """
        return cls(
            table_name=os.getenv("AUDIT_TABLE_NAME", "billing-data-dev"),
            storage_critical=_get_env_bool("AUDIT_STORAGE_CRITICAL", False),
            compression_enabled=_get_env_bool("AUDIT_COMPRESSION_ENABLED", True),
            compression_threshold=int(os.getenv("AUDIT_COMPRESSION_THRESHOLD", "10240")),
            redaction_enabled=_get_env_bool("AUDIT_REDACTION_ENABLED", True),
            max_redaction_depth=int(os.getenv("AUDIT_MAX_REDACTION_DEPTH", "10")),
            batch_size=int(os.getenv("AUDIT_BATCH_SIZE", "100")),
            flush_interval=float(os.getenv("AUDIT_FLUSH_INTERVAL", "5.0")),
            retention_days=int(os.getenv("AUDIT_RETENTION_DAYS", "730")),
            circuit_breaker_enabled=_get_env_bool("AUDIT_CIRCUIT_BREAKER_ENABLED", True),
            circuit_breaker_failure_threshold=int(
                os.getenv("AUDIT_CIRCUIT_BREAKER_FAILURE_THRESHOLD", "5")
            ),
            circuit_breaker_timeout=int(os.getenv("AUDIT_CIRCUIT_BREAKER_TIMEOUT", "60")),
        )

    def validate(self) -> None:
        """Validate configuration values.

        Raises:
            ValueError: If configuration is invalid
        """
        if self.compression_threshold <= 0:
            raise ValueError("compression_threshold must be > 0")

        if self.max_redaction_depth <= 0:
            raise ValueError("max_redaction_depth must be > 0")

        if self.batch_size <= 0:
            raise ValueError("batch_size must be > 0")

        if self.flush_interval <= 0:
            raise ValueError("flush_interval must be > 0")

        if self.retention_days <= 0:
            raise ValueError("retention_days must be > 0")

        if self.circuit_breaker_failure_threshold <= 0:
            raise ValueError("circuit_breaker_failure_threshold must be > 0")

        if self.circuit_breaker_timeout <= 0:
            raise ValueError("circuit_breaker_timeout must be > 0")

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of configuration
        """
        return {
            "table_name": self.table_name,
            "storage_critical": self.storage_critical,
            "compression_enabled": self.compression_enabled,
            "compression_threshold": self.compression_threshold,
            "redaction_enabled": self.redaction_enabled,
            "max_redaction_depth": self.max_redaction_depth,
            "batch_size": self.batch_size,
            "flush_interval": self.flush_interval,
            "retention_days": self.retention_days,
            "circuit_breaker_enabled": self.circuit_breaker_enabled,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "circuit_breaker_timeout": self.circuit_breaker_timeout,
        }


def _get_env_bool(key: str, default: bool) -> bool:
    """Get boolean value from environment variable.

    Args:
        key: Environment variable key
        default: Default value if not set

    Returns:
        Boolean value
    """
    value = os.getenv(key)
    if value is None or value == "":
        return default
    return value.lower() in ("true", "1", "yes", "on")


# Global configuration instance
_config: Optional[AuditConfig] = None


def get_audit_config() -> AuditConfig:
    """Get global audit configuration instance.

    Returns:
        Cached AuditConfig instance
    """
    global _config  # noqa: PLW0603
    if _config is None:
        _config = AuditConfig.from_env()
        _config.validate()
    return _config


def reset_audit_config() -> None:
    """Reset global configuration (useful for testing)."""
    global _config  # noqa: PLW0603
    _config = None
