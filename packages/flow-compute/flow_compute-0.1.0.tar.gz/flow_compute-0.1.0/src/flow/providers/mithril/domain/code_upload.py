"""Code upload orchestration service.

Provides a high-level API to decide and perform code upload (embedded vs SCP)
without keeping this logic in the provider facade.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
import tarfile
import tempfile
import base64

from flow.api.models import Task, TaskConfig
from flow.providers.mithril.code_transfer import CodeTransferConfig, CodeTransferManager


class CodeUploadPlan:
    def __init__(self, use_scp: bool) -> None:
        self.use_scp = use_scp


class CodeUploadService:
    def __init__(self, provider) -> None:
        self._provider = provider
        self._logger = logging.getLogger(__name__)

    def plan(self, config: TaskConfig) -> CodeUploadPlan:
        strategy = (getattr(config, "upload_strategy", None) or "embedded").lower()
        use_scp = strategy in {"scp", "rsync", "ssh"}
        return CodeUploadPlan(use_scp=use_scp)

    def maybe_package_embedded(self, config: TaskConfig) -> TaskConfig:
        # Package via service to avoid duplication in provider
        return self.package_local_code(config)

    def initiate_async_upload(self, task: Task, config: TaskConfig) -> None:
        manager = CodeTransferManager(provider=self._provider)
        # Fire-and-forget in background via provider public helper
        self._provider.start_background_code_upload(manager, task, CodeTransferConfig())

    # -------- strategy decisions --------
    def should_use_scp_upload(self, config: TaskConfig) -> bool:
        """Determine if SCP upload should be used instead of embedded."""
        # Explicit strategy wins
        try:
            if getattr(config, "upload_strategy", None) == "scp":
                return True
            if getattr(config, "upload_strategy", None) in ["embedded", "none"]:
                return False
        except Exception:
            pass

        # Auto mode - estimate compressed size
        try:
            try:
                code_root_value = getattr(config, "code_root", None)
            except Exception:
                code_root_value = None
            cwd = Path(code_root_value) if code_root_value else Path.cwd()

            total_size = 0
            file_count = 0

            # Use provider's helper via public wrapper to stay consistent with CLI
            try:
                excludes = self._provider.get_exclude_patterns(cwd)  # type: ignore[attr-defined]
            except AttributeError:
                # Fallback for older provider versions without the public API
                excludes = getattr(self._provider, "_get_exclude_patterns")(cwd)

            for root, dirs, files in os.walk(cwd):
                # Skip excluded directories
                dirs[:] = [d for d in dirs if not any(Path(root, d).match(p) for p in excludes)]

                for file in files:
                    file_path = Path(root) / file
                    if any(file_path.match(p) for p in excludes):
                        continue
                    try:
                        total_size += file_path.stat().st_size
                        file_count += 1
                    except OSError:
                        continue

            estimated_compressed = total_size * 0.4  # heuristic
            if estimated_compressed > 8 * 1024:  # > 8KB
                self._logger.info(
                    f"Auto-selected SCP upload: {file_count} files, ~{estimated_compressed / 1024:.1f}KB compressed"
                )
                return True
            else:
                self._logger.info(
                    f"Auto-selected embedded upload: {file_count} files, ~{estimated_compressed / 1024:.1f}KB compressed"
                )
                return False
        except Exception as e:
            self._logger.warning(f"Error estimating project size: {e}. Using embedded upload.")
            return False

    # -------- embedded packaging --------
    def package_local_code(self, config: TaskConfig) -> TaskConfig:
        """Create gzipped tar archive and embed into config env as base64."""
        # Resolve code root (defaults to CWD)
        try:
            code_root_value = getattr(config, "code_root", None)
        except Exception:
            code_root_value = None
        cwd = Path(code_root_value) if code_root_value else Path.cwd()

        # Create excludes list
        excludes: set[str] = {
            ".git",
            "__pycache__",
            "*.pyc",
            ".env",
            ".venv",
            "venv",
            "node_modules",
            ".DS_Store",
            "*.log",
            ".pytest_cache",
            ".mypy_cache",
            ".tox",
            ".coverage",
            "htmlcov",
            ".idea",
            ".vscode",
            "*.egg-info",
            "dist",
            "build",
        }

        # Check for .flowignore file
        flowignore_path = cwd / ".flowignore"
        if flowignore_path.exists():
            try:
                with flowignore_path.open() as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            excludes.add(line)
            except Exception:
                pass

        # Collect files
        files_to_package: list[Path] = []
        for root, dirs, files in os.walk(cwd):
            root_path = Path(root)
            # Filter directories
            dirs[:] = [d for d in dirs if not any((root_path / d).match(p) for p in excludes)]
            for file in files:
                file_path = root_path / file
                if not any(file_path.match(pattern) for pattern in excludes):
                    files_to_package.append(file_path)

        if not files_to_package:
            self._logger.info("No files to upload (empty directory or all files excluded)")
            return config

        # Create archive and embed
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp_file:
            try:
                with tarfile.open(tmp_file.name, "w:gz") as tar:
                    for file_path in files_to_package:
                        rel_path = file_path.relative_to(cwd)
                        tar.add(file_path, arcname=str(rel_path))

                size_bytes = os.path.getsize(tmp_file.name)
                size_mb = size_bytes / (1024 * 1024)
                self._logger.info(f"Code archive size: {size_mb:.2f}MB")

                if size_mb > 10:  # 10MB limit
                    self._logger.info(
                        f"Project size {size_mb:.1f}MB exceeds embedded limit (10MB). Falling back to upload_strategy='scp'"
                    )
                    try:
                        return config.model_copy(update={"upload_strategy": "scp"})
                    except Exception:
                        return config

                with open(tmp_file.name, "rb") as f:
                    code_archive = base64.b64encode(f.read()).decode("ascii")

                updated_env = dict(getattr(config, "env", {}) or {})
                updated_env["_FLOW_CODE_ARCHIVE"] = code_archive
                try:
                    return config.model_copy(update={"env": updated_env})
                except Exception:
                    # Best-effort – return original if cloning fails
                    return config
            finally:
                try:
                    os.unlink(tmp_file.name)
                except Exception:
                    pass
