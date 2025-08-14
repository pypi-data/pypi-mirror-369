"""Unified configuration loader for Flow SDK.

Loads Flow configuration from supported sources with a clear precedence order.
"""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
import os as _os_for_home

from flow.errors import ConfigParserError

logger = logging.getLogger(__name__)

# Resolve the real user's config path at import time to distinguish between
# test-provided temp configs (patched Path.home) and the developer's actual
# ~/.flow/config.yaml which should not be read during tests.
_ORIGINAL_USER_CONFIG_PATH = (Path(_os_for_home.path.expanduser("~")) / ".flow" / "config.yaml").resolve()

# Internal toggle used by Config.from_env to avoid reading the real user's
# ~/.flow/config.yaml during certain test scenarios. This avoids leaking a
# developer's config into tests without relying on process-wide env vars.
_SKIP_USER_CONFIG: bool = False


@dataclass
class ConfigSources:
    """All configuration data from various sources.

    Streamlined to only consider environment variables and the YAML config file
    as sources for provider API credentials. Provider-specific credentials files
    are deliberately ignored to reduce ambiguity in precedence and simplify
    mental models.
    """

    env_vars: dict[str, str]
    config_file: dict[str, Any]

    @property
    def api_key(self) -> str | None:
        """Get API key with clear precedence: environment > config file.

        The credentials-file fallback has been removed on purpose.
        """
        return self.env_vars.get("MITHRIL_API_KEY") or self.config_file.get("api_key")

    @property
    def provider(self) -> str:
        """Get provider with proper precedence and demo-mode override.

        Precedence:
        1) Demo mode (FLOW_DEMO_MODE=1) → provider 'mock' unless FLOW_PROVIDER explicitly set
        2) FLOW_PROVIDER env var
        3) config file 'provider'
        4) default 'mithril'
        """
        # 1) Respect explicit provider even if a persisted demo env exists
        provider_env = self.env_vars.get("FLOW_PROVIDER")
        demo = self.env_vars.get("FLOW_DEMO_MODE")
        if provider_env:
            # Explicit provider overrides demo mode for provider selection
            return provider_env
        if demo and str(demo).lower() in ("1", "true", "yes"):
            # Demo active without explicit provider → default to mock
            return "mock"

        # 2) Explicit env var wins (and cancels demo mode)
        if provider_env:
            try:
                if str(provider_env).strip().lower() != "mock":
                    os.environ["FLOW_DEMO_MODE"] = "0"
            except Exception:
                pass
            return provider_env

        # 3) Config file provider key
        cfg_provider = self.config_file.get("provider") if isinstance(self.config_file, dict) else None
        if cfg_provider:
            return str(cfg_provider)

        # 4) Default
        return "mithril"

    def get_mithril_config(self) -> dict[str, Any]:
        """Get Mithril-specific configuration with proper precedence."""
        config = {}

        # API URL (canonical env var + provider section; fallback to top-level for migration)
        config["api_url"] = (
            self.env_vars.get("MITHRIL_API_URL")
            or self.config_file.get("mithril", {}).get("api_url")
            or self.config_file.get("api_url")
            or "https://api.mithril.ai"
        )

        # Project (canonical env var and provider section; fallback to top-level for migration)
        project = (
            self.env_vars.get("MITHRIL_PROJECT")
            or self.env_vars.get("MITHRIL_DEFAULT_PROJECT")
            or self.config_file.get("mithril", {}).get("project")
            or self.config_file.get("project")
        )
        if project:
            config["project"] = project

        # Region (canonical env var and provider section; fallback to top-level for migration)
        region = (
            self.env_vars.get("MITHRIL_REGION")
            or self.env_vars.get("MITHRIL_DEFAULT_REGION")
            or self.config_file.get("mithril", {}).get("region")
            or self.config_file.get("region")
        )
        if region:
            config["region"] = region

        # SSH Keys
        ssh_keys_env = self.env_vars.get("MITHRIL_SSH_KEYS")
        if ssh_keys_env:
            config["ssh_keys"] = [k.strip() for k in ssh_keys_env.split(",") if k.strip()]
        else:
            # Check config file
            ssh_keys = self.config_file.get("mithril", {}).get("ssh_keys")
            if ssh_keys:
                config["ssh_keys"] = ssh_keys
            else:
                # Legacy single-key field
                legacy_key = self.config_file.get("default_ssh_key") or self.config_file.get("ssh_key")
                if legacy_key:
                    config["ssh_keys"] = [legacy_key]

        # Pricing overrides (from config file only; explicit CLI flags override at runtime)
        try:
            limit_prices = self.config_file.get("mithril", {}).get("limit_prices")
            if isinstance(limit_prices, dict) and limit_prices:
                config["limit_prices"] = limit_prices
        except Exception:
            pass

        return config

    def get_health_config(self) -> dict[str, Any]:
        """Get health monitoring configuration with proper precedence."""
        config = {}

        # Health monitoring enabled
        config["enabled"] = (
            self.env_vars.get("FLOW_HEALTH_MONITORING", "true").lower() == "true"
            if "FLOW_HEALTH_MONITORING" in self.env_vars
            else self.config_file.get("health", {}).get("enabled", True)
        )

        # GPUd configuration
        config["gpud_version"] = self.env_vars.get("FLOW_GPUD_VERSION") or self.config_file.get(
            "health", {}
        ).get("gpud_version", "v0.5.1")

        config["gpud_port"] = int(
            self.env_vars.get("FLOW_GPUD_PORT")
            or self.config_file.get("health", {}).get("gpud_port", 15132)
        )

        config["gpud_bind"] = self.env_vars.get("FLOW_GPUD_BIND") or self.config_file.get(
            "health", {}
        ).get("gpud_bind", "127.0.0.1")

        # Metrics configuration
        config["metrics_endpoint"] = self.env_vars.get(
            "FLOW_METRICS_ENDPOINT"
        ) or self.config_file.get("health", {}).get("metrics_endpoint")

        config["metrics_batch_size"] = int(
            self.env_vars.get("FLOW_METRICS_BATCH_SIZE")
            or self.config_file.get("health", {}).get("metrics_batch_size", 100)
        )

        config["metrics_interval"] = int(
            self.env_vars.get("FLOW_METRICS_INTERVAL")
            or self.config_file.get("health", {}).get("metrics_interval", 60)
        )

        # Storage configuration
        config["retention_days"] = int(
            self.env_vars.get("FLOW_METRICS_RETENTION_DAYS")
            or self.config_file.get("health", {}).get("retention_days", 7)
        )

        config["compress_after_days"] = int(
            self.env_vars.get("FLOW_METRICS_COMPRESS_AFTER_DAYS")
            or self.config_file.get("health", {}).get("compress_after_days", 1)
        )

        return config


class ConfigLoader:
    """Unified configuration loader with clear precedence and error handling."""

    def __init__(self, config_path: Path | None = None, *, skip_user_config: bool = False):
        """Initialize the loader.

        Args:
            config_path: Path to config file (defaults to ~/.flow/config.yaml)
        """
        self.config_path = config_path or Path.home() / ".flow" / "config.yaml"
        self._skip_user_config = skip_user_config

    def load_all_sources(self) -> ConfigSources:
        """Load configuration from all available sources.

        Returns:
            ConfigSources object with all available configuration
        """
        # 1. Environment variables (highest precedence)
        env_vars = dict(os.environ)

        # 2. Config file (lowest precedence)
        if self._skip_user_config:
            config_file = {}
        else:
            # Under pytest, avoid reading the developer's real ~/.flow/config.yaml.
            # Tests that want to supply a config file patch Path.home() so the
            # loader's config_path differs from the original.
            if os.getenv("PYTEST_CURRENT_TEST") and self.config_path.resolve() == _ORIGINAL_USER_CONFIG_PATH:
                config_file = {}
            else:
                config_file = self._load_config_file()

        return ConfigSources(env_vars=env_vars, config_file=config_file)

    # NOTE: Legacy credential files (e.g., ~/.flow/credentials.*) are intentionally
    # not supported. The single source of truth is ~/.flow/config.yaml plus
    # process environment variables. Keeping this stub documents that decision
    # and avoids accidental reintroduction.

    def _load_config_file(self) -> dict[str, Any]:
        """Load configuration from YAML file.

        Returns:
            Configuration dict, empty dict if file doesn't exist or has errors
        """
        if not self.config_path.exists():
            return {}

        try:
            with open(self.config_path) as f:
                content = yaml.safe_load(f) or {}
                if not isinstance(content, dict):
                    raise ConfigParserError(
                        f"Configuration file must contain a YAML dictionary, got {type(content).__name__}",
                        suggestions=[
                            "Ensure your config file starts with key: value pairs",
                            "Check that you haven't accidentally created a list or string",
                            "Example valid config: api_key: YOUR_KEY",
                        ],
                        error_code="CONFIG_002",
                    )
                return content
        except yaml.YAMLError as e:
            raise ConfigParserError(
                f"Invalid YAML syntax in {self.config_path}: {str(e)}",
                suggestions=[
                    "Check YAML indentation (use spaces, not tabs)",
                    "Ensure all strings with special characters are quoted",
                    "Validate syntax at yamllint.com",
                    "Common issue: unquoted strings containing colons",
                ],
                error_code="CONFIG_001",
            ) from e
        except ConfigParserError:
            raise
        except Exception as e:
            # For unexpected errors, still log and return empty dict for backward compatibility
            logger.warning(f"Unexpected error reading config file {self.config_path}: {e}")
            return {}

    def has_valid_config(self) -> bool:
        """Check if valid configuration exists.

        Returns:
            True if we have an API key from any source
        """
        sources = self.load_all_sources()
        api_key = sources.api_key
        return bool(api_key and not api_key.startswith("YOUR_"))

    def get_config_status(self) -> tuple[bool, str]:
        """Get detailed configuration status.

        Returns:
            Tuple of (is_valid, status_message)
        """
        sources = self.load_all_sources()

        # Check API key
        if sources.env_vars.get("MITHRIL_API_KEY"):
            api_key_source = "environment variable (MITHRIL_API_KEY)"
        elif sources.config_file.get("api_key"):
            api_key_source = "config file"
        else:
            return (
                False,
                "No API key found in environment (MITHRIL_API_KEY) or config file",
            )

        api_key = sources.api_key
        if not api_key:
            return False, "No API key configured"

        if api_key.startswith("YOUR_"):
            return False, f"API key in {api_key_source} needs to be updated"

        # Check project
        mithril_config = sources.get_mithril_config()
        if not mithril_config.get("project"):
            return False, f"API key found in {api_key_source}, but no project configured"

        return True, f"Valid configuration found (API key from {api_key_source})"
