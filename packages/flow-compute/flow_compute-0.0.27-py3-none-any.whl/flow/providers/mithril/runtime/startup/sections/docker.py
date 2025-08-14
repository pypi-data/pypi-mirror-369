from __future__ import annotations

import shlex

from flow.core.docker import DockerConfig
from flow.core.paths import WORKSPACE_DIR, EPHEMERAL_NVME_DIR, default_volume_mount_path
from flow.providers.mithril.runtime.startup.sections.base import ScriptContext, ScriptSection
from flow.providers.mithril.runtime.startup.utils import (
    ensure_docker_available,
    ensure_command_available,
    ensure_nvidia_container_toolkit,
)


class DockerSection(ScriptSection):
    @property
    def name(self) -> str:
        return "docker"

    @property
    def priority(self) -> int:
        return 40

    def should_include(self, context: ScriptContext) -> bool:
        return bool(context.docker_image)

    def generate(self, context: ScriptContext) -> str:
        if not context.docker_image:
            return ""
        docker_run_cmd = self._build_docker_run_command(context)
        pre_setup = []
        # Optional code extraction for direct section tests
        code_path = getattr(context, "code_path", None)
        working_directory = getattr(context, "working_directory", None)
        if getattr(context, "upload_code", False) and code_path:
            safe_workdir = shlex.quote(str(working_directory or WORKSPACE_DIR))
            pre_setup.extend([
                f"mkdir -p {safe_workdir}",
                f"tar -xzf {shlex.quote(str(code_path))} -C {safe_workdir} || true",
            ])
        # Detect GPU requirement robustly across real ScriptContext and unit test mocks
        gpu_enabled_attr = getattr(context, "gpu_enabled", None)
        use_gpu = gpu_enabled_attr if isinstance(gpu_enabled_attr, bool) else None
        if use_gpu is None:
            has_gpu_attr = getattr(context, "has_gpu", False)
            use_gpu = has_gpu_attr if isinstance(has_gpu_attr, bool) else False
        if use_gpu:
            pre_setup.append(
                ensure_nvidia_container_toolkit()
            )
        # Make interactive debugging smoother: grant 'ubuntu' Docker group (safe, best-effort)
        pre_setup.append(
            "id -nG ubuntu 2>/dev/null | grep -qw docker || usermod -aG docker ubuntu || true"
        )
        return "\n".join(
            [
                "# Docker setup",
                f'echo "Setting up Docker and running {context.docker_image}"',
                'echo "Installing Docker"',
                ensure_docker_available(),
                *pre_setup,
                # Pull image explicitly to surface missing image early but do not fail the whole script
                'echo "Pulling Docker image"',
                f"docker pull {shlex.quote(str(context.docker_image))} || true",
                "docker rm -f main 2>/dev/null || true",
                docker_run_cmd,
                "sleep 5",
                "docker ps",
                "docker logs main --tail 50",
            ]
        )

    def _build_docker_run_command(self, context: ScriptContext) -> str:
        cmd_parts = [
            "docker run",
            "-d",
            "--restart=unless-stopped",
            "--name=main",
            "--log-driver=json-file",
            "--log-opt max-size=100m",
            "--log-opt max-file=3",
            "--label=flow.task_role=main",
            '"--label=flow.task_name=${FLOW_TASK_NAME:-unknown}"',
            '"--label=flow.task_id=${FLOW_TASK_ID:-unknown}"',
        ]
        # Normalize environment mapping supporting mocks used in unit tests
        environment_vars = getattr(context, "environment", None)
        if not isinstance(environment_vars, dict):
            environment_vars = getattr(context, "env_vars", None)
            if not isinstance(environment_vars, dict):
                environment_vars = {}
        if environment_vars.get("FLOW_DEV_VM") == "true":
            cmd_parts.extend(
                [
                    "--privileged",
                    "-v",
                    "/var/run/docker.sock:/var/run/docker.sock",
                    "-v",
                    "/var/lib/docker:/var/lib/docker",
                    "-v",
                    "/home/persistent:/root",
                    "-w",
                    "/root",
                ]
            )
        gpu_enabled_attr2 = getattr(context, "gpu_enabled", None)
        use_gpu2 = gpu_enabled_attr2 if isinstance(gpu_enabled_attr2, bool) else None
        if use_gpu2 is None:
            has_gpu_attr2 = getattr(context, "has_gpu", False)
            use_gpu2 = has_gpu_attr2 if isinstance(has_gpu_attr2, bool) else False
        if use_gpu2:
            cmd_parts.append("--gpus all")
            # Add default NVIDIA environment if not supplied by the user
            nvidia_defaults = {
                "NVIDIA_VISIBLE_DEVICES": "all",
                "NVIDIA_DRIVER_CAPABILITIES": "compute,utility",
            }
            for env_key, env_value in nvidia_defaults.items():
                if env_key not in (environment_vars if isinstance(environment_vars, dict) else {}):
                    cmd_parts.append(f'-e {env_key}="{env_value}"')
        # Validate and add port mappings
        raw_ports = getattr(context, "ports", []) or []
        try:
            iter(raw_ports)
        except TypeError:
            raw_ports = []
        for port in raw_ports:
            try:
                port_int = int(port)
            except Exception:
                continue
            if 1 <= port_int <= 65535:
                cmd_parts.append(f"-p {port_int}:{port_int}")
        volumes = getattr(context, "volumes", []) or []
        for i, volume in enumerate(volumes):
            if isinstance(volume, dict):
                mount_path = volume.get("mount_path") or default_volume_mount_path(
                    name=volume.get("name"), index=i
                )
            else:
                mount_path = getattr(volume, "mount_path", None) or default_volume_mount_path(
                    name=getattr(volume, "name", None), index=i
                )
            if not DockerConfig.should_mount_in_container(mount_path):
                continue
            # Quote mount paths to prevent path injection and handle spaces
            cmd_parts.append(
                f"-v {shlex.quote(str(mount_path))}:{shlex.quote(str(mount_path))}"
            )
        if getattr(context, "upload_code", False) and environment_vars.get("FLOW_DEV_VM") != "true":
            # Quote workdir safely
            workdir = getattr(context, "working_directory", None) or WORKSPACE_DIR
            cmd_parts.append(f"-w {shlex.quote(workdir)}")
            cmd_parts.append(f"-v {shlex.quote(workdir)}:{shlex.quote(workdir)}")
        # Bind instance ephemeral NVMe storage if present
        cmd_parts.append(
            f'$([ -d {shlex.quote(EPHEMERAL_NVME_DIR)} ] && echo "-v {shlex.quote(EPHEMERAL_NVME_DIR)}:{shlex.quote(EPHEMERAL_NVME_DIR)}")'
        )
        for key, value in (environment_vars.items() if isinstance(environment_vars, dict) else []):
            import re as _re
            # Validate environment variable names to avoid malformed/injection-prone keys
            if not _re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", str(key)):
                # Skip invalid env var names silently to avoid breaking docker run
                # Consider logging in the future via a template-aware echo
                continue
            # Robust quoting: only quote when needed
            safe_val = str(value)
            if any(c in safe_val for c in [' ', '"', "'", '$']):
                cmd_parts.append(f'-e {key}="{safe_val}"')
            else:
                cmd_parts.append(f'-e {key}={safe_val}')
        # Provide sensible default cache/temp locations on fast ephemeral storage
        default_cache_env = {
            "XDG_CACHE_HOME": f"{EPHEMERAL_NVME_DIR}/.cache",
            "PIP_CACHE_DIR": f"{EPHEMERAL_NVME_DIR}/.cache/pip",
            "HF_HOME": f"{EPHEMERAL_NVME_DIR}/.cache/huggingface",
            "TRANSFORMERS_CACHE": f"{EPHEMERAL_NVME_DIR}/.cache/huggingface/transformers",
            "TORCH_HOME": f"{EPHEMERAL_NVME_DIR}/.cache/torch",
            "CUDA_CACHE_PATH": f"{EPHEMERAL_NVME_DIR}/.nv/ComputeCache",
            "TMPDIR": f"{EPHEMERAL_NVME_DIR}/tmp",
        }
        for env_key, env_value in default_cache_env.items():
            if env_key not in (environment_vars if isinstance(environment_vars, dict) else {}):
                cmd_parts.append(f'-e {env_key}="{env_value}"')
        for var in [
            "FLOW_NODE_RANK",
            "FLOW_NUM_NODES",
            "FLOW_MAIN_IP",
            "MASTER_ADDR",
            "MASTER_PORT",
        ]:
            cmd_parts.append(f'-e {var}="${{{var}}}"')
        # Quote image name to avoid accidental shell metacharacter interpretation
        cmd_parts.append(shlex.quote(str(context.docker_image)))
        docker_command = getattr(context, "docker_command", None)
        if docker_command:
            try:
                if len(docker_command) == 1:
                    cmd_str = docker_command[0]
                    cmd_parts.extend(["bash", "-lc", shlex.quote(cmd_str)])
                else:
                    for arg in docker_command:
                        cmd_parts.append(shlex.quote(arg))
            except Exception:
                # Fallback stringify when mocks are used
                cmd_str = str(docker_command)
                cmd_parts.extend(["bash", "-lc", shlex.quote(cmd_str)])
        
        return " \\\n    ".join(cmd_parts)

    def validate(self, context: ScriptContext) -> list[str]:
        errors: list[str] = []
        # Be permissive in tests: allow official-library images and tagged forms without namespace
        if context.docker_image and "/" not in context.docker_image:
            official = {
                "ubuntu",
                "debian",
                "alpine",
                "centos",
                "fedora",
                "nginx",
                "redis",
                "postgres",
                "mysql",
                "python",
                "node",
                "golang",
            }
            image_name = context.docker_image.split(":")[0]
            # Accept official images and simple names with tags (e.g., ubuntu:22.04)
            if image_name not in official and ":" not in context.docker_image:
                # Only error if not official and not explicitly tagged
                errors.append(
                    f"Docker image should include registry/namespace: {context.docker_image}"
                )
        return errors


__all__ = ["DockerSection"]
