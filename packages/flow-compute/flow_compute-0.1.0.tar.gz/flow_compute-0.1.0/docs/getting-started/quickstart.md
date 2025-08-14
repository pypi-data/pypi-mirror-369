# Quickstart

Run your first GPU job in under 3 minutes. Choose SDK or CLI and follow three steps.

## 1) Install

=== "uv (recommended)"

    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    uv tool install flow-compute
    ```

=== "pipx"

    ```bash
    pipx install flow-compute
    ```

=== "One-liner (macOS/Linux)"

    ```bash
    curl -fsSL https://raw.githubusercontent.com/mithrilcompute/flow/main/scripts/install.sh | sh
    ```

## 2) Configure

```bash
flow init
```

Get an API key at [app.mithril.ai/account/apikeys][api_keys].

[api_keys]: {{ WEB_BASE }}/account/apikeys

## 3) Run on GPU

=== "Python SDK"

    ```python
    import flow
    task = flow.run("nvidia-smi", instance_type="a100")
    print(task.task_id)
    ```

=== "CLI"

    ```bash
    flow run "nvidia-smi" --instance-type a100
    ```

---

### Verify (optional)

```bash
flow status              # List tasks
flow logs TASK_ID        # Stream logs
flow cancel TASK_ID      # Cancel if needed
```

??? details "Full GPU test example (PyTorch)"
    Save as `gpu_test.py` and run via SDK or CLI.

    ```python
    import torch

    if torch.cuda.is_available():
        gpu = torch.cuda.get_device_name(0)
        mem_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU: {gpu} ({mem_gb:.1f} GB)")
        x = torch.randn(5000, 5000, device="cuda")
        y = torch.randn(5000, 5000, device="cuda")
        z = torch.matmul(x, y)
        print(z.shape)
    else:
        print("No GPU found")
    ```

    ```python
    # SDK
    from flow import TaskConfig
    config = TaskConfig(command="python gpu_test.py", instance_type="a100", max_price_per_hour=10.0)
    task = flow.run(config)
    task.wait()
    print(task.logs())
    ```

    ```bash
    # CLI
    flow run "python gpu_test.py" --instance-type a100 --max-price-per-hour 10
    ```

---

## Cost control (strongly recommended)

Always set limits.

```python
from flow import TaskConfig
TaskConfig(
    command="python train.py",
    instance_type="a100",
    max_price_per_hour=10.0,
    max_run_time_hours=24.0,
)
```

---

## Next steps

- [Python SDK quickstarts](../quickstart/sdk/inference.md) – Inference, training, fine-tuning
- [CLI quickstarts](../quickstart/cli/inference.md) – Command-line workflows
- [IaC quickstarts](../quickstart/iac/terraform.md) – Terraform/Pulumi
- [Interactive notebooks](../quickstart/notebook/getting-started.ipynb) – Jupyter tutorials

More:
- [Authentication](authentication.md)
- [Core concepts](core-concepts.md)
- [Examples]({{ REPO_BASE }}/tree/main/examples)

---

## Troubleshooting (common quick fixes)

??? details "No instances available"
    Try a different instance type (e.g., `a10g`), raise `max_price_per_hour`, or choose another region.

??? details "Task stays pending"
    Check instance availability (`flow pricing --market`), quota, and API permissions.

??? details "Import errors"
    Ensure Python ≥ 3.10, `flow-compute` is installed, and you are using `import flow`.