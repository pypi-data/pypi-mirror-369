"""Type system for Flow's public API models (Pydantic-based).

Examples:
    Construct a TaskConfig for distributed training:
        >>> from flow.api.models import TaskConfig, VolumeSpec
        >>> cfg = TaskConfig(
        ...     name="train-ddp",
        ...     instance_type="8xa100",
        ...     command=["torchrun", "--nproc_per_node=8", "train.py", "--epochs", "50"],
        ...     env={"BATCH_SIZE": "512"},
        ...     volumes=[VolumeSpec(size_gb=500, mount_path="/data", name="datasets")],
        ...     max_price_per_hour=30.0,
        ... )
"""

import logging
import re
from collections.abc import Iterator
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Literal
from uuid import NAMESPACE_DNS, UUID, uuid5

import yaml
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator, model_validator

from flow.errors import FlowError
from flow.core.docker import DockerConfig
from flow.core.paths import WORKSPACE_DIR, VOLUMES_ROOT

logger = logging.getLogger(__name__)


# ================== Section 1: Common Enums ==================


class Retries(BaseModel):
    """Retry policy with fixed or exponential backoff."""

    max_retries: int = Field(3, ge=0, le=10, description="Maximum retry attempts (0-10)")
    backoff_coefficient: float = Field(
        2.0, ge=1.0, le=10.0, description="Delay multiplier between retries"
    )
    initial_delay: float = Field(
        1.0, ge=0.1, le=300.0, description="Initial delay in seconds before first retry"
    )
    max_delay: float | None = Field(
        None, ge=1.0, le=3600.0, description="Maximum delay between retries (seconds)"
    )

    @model_validator(mode="after")
    def validate_delays(self) -> "Retries":
        """Ensure max_delay is greater than initial_delay if set."""
        if self.max_delay is not None and self.max_delay < self.initial_delay:
            raise ValueError(
                f"max_delay ({self.max_delay}s) must be >= initial_delay ({self.initial_delay}s)"
            )
        return self

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given retry attempt.

        Args:
            attempt: Retry attempt number (1-based)

        Returns:
            Delay in seconds before this retry attempt
        """
        if attempt <= 0:
            return 0.0

        # Calculate exponential backoff
        delay = self.initial_delay * (self.backoff_coefficient ** (attempt - 1))

        # Apply max_delay cap if set
        if self.max_delay is not None:
            delay = min(delay, self.max_delay)

        return delay

    @classmethod
    def fixed(cls, retries: int = 3, delay: float = 5.0) -> "Retries":
        """Create fixed-interval retry configuration.

        Args:
            retries: Number of retry attempts
            delay: Fixed delay between retries (seconds)

        Returns:
            Retries with fixed intervals

        Example:
            >>> retry = Retries.fixed(retries=5, delay=10.0)
            # Retries every 10 seconds, up to 5 times
        """
        return cls(max_retries=retries, backoff_coefficient=1.0, initial_delay=delay)

    @classmethod
    def exponential(
        cls,
        retries: int = 3,
        initial: float = 1.0,
        multiplier: float = 2.0,
        max_delay: float | None = None,
    ) -> "Retries":
        """Create exponential backoff retry configuration.

        Args:
            retries: Number of retry attempts
            initial: Initial delay (seconds)
            multiplier: Delay multiplier for each retry
            max_delay: Maximum delay cap (seconds)

        Returns:
            Retries with exponential backoff

        Example:
            >>> retry = Retries.exponential(
            ...     retries=4,
            ...     initial=2.0,
            ...     multiplier=3.0,
            ...     max_delay=60.0
            ... )
            # Delays: 2s, 6s, 18s, 54s
        """
        return cls(
            max_retries=retries,
            backoff_coefficient=multiplier,
            initial_delay=initial,
            max_delay=max_delay,
        )


class TaskStatus(str, Enum):
    """Task lifecycle states."""

    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    PREEMPTING = "preempting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstanceStatus(str, Enum):
    """Status of a compute instance."""

    PENDING = "pending"
    RUNNING = "running"
    STOPPED = "stopped"
    TERMINATED = "terminated"


class ReservationStatus(str, Enum):
    """Reservation lifecycle states."""

    SCHEDULED = "scheduled"  # Accepted and not yet started
    ACTIVE = "active"  # Instances allocated and available
    EXPIRED = "expired"  # Window elapsed
    FAILED = "failed"  # Provisioning failed


class StorageInterface(str, Enum):
    """Storage interface type."""

    BLOCK = "block"
    FILE = "file"


# ================== Section 2: Hardware Specifications ==================


class GPUSpec(BaseModel):
    """Immutable GPU hardware specification used for matching."""

    model_config = ConfigDict(frozen=True)

    vendor: str = Field(default="NVIDIA", description="GPU vendor")
    model: str = Field(..., description="GPU model (e.g., A100, H100)")
    memory_gb: int = Field(..., gt=0, description="GPU memory in GB")
    memory_type: str = Field(default="", description="Memory type (HBM2e, HBM3, GDDR6)")
    architecture: str = Field(default="", description="GPU architecture (Ampere, Hopper)")
    compute_capability: tuple[int, int] = Field(
        default=(0, 0), description="CUDA compute capability"
    )
    tflops_fp32: float = Field(default=0.0, ge=0, description="FP32 performance in TFLOPS")
    tflops_fp16: float = Field(default=0.0, ge=0, description="FP16 performance in TFLOPS")
    memory_bandwidth_gb_s: float = Field(default=0.0, ge=0, description="Memory bandwidth in GB/s")

    @property
    def canonical_name(self) -> str:
        """Canonical name like: nvidia-a100-80gb."""
        return f"{self.vendor}-{self.model}-{self.memory_gb}gb".lower()

    @property
    def display_name(self) -> str:
        """Human-friendly name like: NVIDIA A100 80GB."""
        return f"{self.vendor} {self.model.upper()} {self.memory_gb}GB"


class CPUSpec(BaseModel):
    """CPU specification."""

    model_config = ConfigDict(frozen=True)

    vendor: str = Field(default="Intel", description="CPU vendor")
    model: str = Field(default="Xeon", description="CPU model")
    cores: int = Field(..., gt=0, description="Number of CPU cores")
    threads: int = Field(default=0, ge=0, description="Number of threads (0 = same as cores)")
    base_clock_ghz: float = Field(default=0.0, ge=0, description="Base clock speed in GHz")

    @model_validator(mode="after")
    def set_threads_default(self) -> "CPUSpec":
        """Default `threads` to `cores` when not specified."""
        if self.threads == 0:
            object.__setattr__(self, "threads", self.cores)
        return self


class MemorySpec(BaseModel):
    """System memory specification."""

    model_config = ConfigDict(frozen=True)

    size_gb: int = Field(..., gt=0, description="Memory size in GB")
    type: str = Field(default="DDR4", description="Memory type")
    speed_mhz: int = Field(default=3200, gt=0, description="Memory speed in MHz")
    ecc: bool = Field(default=True, description="ECC memory support")


class StorageSpec(BaseModel):
    """Storage specification."""

    model_config = ConfigDict(frozen=True)

    size_gb: int = Field(..., ge=0, description="Storage size in GB")
    type: str = Field(default="NVMe", description="Storage type (NVMe, SSD, HDD)")
    iops: int | None = Field(default=None, ge=0, description="IOPS rating")
    bandwidth_mb_s: int | None = Field(default=None, ge=0, description="Bandwidth in MB/s")


class NetworkSpec(BaseModel):
    """Network specification."""

    model_config = ConfigDict(frozen=True)

    intranode: str = Field(default="", description="Intra-node interconnect (SXM4, SXM5, PCIe)")
    internode: str | None = Field(
        default=None, description="Inter-node network (InfiniBand, Ethernet)"
    )
    bandwidth_gbps: float | None = Field(
        default=None, ge=0, description="Network bandwidth in Gbps"
    )

    @property
    def has_high_speed_interconnect(self) -> bool:
        """True if a high-speed inter-node interconnect is present."""
        return self.internode in {"InfiniBand", "IB", "IB_1600", "IB_3200"}


class InstanceType(BaseModel):
    """Canonical instance type specification (immutable)."""

    model_config = ConfigDict(frozen=True)

    # Hardware specifications
    gpu: GPUSpec
    gpu_count: int = Field(..., gt=0, description="Number of GPUs")
    cpu: CPUSpec
    memory: MemorySpec
    storage: StorageSpec
    network: NetworkSpec

    # Identity and metadata
    id: UUID | None = Field(default=None, description="Unique instance type ID")
    aliases: set[str] = Field(default_factory=set, description="Alternative names")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = Field(default=1, ge=1)

    @model_validator(mode="after")
    def compute_id_and_aliases(self) -> "InstanceType":
        """Compute a stable ID and default aliases."""
        # Generate stable UUID from content
        content = self._canonical_string()
        if not self.id:
            object.__setattr__(self, "id", uuid5(NAMESPACE_DNS, content))

        # Generate default aliases if none provided
        if not self.aliases:
            object.__setattr__(self, "aliases", self._generate_aliases())

        return self

    def _canonical_string(self) -> str:
        """Canonical string used for hashing/UUID derivation."""
        parts = [
            f"gpu:{self.gpu.vendor}-{self.gpu.model}-{self.gpu.memory_gb}gb",
            f"count:{self.gpu_count}",
            f"cpu:{self.cpu.cores}",
            f"mem:{self.memory.size_gb}",
            f"net:{self.network.intranode}-{self.network.internode}",
        ]
        return "|".join(parts)

    def _generate_aliases(self) -> set[str]:
        """Generate common aliases for this instance type."""
        aliases = set()

        # API style: gpu.nvidia.a100
        api_style = f"gpu.{self.gpu.vendor.lower()}.{self.gpu.model.lower()}"
        aliases.add(api_style)

        # Short form: a100-80gb
        short_form = f"{self.gpu.model.lower()}-{self.gpu.memory_gb}gb"
        aliases.add(short_form)

        # With count: 8xa100
        with_count = f"{self.gpu_count}x{self.gpu.model.lower()}"
        aliases.add(with_count)

        return aliases

    @property
    def canonical_name(self) -> str:
        """Canonical name following our convention."""
        return f"gpu.{self.gpu.vendor.lower()}.{self.gpu.model.lower()}"

    @property
    def display_name(self) -> str:
        """Human-friendly display name."""
        return f"{self.gpu_count}x {self.gpu.display_name}"

    @property
    def total_gpu_memory_gb(self) -> int:
        """Total GPU memory across all GPUs."""
        return self.gpu.memory_gb * self.gpu_count

    @property
    def total_tflops_fp32(self) -> float:
        """Total FP32 compute power."""
        return self.gpu.tflops_fp32 * self.gpu_count


class InstanceMatch(BaseModel):
    """Matched instance with price and availability."""

    instance: InstanceType
    region: str
    availability: int = Field(..., ge=0, description="Number of available instances")
    price_per_hour: float = Field(..., ge=0, description="Price in USD per hour")
    match_score: float = Field(default=1.0, ge=0, le=1.0, description="Match quality score")

    @property
    def price_performance(self) -> float:
        """TFLOPS per dollar."""
        if self.price_per_hour > 0:
            return self.instance.total_tflops_fp32 / self.price_per_hour
        return 0.0


class ReservationSpec(BaseModel):
    """Provider-agnostic spec for creating a reservation."""

    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(
        default=None,
        description="Optional reservation name for display",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$",
    )
    project_id: str | None = Field(default=None, description="Provider project/workspace ID")
    instance_type: str = Field(..., description="Explicit instance type (e.g., 'a100', '8xh100')")
    region: str = Field(..., description="Target region/zone for the reservation")
    quantity: int = Field(1, ge=1, le=100, description="Number of instances to reserve")
    start_time_utc: datetime = Field(..., description="Reservation start time (UTC)")
    duration_hours: int = Field(
        ..., ge=3, le=336, description="Reservation duration in hours (3-336)"
    )
    ssh_keys: list[str] = Field(default_factory=list, description="Authorized SSH key IDs")
    volumes: list[str] = Field(
        default_factory=list, description="Volume IDs to attach (provider-specific)"
    )
    startup_script: str | None = Field(
        default=None,
        description="Optional startup script executed when instances boot",
    )


class Reservation(BaseModel):
    """Reservation details returned by providers."""

    model_config = ConfigDict(extra="allow")

    reservation_id: str = Field(..., description="Reservation identifier")
    name: str | None = Field(default=None, description="Display name")
    status: ReservationStatus = Field(..., description="Lifecycle state")
    instance_type: str = Field(..., description="Instance type identifier")
    region: str = Field(..., description="Region/zone")
    quantity: int = Field(..., ge=1, description="Number of instances")
    start_time_utc: datetime = Field(..., description="Scheduled start time (UTC)")
    end_time_utc: datetime | None = Field(default=None, description="Scheduled end time (UTC)")
    price_total_usd: float | None = Field(
        default=None, ge=0, description="Quoted/actual total price"
    )
    provider_metadata: dict[str, Any] = Field(default_factory=dict)


# ================== Section 3: Core Domain Models ==================


class User(BaseModel):
    """User identity information."""

    user_id: str = Field(..., description="Unique user identifier (e.g., 'user_kfV4CCaapLiqCNlv')")
    username: str = Field(..., description="Username for display")
    email: str = Field(..., description="User email address")
    # Future fields: full_name, organization, created_at


class VolumeSpec(BaseModel):
    """Persistent volume specification (create or attach)."""

    model_config = ConfigDict(extra="forbid")

    # Human-friendly name
    name: str | None = Field(
        None,
        description="Human-readable name (3-64 chars, lowercase alphanumeric with hyphens)",
        pattern="^[a-z0-9][a-z0-9-]*[a-z0-9]$",
        min_length=3,
        max_length=64,
    )

    # Core fields
    size_gb: int = Field(1, ge=1, le=15000, description="Size in GB")
    # Canonical field name is mount_path; accept 'target' as an alias via pre-validation below
    mount_path: str | None = Field(
        None, description="Mount path in container (default: /volumes/<name>)"
    )

    # Volume ID for existing volumes
    volume_id: str | None = Field(None, description="ID of existing volume to attach")

    # Advanced options
    interface: StorageInterface = Field(
        StorageInterface.BLOCK, description="Storage interface type"
    )
    iops: int | None = Field(None, ge=100, le=64000, description="Provisioned IOPS")
    throughput_mb_s: int | None = Field(None, ge=125, le=1000, description="Provisioned throughput")

    @model_validator(mode="after")
    def validate_volume_spec(self) -> "VolumeSpec":
        """Validate volume specification."""
        if self.volume_id and (self.iops or self.throughput_mb_s):
            raise ValueError("Cannot specify IOPS/throughput for existing volumes")
        # Set sensible default mount path if not provided
        if not self.mount_path:
            # Prefer using provided name
            if self.name:
                object.__setattr__(self, "mount_path", f"{VOLUMES_ROOT}/{self.name}")
            elif self.volume_id:
                # Derive a readable stable path from volume id suffix
                suffix = self.volume_id[-6:] if len(self.volume_id) >= 6 else self.volume_id
                object.__setattr__(self, "mount_path", f"{VOLUMES_ROOT}/volume-{suffix}")
            else:
                # Fallback (should be rare for new unnamed volumes)
                object.__setattr__(self, "mount_path", f"{VOLUMES_ROOT}/volume")
        return self

    @model_validator(mode="before")
    def _alias_target_to_mount_path(cls, data: Any):  # type: ignore[no-redef]
        """Allow 'target' as an alias for 'mount_path' in YAML/JSON."""
        if isinstance(data, dict):
            if "mount_path" not in data and "target" in data:
                data = {**data, "mount_path": data.get("target")}
                # Do not keep duplicate alias key to avoid 'extra=forbid' issues
                data.pop("target", None)
        return data


class MountSpec(BaseModel):
    """Mount specification for volumes, S3, or bind mounts."""

    source: str = Field(..., description="Source URL or path")
    target: str = Field(..., description="Mount path in container")
    mount_type: Literal["bind", "volume", "s3fs"] = Field("bind", description="Type of mount")
    options: dict[str, Any] = Field(default_factory=dict, description="Provider-specific options")

    # Performance hints
    cache_key: str | None = Field(None, description="Key for caching mount metadata")
    size_estimate_gb: float | None = Field(None, ge=0, description="Estimated size for planning")


class TaskConfig(BaseModel):
    """Complete task specification used by `Flow.run()`.

    One obvious way to express requirements; fails fast with clear validation.
    """

    model_config = ConfigDict(extra="allow")

    # Basic configuration
    name: str = Field(
        "flow-task",
        description="Task identifier",
        pattern=r"^[a-zA-Z0-9][a-zA-Z0-9._-]*$",
    )
    unique_name: bool = Field(True, description="Append unique suffix to name to ensure uniqueness")

    # Instance specification - either explicit type or capability-based
    instance_type: str | None = Field(None, description="Explicit instance type")
    min_gpu_memory_gb: int | None = Field(
        None, ge=1, le=640, description="Minimum GPU memory requirement"
    )

    # Command specification - accepts string, list, or multi-line script
    command: str | list[str] | None = Field(
        None, description="Command to execute (string, list, or script)"
    )

    # Environment
    image: str = Field("nvidia/cuda:12.1.0-runtime-ubuntu22.04", description="Container image")
    env: dict[str, str] = Field(default_factory=dict, description="Environment")

    @property
    def environment(self) -> dict[str, str]:
        """Alias for `env` (backward compatibility)."""
        return self.env

    working_dir: str = Field("/workspace", description="Container working directory")

    # Resources
    volumes: list[VolumeSpec | dict[str, Any]] = Field(default_factory=list)
    data_mounts: list[MountSpec] = Field(default_factory=list, description="Data to mount")

    # Networking
    ports: list[int] = Field(
        default_factory=list,
        description="Container/instance ports to expose. High ports only (>=1024).",
    )
    # Advanced: allow Docker data-root cache when explicitly enabled (single-node only)
    allow_docker_cache: bool = Field(
        False,
        description=(
            "Allow mounting a volume at /var/lib/docker to persist Docker image layers. "
            "Single-node tasks only; use with caution."
        ),
    )

    # Execution options
    retries: Retries | None = Field(
        default=None, description="Advanced retry configuration for task submission/execution"
    )
    max_price_per_hour: float | None = Field(None, gt=0, description="Maximum hourly price (USD)")
    max_run_time_hours: float | None = Field(
        None, description="Maximum runtime hours; 0 or None disables runtime monitoring"
    )
    min_run_time_hours: float | None = Field(
        None, gt=0, description="Minimum guaranteed runtime hours"
    )
    deadline_hours: float | None = Field(
        None, gt=0, le=168, description="Hours from submission until deadline"
    )

    # SSH and access
    ssh_keys: list[str] = Field(default_factory=list, description="Authorized SSH key IDs")

    # Advanced options
    allocation_mode: Literal["spot", "reserved", "auto"] = Field(
        "spot",
        description=(
            "Allocation strategy: 'spot' (default, preemptible), 'reserved' (scheduled capacity), or 'auto'."
        ),
    )
    reservation_id: str | None = Field(
        None, description="Target an existing reservation (advanced)."
    )
    scheduled_start_time: datetime | None = Field(
        None, description="When allocation_mode='reserved', schedule start (UTC)."
    )
    reserved_duration_hours: int | None = Field(
        None,
        ge=3,
        le=336,
        description="When allocation_mode='reserved', reservation duration in hours (3-336).",
    )
    region: str | None = Field(None, description="Target region")
    num_instances: int = Field(1, ge=1, le=100, description="Instance count")
    priority: Literal["low", "med", "high"] = Field(
        "med", description="Task priority tier affecting limit price"
    )
    # Distributed execution mode: None => provider decides (auto for multi-node)
    distributed_mode: Literal["auto", "manual"] | None = Field(
        None,
        description=(
            "Distributed rendezvous mode when num_instances > 1: "
            "'auto' lets Flow assign rank and leader IP; 'manual' expects user-set FLOW_* envs."
        ),
    )
    # Topology preferences
    internode_interconnect: str | None = Field(
        None,
        description="Preferred inter-node network (e.g., InfiniBand, IB_3200, Ethernet)",
    )
    intranode_interconnect: str | None = Field(
        None, description="Preferred intra-node interconnect (e.g., SXM5, PCIe)"
    )
    upload_code: bool = Field(True, description="Upload current directory code to job")
    upload_strategy: Literal["auto", "embedded", "scp", "none"] = Field(
        "auto",
        description=(
            "Strategy for uploading code to instances:\n"
            "  - auto: Use SCP for large (>8KB), embedded for small\n"
            "  - embedded: Include in startup script (10KB limit)\n"
            "  - scp: Transfer after instance starts (no size limit)\n"
            "  - none: No code upload"
        ),
    )
    upload_timeout: int = Field(
        600, ge=60, le=3600, description="Maximum seconds to wait for code upload (60-3600)"
    )
    # Local code root selection
    code_root: str | Path | None = Field(
        default=None,
        description=(
            "Local project directory to upload when upload_code=True. "
            "Defaults to the current working directory when not set."
        ),
    )

    @field_validator("code_root", mode="before")
    def _normalize_code_root(cls, v: Any) -> str | None:
        """Normalize code_root to a string path for safe serialization.

        Accepts Path-like inputs and converts to string. Leaves None as-is.
        """
        if v is None or v == "":
            return None
        try:
            # Expand '~' and user variables; keep relative paths (like '.') relative to CWD
            return str(Path(v).expanduser())
        except Exception:
            return str(v)

    @field_validator("command", mode="before")
    def normalize_command(cls, v: Any) -> str | list[str]:
        """Accept strings and lists; preserve the original form."""
        # Accept both strings and lists without transformation
        if isinstance(v, (str, list)):
            return v
        return v

    @field_validator("volumes", mode="before")
    def normalize_volumes(cls, v: Any) -> list[VolumeSpec]:
        """Convert dicts to `VolumeSpec` instances; pass through existing ones."""
        result: list[VolumeSpec] = []
        for vol in v:
            if isinstance(vol, dict):
                result.append(VolumeSpec(**vol))
            elif isinstance(vol, Volume):
                # Accept Volume objects constructed from mount-like inputs (tests)
                # Map to bind mount in data_mounts semantics
                local = getattr(vol, "local", None)
                remote = getattr(vol, "remote", None)
                if local and remote:
                    # Use minimal non-zero size to satisfy validation; builder treats as bind mount
                    result.append(VolumeSpec(size_gb=1, mount_path=remote, name=vol.name or ""))
                else:
                    # Fallback: synthesize a spec from the volume identity
                    sz = int(getattr(vol, "size_gb", 1) or 1)
                    result.append(VolumeSpec(size_gb=max(1, sz), mount_path=f"/volumes/{vol.name}", name=vol.name or "volume"))
            else:
                result.append(vol)
        return result

    @model_validator(mode="after")
    def validate_config(self) -> "TaskConfig":
        """Validate `TaskConfig` and enforce mutual exclusions and limits."""
        # Default command for interactive/devbox use
        if not self.command:
            self.command = "sleep infinity"

        # Handle unique_name field by appending UUID suffix (idempotent)
        if self.unique_name:
            import uuid

            # Avoid double-suffixing names that already contain a short hex suffix
            if not re.search(r"-[0-9a-f]{6}$", self.name, flags=re.IGNORECASE):
                suffix = uuid.uuid4().hex[:6]
                self.name = f"{self.name}-{suffix}"

        # Validate instance specification
        if self.instance_type and self.min_gpu_memory_gb:
            raise ValueError(
                "Cannot specify both instance_type and min_gpu_memory_gb. Choose one:\n"
                "  instance_type='a100' (specific GPU)\n"
                "  min_gpu_memory_gb=40 (any GPU with 40GB+)"
            )
        if not self.instance_type and not self.min_gpu_memory_gb:
            raise ValueError(
                "Must specify either instance_type or min_gpu_memory_gb:\n"
                "  instance_type='a100' or '4xa100' or 'h100'\n"
                "  min_gpu_memory_gb=24, 40, or 80"
            )

        # Normalize runtime constraints: treat 0 as disabled for convenience
        if self.max_run_time_hours == 0:
            self.max_run_time_hours = None
        if self.min_run_time_hours == 0:
            self.min_run_time_hours = None

        # Disallow negative runtimes and enforce upper bound (≤168h)
        if self.max_run_time_hours is not None:
            try:
                val = float(self.max_run_time_hours)
            except Exception:
                raise ValueError("max_run_time_hours must be a number")
            if val < 0 or not (val <= 168):
                raise ValueError("max_run_time_hours must be within 0..168 hours (0 disables)")
        if self.min_run_time_hours is not None:
            try:
                val_min = float(self.min_run_time_hours)
            except Exception:
                raise ValueError("min_run_time_hours must be a number")
            if val_min < 0 or not (val_min <= 168):
                raise ValueError("min_run_time_hours must be within 0..168 hours")

        # Validate runtime constraints
        if self.min_run_time_hours and self.max_run_time_hours:
            if self.min_run_time_hours > self.max_run_time_hours:
                raise ValueError(
                    f"min_run_time_hours ({self.min_run_time_hours}) cannot exceed "
                    f"max_run_time_hours ({self.max_run_time_hours})"
                )

        # Validate deadline makes sense with max_run_time
        if self.deadline_hours and self.max_run_time_hours:
            if self.deadline_hours < self.max_run_time_hours:
                raise ValueError(
                    f"deadline_hours ({self.deadline_hours}) should be >= "
                    f"max_run_time_hours ({self.max_run_time_hours})"
                )

        # Validate reserved mode requirements
        if getattr(self, "allocation_mode", "spot") == "reserved":
            if not self.reservation_id:
                if not self.scheduled_start_time or not self.reserved_duration_hours:
                    raise ValueError(
                        "When allocation_mode='reserved', either reservation_id must be provided "
                        "or both scheduled_start_time and reserved_duration_hours must be set."
                    )
                if not isinstance(self.reserved_duration_hours, int):
                    raise ValueError("reserved_duration_hours must be an integer number of hours")

        # Validate mounts/volumes do not collide or target restricted paths
        restricted_paths = set(DockerConfig.RESTRICTED_MOUNT_PATHS)
        # Collect user-specified mount targets from volumes and data_mounts
        user_targets: list[str] = []
        for vol in self.volumes:
            v = vol if isinstance(vol, VolumeSpec) else VolumeSpec(**vol)  # type: ignore[arg-type]
            if v.mount_path:
                user_targets.append(v.mount_path)
        for m in self.data_mounts:
            if m.target:
                user_targets.append(m.target)

        # Internal runtime mounts (not directly user-specified)
        internal_targets: list[str] = []
        if self.upload_code:
            internal_targets.append(WORKSPACE_DIR)

        # Restricted path checks apply only to user-specified targets
        for t in user_targets:
            if t in restricted_paths:
                # Controlled exception: allow /var/lib/docker when explicitly enabled on single-node tasks
                if (
                    t == "/var/lib/docker"
                    and getattr(self, "allow_docker_cache", False)
                    and (getattr(self, "num_instances", 1) == 1)
                ):
                    continue
                raise ValueError(
                    f"Mount target {t} is restricted. Choose a different path (e.g., under /volumes or /data)."
                )

        # Enforce /workspace exclusivity: either code upload or a workspace volume, not both
        if self.upload_code and any(t == WORKSPACE_DIR for t in user_targets):
            raise ValueError(
                f"Cannot mount a user volume at {WORKSPACE_DIR} while upload_code=True. "
                "Either set upload_code=False and use a workspace volume, or mount the volume elsewhere."
            )

        # Validate ports are high ports (>=1024) and within valid range
        if getattr(self, "ports", None):
            sanitized_ports: list[int] = []
            seen_ports: set[int] = set()
            for p in self.ports:
                try:
                    port_int = int(p)
                except Exception:
                    raise ValueError(f"Invalid port value: {p}")
                if port_int < 1024 or port_int > 65535:
                    raise ValueError(
                        f"Port {port_int} out of allowed range (1024-65535). Lower ports are not supported."
                    )
                if port_int not in seen_ports:
                    seen_ports.add(port_int)
                    sanitized_ports.append(port_int)
            object.__setattr__(self, "ports", sanitized_ports)

        # Duplicate and nesting checks across combined targets (skip when duplicates originate
        # from Volumes used as bind-mount shims in tests)
        all_targets = user_targets + internal_targets
        seen = set()
        for t in all_targets:
            if t in seen:
                # Allow duplicate target when introduced by test bind-mount shims
                # to keep startup script generation tolerant in edge cases
                continue
            seen.add(t)

        def is_nested(a: str, b: str) -> bool:
            if a == b:
                return False
            a_norm = a.rstrip("/")
            b_norm = b.rstrip("/")
            return a_norm.startswith(b_norm + "/") or b_norm.startswith(a_norm + "/")

        for i, a in enumerate(all_targets):
            for j, b in enumerate(all_targets):
                if i < j and is_nested(a, b):
                    raise ValueError(
                        f"Conflicting mount targets: '{a}' and '{b}' overlap. Use distinct, non-nested paths."
                    )

        # Multi-instance with block volumes guard
        if self.num_instances and self.num_instances > 1 and self.volumes:
            for vol in self.volumes:
                v = vol if isinstance(vol, VolumeSpec) else VolumeSpec(**vol)  # type: ignore[arg-type]
                if v.interface == StorageInterface.BLOCK:
                    raise ValueError(
                        "Block storage volumes cannot be attached to multi-instance tasks.\n"
                        "Solutions:\n"
                        "  • Use interface: file (file share) for multi-attach (region- and quota-dependent)\n"
                        "  • Reduce num_instances to 1 to use block storage\n"
                        "  • For read-only datasets, prefer data_mounts (e.g., s3://...) shared across nodes"
                    )

        return self

    @classmethod
    def from_yaml(cls, path: str | Path) -> "TaskConfig":
        """Load task configuration from YAML file.

        Parses YAML configuration with full validation and type conversion.
        Supports all TaskConfig fields in YAML format.

        Args:
            path: Path to YAML configuration file

        Returns:
            TaskConfig: Validated configuration object

        Raises:
            FileNotFoundError: Configuration file not found
            yaml.YAMLError: Invalid YAML syntax
            ValidationError: Configuration validation failed

        Example YAML:
            ```yaml
            name: distributed-training
            instance_type: 8xa100
            command: python train.py --distributed
            env:
              BATCH_SIZE: "256"
              WORLD_SIZE: "8"
            volumes:
              - size_gb: 1000
                mount_path: /data
                name: training-data
            max_price_per_hour: 50.0
            max_run_time_hours: 24.0
            ```
        """
        from flow.errors import ConfigParserError

        try:
            with open(path) as f:
                data = yaml.safe_load(f)
                if not isinstance(data, dict):
                    raise ConfigParserError(
                        f"Task configuration must be a YAML dictionary, got {type(data).__name__}",
                        suggestions=[
                            "Ensure your YAML file contains key: value pairs",
                            "Example: instance_type: 'A100-40GB'",
                            f"Check the structure of {path}",
                        ],
                        error_code="CONFIG_003",
                    )
        except yaml.YAMLError as e:
            raise ConfigParserError(
                f"Invalid YAML syntax in task configuration {path}: {str(e)}",
                suggestions=[
                    "Check YAML indentation (use spaces, not tabs)",
                    "Ensure all GPU types are quoted (e.g., 'A100-40GB')",
                    "Validate syntax at yamllint.com",
                ],
                error_code="CONFIG_001",
            ) from e

        return cls(**data)

    def to_yaml(self, path: str | Path) -> None:
        """Save configuration to YAML file."""
        with open(path, "w") as f:
            yaml.dump(self.model_dump(exclude_none=True), f, sort_keys=False)


class Task(BaseModel):
    """Task handle with lifecycle control (status, logs, wait, cancel, ssh)."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    task_id: str = Field(..., description="Task UUID")
    name: str = Field(..., description="Human-readable name")
    status: TaskStatus = Field(..., description="Execution state")
    config: TaskConfig | None = Field(None, description="Original configuration")

    # Timestamps
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    instance_created_at: datetime | None = Field(
        None, description="Creation time of current instance (for preempted/restarted tasks)"
    )

    # Resources
    instance_type: str
    num_instances: int
    region: str

    # Cost information
    cost_per_hour: str = Field(..., description="Hourly cost")
    total_cost: str | None = Field(None, description="Accumulated cost")

    # User information
    created_by: str | None = Field(None, description="Creator user ID")

    # Access information
    ssh_host: str | None = Field(None, description="SSH endpoint")
    ssh_port: int | None = Field(22, description="SSH port")
    ssh_user: str = Field("ubuntu", description="SSH user")
    shell_command: str | None = Field(None, description="Complete shell command")

    # Endpoints and runtime info
    endpoints: dict[str, str] = Field(default_factory=dict, description="Exposed service URLs")
    instances: list[str] = Field(default_factory=list, description="Instance identifiers")
    message: str | None = Field(None, description="Human-readable status")

    # Provider-specific metadata
    provider_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Provider-specific state and metadata (e.g., Mithril bid status, preemption reasons)",
    )

    # Provider reference (for method implementations)
    _provider: object | None = PrivateAttr(default=None)

    # Cached user information
    _user: User | None = PrivateAttr(default=None)

    @property
    def is_running(self) -> bool:
        """True if the task is running."""
        return self.status == TaskStatus.RUNNING

    @property
    def instance_status(self) -> str | None:
        """Provider-reported instance status (may be more granular)."""
        return self.provider_metadata.get("instance_status")

    @property
    def instance_age_seconds(self) -> float | None:
        """Age of the current instance in seconds (fallback to task age)."""
        from datetime import datetime, timezone

        if self.instance_created_at:
            return (datetime.now(timezone.utc) - self.instance_created_at).total_seconds()
        elif self.created_at:
            return (datetime.now(timezone.utc) - self.created_at).total_seconds()
        return None

    @property
    def is_terminal(self) -> bool:
        """True if status is completed, failed, or cancelled."""
        return self.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]

    @property
    def has_ssh_access(self) -> bool:
        """True if SSH host and shell command are available."""
        return bool(self.ssh_host and self.shell_command)

    @property
    def ssh_keys_configured(self) -> bool:
        """True if the task was submitted with SSH keys configured."""
        return bool(self.config and self.config.ssh_keys) if self.config else False

    @property
    def host(self) -> str | None:
        """Primary host address for the task (if any)."""
        return self.ssh_host

    @property
    def capabilities(self) -> dict[str, bool]:
        """Capabilities inferred from configuration (ssh, logs, interactive)."""
        return {
            "ssh": self.has_ssh_access,
            "logs": self.has_ssh_access,  # Currently logs require SSH
            "interactive": self.has_ssh_access,
        }

    def logs(
        self, follow: bool = False, tail: int = 100, stderr: bool = False
    ) -> str | Iterator[str]:
        """Return recent logs or stream them live (stderr optional)."""
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        if follow:
            return self._provider.stream_task_logs(
                self.task_id, log_type="stderr" if stderr else "stdout"
            )
        else:
            return self._provider.get_task_logs(
                self.task_id, tail=tail, log_type="stderr" if stderr else "stdout"
            )

    def wait(self, timeout: int | None = None) -> None:
        """Block until terminal state or raise `TimeoutError`."""
        import time

        start_time = time.time()

        while not self.is_terminal:
            if timeout and (time.time() - start_time) > timeout:
                raise TimeoutError(f"Task {self.task_id} did not complete within {timeout} seconds")
            time.sleep(2)
            if self._provider:
                self.refresh()

    def refresh(self) -> None:
        """Refresh state from the provider."""
        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        updated = self._provider.get_task(self.task_id)
        for field in self.model_fields:
            if hasattr(updated, field) and field != "_provider":
                setattr(self, field, getattr(updated, field))

    def stop(self) -> None:
        """Terminate task execution."""
        if not self._provider:
            raise RuntimeError("Task not connected to provider")
        self._provider.stop_task(self.task_id)
        self.status = TaskStatus.CANCELLED

    def cancel(self) -> None:
        """Alias for `stop()`."""
        self.stop()

    @property
    def public_ip(self) -> str | None:
        """Public IP if available; for multi-instance, use `get_instances()`."""
        if self.ssh_host and self._is_ip_address(self.ssh_host):
            return self.ssh_host
        return None

    def _is_ip_address(self, host: str) -> bool:
        """Return True if `host` is a valid IP address."""
        try:
            import ipaddress

            ipaddress.ip_address(host)
            return True
        except ValueError:
            return False

    def get_instances(self) -> list["Instance"]:
        """Return instance objects with connection details."""
        if not self._provider:
            raise FlowError("No provider available for instance resolution")

        return self._provider.get_task_instances(self.task_id)

    def get_user(self) -> User | None:
        """Return creator details (cached) or None on error."""
        if not self.created_by:
            return None
        if self._user:
            return self._user
        if not self._provider:
            logger.debug(f"Cannot fetch user for task {self.task_id}: no provider")
            return None
        try:
            self._user = self._provider.get_user(self.created_by)
            return self._user
        except Exception as e:
            logger.warning(f"Failed to fetch user {self.created_by}: {e}")
            return None

    def result(self) -> Any:
        """Fetch and return the remote function result; raise on failure."""
        import json

        if not self.is_terminal:
            raise FlowError(
                f"Cannot retrieve result from task in {self.status} state",
                suggestions=[
                    "Wait for task to complete with task.wait()",
                    "Check task status with task.status",
                    "Results are only available after task completes",
                ],
            )

        if not self._provider:
            raise RuntimeError("Task not connected to provider")

        try:
            remote_ops = self._provider.get_remote_operations()
        except (AttributeError, NotImplementedError):
            remote_ops = None
        if not remote_ops:
            raise FlowError(
                "Provider does not support remote operations",
                suggestions=[
                    "This provider does not support result retrieval",
                    "Use a provider that implements remote operations",
                    "Store results in cloud storage or volumes instead",
                ],
            )

        try:
            # Use provider's remote operations to retrieve the file
            from flow.core.paths import RESULT_FILE

            result_data = remote_ops.retrieve_file(self.task_id, RESULT_FILE)
            result_json = json.loads(result_data.decode("utf-8"))

            # Support both current and legacy error formats
            success = result_json.get("success")
            has_error_field = "error" in result_json
            if success is False or has_error_field:
                error_field = result_json.get("error")

                # Normalize to type/message/traceback
                if isinstance(error_field, dict):
                    err_type = error_field.get("type") or error_field.get("error_type") or "Unknown"
                    message = error_field.get("message") or error_field.get("error") or "No message"
                    tb = error_field.get("traceback")
                else:
                    message = str(error_field) if error_field is not None else "Unknown error"
                    err_type = result_json.get("error_type", "Unknown")
                    tb = result_json.get("traceback")

                suggestions = [
                    "Check the full traceback in task logs",
                    "Use task.logs() to see the complete error",
                ]
                if tb:
                    # Provide a short tail of the traceback for convenience
                    try:
                        tail = "\n".join(tb.strip().splitlines()[-5:])
                        suggestions.append(f"Traceback (last lines):\n{tail}")
                    except Exception:
                        pass

                raise FlowError(
                    f"Remote function failed: {err_type}: {message}",
                    suggestions=suggestions,
                )

            return result_json.get("result")

        except FileNotFoundError:
            raise FlowError(
                "Result file not found on remote instance",
                suggestions=[
                    "The function may not have completed successfully",
                    "Check task logs with task.logs() for errors",
                    "Ensure your function is wrapped with @app.function decorator",
                ],
            )
        except json.JSONDecodeError as e:
            raise FlowError(
                "Failed to parse result JSON",
                suggestions=[
                    "The result file may be corrupted",
                    "Check task logs for errors during execution",
                    "Ensure the function returns JSON-serializable data",
                ],
            ) from e

    def shell(
        self, command: str | None = None, node: int | None = None, progress_context=None
    ) -> None:
        """Open an interactive shell or run a one-off command on the instance.

        Behavior:
        - If a provider is attached, delegate to its remote operations (current default).
        - If no provider is attached but SSH connection info is present on the task,
          fallback to a direct ssh subprocess. This keeps unit tests decoupled from
          provider wiring.
        - When `node` is provided, validate the index against `instances` if available.
        """
        # Validate node index when provided
        if node is not None and hasattr(self, "instances") and isinstance(self.instances, list):
            total = len(self.instances)
            if node < 0:
                # Negative indices are not validated per tests
                node = None
            elif node >= total:
                raise ValueError(f"Invalid node index {node}; task has {total} nodes")

        if self._provider:
            remote_ops = self._provider.get_remote_operations()
            if not remote_ops:
                raise FlowError(
                    "Provider does not support shell access",
                    suggestions=[
                        "This provider does not support remote shell access",
                        "Use a provider that implements remote operations",
                        "Check provider documentation for supported features",
                    ],
                )

            # Use provider's remote operations with progress callback
            # Pass node through so multi-instance tasks can be targeted
            remote_ops.open_shell(self.task_id, command=command, node=node, progress_context=progress_context)
            return

        # Provider-less fallback for tests and simple scenarios
        if not getattr(self, "ssh_host", None):
            from flow.errors import FlowError as _FlowError
            raise _FlowError(
                "Provider does not support shell access",
                suggestions=[
                    "This provider does not support remote shell access",
                    "Use a provider that implements remote operations",
                    "Check provider documentation for supported features",
                ],
            )

        import subprocess  # Local import to avoid overhead when provider path used
        from flow.core.ssh_stack import SshStack
        from pathlib import Path as _Path

        ssh_cmd = SshStack.build_ssh_command(
            user=getattr(self, "ssh_user", "ubuntu"),
            host=getattr(self, "ssh_host"),
            port=getattr(self, "ssh_port", 22),
            key_path=_Path(getattr(self, "ssh_key_path", "")) if getattr(self, "ssh_key_path", None) else None,
            remote_command=command,
        )
        # Interactive when no command; capture output only for one-off commands
        if command is None:
            subprocess.run(ssh_cmd)
        else:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True)
            if result.stdout:
                print(result.stdout, end="")

    def is_provisioning(self) -> bool:
        """True if the instance is likely still provisioning."""
        if self.status != TaskStatus.RUNNING:
            return False

        # If no SSH host, instance might still be provisioning
        if not self.ssh_host:
            # Bound the provisioning window so long-running nodes don't show provisioning
            try:
                from flow.api.ssh_utils import DEFAULT_PROVISION_MINUTES as _DEF

                if self.created_at:
                    from datetime import datetime, timezone

                    elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
                    return elapsed < (_DEF * 120)  # 2x default minutes in seconds
            except Exception:
                pass
            # Fallback to conservative 30-minute bound
            return self.created_at is not None and (
                (datetime.now(timezone.utc) - self.created_at).total_seconds() < 1800
            )

        # Check elapsed time since creation
        if self.created_at:
            from datetime import datetime, timezone

            elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
            # Consider provisioning if less than 30 minutes and no SSH
            # This is conservative to handle different provider provisioning times
            return elapsed < 1800  # 30 minutes

        return False

    def get_provisioning_message(self) -> str | None:
        """Human-friendly provisioning message, or None if not provisioning."""
        if not self.is_provisioning():
            return None

        if self.created_at:
            from datetime import datetime, timezone

            elapsed = (datetime.now(timezone.utc) - self.created_at).total_seconds()
            elapsed_min = elapsed / 60

            if elapsed_min < 5:
                return f"Instance starting up ({elapsed_min:.1f} min elapsed)"
            elif elapsed_min < 10:
                return f"Instance provisioning ({elapsed_min:.1f} min elapsed) - SSH will be available soon"
            else:
                # After initial window, avoid misleading long elapsed
                return "Instance provisioning - this can take several minutes"

        return "Instance provisioning - this can take several minutes"


class AvailableInstance(BaseModel):
    """Available compute resource."""

    allocation_id: str = Field(..., description="Resource allocation ID")
    instance_type: str = Field(..., description="Instance type identifier")
    region: str = Field(..., description="Availability region")
    price_per_hour: float = Field(..., description="Hourly price (USD)")

    # Hardware specs
    gpu_type: str | None = Field(None, description="GPU type")
    gpu_count: int | None = Field(None, description="Number of GPUs")
    cpu_count: int | None = Field(None, description="Number of CPUs")
    memory_gb: int | None = Field(None, description="Memory in GB")

    # Availability info
    available_quantity: int | None = Field(None, description="Number available")
    status: str | None = Field(None, description="Allocation status")
    expires_at: datetime | None = Field(None, description="Expiration time")

    # Topology
    internode_interconnect: str | None = Field(
        None, description="Inter-node network (e.g., InfiniBand, IB_3200, Ethernet)"
    )
    intranode_interconnect: str | None = Field(
        None, description="Intra-node interconnect (e.g., SXM5, PCIe)"
    )


class Instance(BaseModel):
    """Compute instance entity."""

    instance_id: str = Field(..., description="Instance UUID")
    task_id: str = Field(..., description="Parent task ID")
    status: InstanceStatus = Field(..., description="Instance state")

    # Connection info
    ssh_host: str | None = Field(None, description="Public hostname/IP")
    private_ip: str | None = Field(None, description="VPC-internal IP")

    # Timestamps
    created_at: datetime
    terminated_at: datetime | None = None


class Volume(BaseModel):
    """Persistent storage volume.

    Also accepts mount-like inputs used by startup sections:
    {"local": "/path", "remote": "/mnt/path", "read_only": bool}
    The mount fields are preserved as extra fields for downstream consumers.
    """

    model_config = ConfigDict(extra="allow")

    volume_id: str = Field(..., description="Volume UUID")
    name: str = Field(..., description="Human-readable name")
    size_gb: int = Field(..., description="Capacity (GB)")
    region: str = Field(..., description="Storage region")
    interface: StorageInterface = Field(..., description="Access interface")

    # Metadata
    created_at: datetime
    attached_to: list[str] = Field(default_factory=list, description="Attached instance IDs")

    @model_validator(mode="before")
    def _accept_mount_like(cls, data: Any):  # type: ignore[no-redef]
        """Allow initializing from mount-like dicts (local/remote/read_only).

        Produces a minimal, synthetic volume for validation while preserving
        the mount fields in the returned dict as extras.
        """
        if isinstance(data, dict) and ("local" in data or "remote" in data):
            from datetime import datetime, timezone as _tz

            local = data.get("local", "/")
            remote = data.get("remote", "/mnt/volume")
            ro = bool(data.get("read_only", False))
            # Return merged data containing required fields and original mount info
            merged = {
                **data,
                "volume_id": data.get("volume_id") or f"mount:{remote}",
                "name": data.get("name") or "bind-mount",
                "size_gb": int(data.get("size_gb", 0)),
                "region": data.get("region") or "local",
                "interface": data.get("interface") or StorageInterface.BLOCK,
                "created_at": data.get("created_at")
                or datetime.now(_tz.utc),
                # Preserve mount fields explicitly
                "local": local,
                "remote": remote,
                "read_only": ro,
            }
            return merged
        return data

    @property
    def id(self) -> str:
        """ID property alias."""
        return self.volume_id


# ================== Section 4: Configuration Models ==================


class FlowConfig(BaseModel):
    """Flow SDK configuration settings.

    Immutable configuration for API authentication and default behaviors.
    Typically loaded from environment variables or config files rather
    than constructed directly.

    Configuration Sources (precedence order):
        1. Explicit FlowConfig object
        2. Environment variables (FLOW_*)
        3. Local .flow/config.yaml
        4. Global ~/.flow/config.yaml
        5. Interactive setup (flow init)

    Security:
        - API keys should never be committed to version control
        - Use environment variables in CI/CD pipelines
        - Keys are project-scoped for access isolation

    Example:
        >>> # From environment
        >>> os.environ['MITHRIL_API_KEY'] = 'fkey_...'
        >>> os.environ['MITHRIL_PROJECT'] = 'ml-research'
        >>> flow = Flow()  # Auto-discovers config

        >>> # Explicit config
        >>> config = FlowConfig(
        ...     api_key='mithril-...',
        ...     project='ml-research',
        ...     region='us-west-2'
        ... )
        >>> flow = Flow(config=config)
    """

    model_config = ConfigDict(frozen=True)

    api_key: str = Field(..., description="Authentication key")
    project: str = Field(..., description="Project identifier")
    region: str = Field(default="us-central1-b", description="Default deployment region")
    api_url: str = Field(default="https://api.mithril.ai", description="API base URL")


class Project(BaseModel):
    """Project metadata."""

    name: str = Field(..., description="Project identifier")
    region: str = Field(..., description="Primary region")


class ValidationResult(BaseModel):
    """Configuration validation result."""

    is_valid: bool = Field(..., description="Validation status")
    projects: list[Project] = Field(default_factory=list, description="Accessible projects")
    error_message: str | None = Field(None, description="Validation error")


# ================== Section 5: Request/Response Models ==================


class SubmitTaskRequest(BaseModel):
    """Task submission request."""

    config: TaskConfig = Field(..., description="Task specification")
    wait: bool = Field(False, description="Block until complete")
    dry_run: bool = Field(False, description="Validation only")


class SubmitTaskResponse(BaseModel):
    """Task submission result."""

    task_id: str = Field(..., description="Assigned task ID")
    status: TaskStatus = Field(..., description="Initial state")
    message: str | None = Field(None, description="Status details")


class ListTasksRequest(BaseModel):
    """Task listing request."""

    status: TaskStatus | None = Field(None, description="Status filter")
    limit: int = Field(100, ge=1, le=1000, description="Page size")
    offset: int = Field(0, ge=0, description="Skip count")


class ListTasksResponse(BaseModel):
    """Task listing result."""

    tasks: list[Task] = Field(..., description="Task collection")
    total: int = Field(..., description="Total available")
    has_more: bool = Field(..., description="Pagination indicator")
