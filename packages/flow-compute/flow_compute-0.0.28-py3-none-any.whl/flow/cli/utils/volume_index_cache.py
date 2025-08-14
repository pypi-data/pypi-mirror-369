"""Volume index cache for quick volume references.

Provides ephemeral index-based volume references (e.g., 1, 2; legacy :1, :2) based on the
last shown volume list. Behavior is explicit and time-bounded to prevent stale
references.
"""

import json
import time
from pathlib import Path

from flow.api.models import Volume


class VolumeIndexCache:
    """Manages ephemeral volume index mappings.

    Stores mappings from display indices to volume IDs, allowing users
    to reference volumes by position (e.g., :1, :2) from the last volume
    list display. Indices expire after 5 minutes to prevent stale references.
    """

    CACHE_TTL_SECONDS = 300  # 5 minutes

    def _current_context(self) -> str | None:
        """Return a context string to scope cache entries.

        Best-effort: use the prefetch context when available; otherwise None.
        """
        try:
            from flow.cli.utils.prefetch import _context_prefix  # type: ignore

            return _context_prefix()
        except Exception:
            return None

    def __init__(self, cache_dir: Path | None = None):
        """Initialize cache with optional custom directory.

        Args:
            cache_dir: Directory for cache file (defaults to ~/.flow)
        """
        self.cache_dir = cache_dir or Path.home() / ".flow"
        self.cache_file = self.cache_dir / "volume_indices.json"

    def save_indices(self, volumes: list[Volume]) -> None:
        """Save volume indices from a displayed list.

        Args:
            volumes: Ordered list of volumes as displayed
        """
        # Create directory if needed
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Build index mapping (1-based for user friendliness)
        indices = {str(i + 1): volume.id for i, volume in enumerate(volumes)}

        # Cache full volume details for instant access
        volume_details = {}
        for volume in volumes:
            volume_details[volume.id] = {
                "id": volume.id,
                "name": volume.name,
                "region": volume.region,
                "size_gb": volume.size_gb,
                "interface": getattr(volume, "interface", "block"),
                "created_at": volume.created_at.isoformat() if volume.created_at else None,
            }

        cache_data = {
            "indices": indices,
            "volume_details": volume_details,
            "timestamp": time.time(),
            "volume_count": len(volumes),
            # Scope on-disk indices to current provider/project context when known
            "context": self._current_context(),
        }

        # Atomic write
        temp_file = self.cache_file.with_suffix(".tmp")
        temp_file.write_text(json.dumps(cache_data, indent=2))
        temp_file.replace(self.cache_file)

    def resolve_index(self, index_str: str) -> tuple[str | None, str | None]:
        """Resolve an index reference to a volume ID.

        Args:
            index_str: Index string (e.g., "1", ":1")

        Returns:
            Tuple of (volume_id if found, error message if any)
        """
        # Parse index
        if index_str.startswith(":"):
            raw = index_str[1:]
        else:
            raw = index_str

        try:
            index = int(raw)
        except ValueError:
            return None, f"Invalid index format: {index_str}"

        if index < 1:
            return None, "Index must be positive"

        # Load cache
        cache_data = self._load_cache()
        if not cache_data:
            return None, "No recent volume list. Run 'flow volumes list' first"

        # Check if expired
        age = time.time() - cache_data["timestamp"]
        if age > self.CACHE_TTL_SECONDS:
            return None, "Volume indices expired. Run 'flow volumes list' to refresh"

        # Look up index
        volume_id = cache_data["indices"].get(str(index))
        if not volume_id:
            max_index = cache_data["volume_count"]
            return None, f"Index {index} out of range (1-{max_index})"

        return volume_id, None

    def _load_cache(self) -> dict | None:
        """Load cache data if valid.

        Returns:
            Cache data dict or None if not found/invalid
        """
        if not self.cache_file.exists():
            return None

        try:
            data = json.loads(self.cache_file.read_text())
            try:
                saved_ctx = data.get("context")
                curr_ctx = self._current_context()
                if saved_ctx is not None and curr_ctx is not None and saved_ctx != curr_ctx:
                    return None
            except Exception:
                pass
            return data
        except (json.JSONDecodeError, KeyError):
            # Invalid cache file
            return None

    def get_cached_volume(self, volume_id: str) -> dict | None:
        """Get cached volume details if available.

        Args:
            volume_id: Volume ID to look up

        Returns:
            Volume details dict or None if not cached/expired
        """
        cache_data = self._load_cache()
        if not cache_data:
            return None

        # Check if expired
        age = time.time() - cache_data["timestamp"]
        if age > self.CACHE_TTL_SECONDS:
            return None

        return cache_data.get("volume_details", {}).get(volume_id)

    def clear(self) -> None:
        """Clear the index cache."""
        if self.cache_file.exists():
            self.cache_file.unlink()
