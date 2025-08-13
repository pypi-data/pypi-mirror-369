## JuiceFS-based universal multi-cloud fileshare on block storage

This design proposes a universal, cross-region file share for Mithril that works in any region/cloud by layering JuiceFS over an S3-compatible object store that itself runs on block storage volumes. It integrates cleanly with Mithril startup scripts via a dedicated `JuiceFSSection` and uses an explicit, environment-driven configuration.

### Goals
- Provide a consistent POSIX fileshare in all regions (even where native fileshares are unavailable) and across clouds.
- Keep the solution cloud-agnostic with predictable performance knobs.
- Minimize operational complexity in the common path; support advanced replication for multi-region scenarios.

### Non-goals
- Directly mounting raw block devices as a distributed FS via JuiceFS (JuiceFS expects an object storage backend).
- Replacing specialized high-performance filesystems like Weka where already available.

---

### Architecture

1) Object storage layer (per region)
- Deploy an S3-compatible object store (e.g., MinIO, Ceph RGW) backed by regional block volumes.
- Recommended: erasure coding, versioning on; enable bucket replication between regions when multi-region is required.

2) Metadata layer
- JuiceFS CE supports multiple metadata engines (e.g., Redis). For availability and latency, run the metadata close to clients (e.g., Redis + Sentinel in-region).
- For globally writable single volume, expect cross-region metadata latency. Alternative: per-region volumes with object replication.

3) Clients
- Hosts mount JuiceFS; bind mount into containers as needed. Use local NVMe for JuiceFS cache.

Modes
- A. Single global volume: one metadata endpoint; object storage replicated across regions. Simpler, higher metadata latency for remote regions.
- B. Per-region volumes: metadata local to each region; objects replicated across regions (via MinIO/ceph replication or `juicefs sync`). Lower latency; eventual consistency across regions.

---

### Mithril integration

Add a new startup script section: `JuiceFSSection` (priority 36–38; after volumes/S3, before Docker). Responsibilities:
- Ensure fuse and `juicefs` binary availability.
- Write `user_allow_other` to `/etc/fuse.conf`.
- Optionally `format` the volume once (leader-gated) if missing.
- Mount the volume to a configured mountpoint; keep it alive (systemd optional).
- Expose the host mountpoint to containers using the existing volume binding path.

Environment schema (explicit and minimal):
- Required:
  - `JFS_ENABLE=1`
  - `JFS_NAME` (JuiceFS volume name)
  - `JFS_MOUNTPOINT=/mnt/jfs`
  - `JFS_META=redis://host:6379/1` (or other supported metadata URL)
  - `JFS_STORAGE=s3`
  - `JFS_ENDPOINT=http://minio:9000`
  - `JFS_BUCKET=my-bucket`
  - `JFS_ACCESS_KEY`, `JFS_SECRET_KEY`
- Optional:
  - `JFS_FORMAT_IF_MISSING=1`
  - `JFS_CACHE_DIR=/var/cache/juicefs`
  - `JFS_CACHE_SIZE=100GB`
  - `JFS_MOUNT_OPTS="-o writeback,cache-size=${JFS_CACHE_SIZE},allow_other"`
  - `JFS_SYSTEMD=1` (create a unit for persistence across reboot)

Rendered script outline:
```bash
# Ensure dependencies
${ENSURE_FUSE}
${ENSURE_CURL}
if ! command -v juicefs >/dev/null 2>&1; then
  curl -fsSL "${JFS_URL:-https://juicefs.com/static/juicefs}" -o /usr/local/bin/juicefs && chmod +x /usr/local/bin/juicefs
fi
echo 'user_allow_other' >> /etc/fuse.conf || true

# Format once if missing
if [ "${JFS_FORMAT_IF_MISSING:-0}" = "1" ]; then
  if ! juicefs status "${JFS_NAME}" >/dev/null 2>&1; then
    juicefs format \
      --storage "${JFS_STORAGE}" \
      --bucket "${JFS_ENDPOINT}/${JFS_BUCKET}" \
      --access-key "${JFS_ACCESS_KEY}" \
      --secret-key "${JFS_SECRET_KEY}" \
      "${JFS_META}" "${JFS_NAME}"
  fi
fi

mkdir -p "${JFS_MOUNTPOINT}"
juicefs mount ${JFS_MOUNT_OPTS:- -o allow_other} "${JFS_NAME}" "${JFS_MOUNTPOINT}"
mountpoint -q "${JFS_MOUNTPOINT}" || { echo "JuiceFS mount failed"; exit 1; }
```

Section placement
- Insert `JuiceFSSection` into the Mithril startup builder with priority between `S3Section (35)` and `DockerSection (~40)` so the mount is ready before container start.

---

### Cross-region replication strategy

Preferred: replicate at the object-storage layer.
- MinIO/ceph RGW bucket replication across regions/clouds is mature, async, and decouples clients from replication concerns.
- For CE-only or no provider features: schedule `juicefs sync` between buckets. Expect eventual consistency and plan conflict policy accordingly.

Metadata placement
- Keep metadata close to clients. For global RW, latency can dominate; consider per-region volumes when low latency is required.

---

### Operations

Performance
- Enable writeback and large local cache on NVMe (`JFS_CACHE_DIR`, `JFS_CACHE_SIZE`).
- Tune concurrency flags (e.g., `--max-uploads`) in `JFS_MOUNT_OPTS`.

Reliability
- Optionally manage mount with systemd (`JFS_SYSTEMD=1`). Restart-on-failure; set `KillMode=process`.

Security
- Do not bake credentials into scripts; inject via env/secret store. Use TLS for the MinIO endpoint.

Container integration
- Host mount (`/mnt/jfs`) is bind-mounted into containers using existing volume bindings.

---

### Example: Minimal env
```bash
JFS_ENABLE=1
JFS_NAME=flowfs
JFS_MOUNTPOINT=/mnt/jfs
JFS_META=redis://redis.mycluster:6379/1
JFS_STORAGE=s3
JFS_ENDPOINT=https://minio.region.example.com
JFS_BUCKET=flow-bucket
JFS_ACCESS_KEY=...
JFS_SECRET_KEY=...
JFS_FORMAT_IF_MISSING=1
JFS_CACHE_DIR=/var/cache/juicefs
JFS_CACHE_SIZE=100GB
```

---

### Rollout plan
- Phase 1: Implement `JuiceFSSection`, docs, and an example config; test single-region with MinIO.
- Phase 2: Add object replication docs and per-region guidance; validate with multi-region smoke tests.
- Phase 3: Optional `MinIOSection` for dev-only bootstrap; production uses IAC for MinIO clusters.

### Risks and mitigations
- Cross-region metadata latency: prefer per-region volumes when needed.
- Credentials sprawl: enforce secret injection and scope-limited tokens.
- Kernel/FUSE variations: ensure distro-agnostic install and runtime checks in section.


