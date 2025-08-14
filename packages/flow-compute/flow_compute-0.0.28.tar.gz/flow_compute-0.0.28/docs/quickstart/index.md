# Quickstart Hub

Choose a path. Each card gets you from zero to GPU in minutes.

-   :material-language-python: **Python SDK (recommended)**
    ---
    Direct API control with type safety and programmatic workflows.

    ```python
    import flow
    from flow import TaskConfig
    config = TaskConfig(command="python model.py", instance_type="a100")
    task = flow.run(config)
    print(task.logs())
    ```

    **Start here:**
    - [Inference](sdk/inference.md)
    - [Training](sdk/training.md)
    - [Fine-tuning](sdk/fine-tuning.md)

-   :material-console: **Command Line (SLURM compatible)**
    ---
    Familiar bash workflows. Run SLURM scripts unchanged.

    ```bash
    flow run "python train.py" --instance-type a100
    # SLURM
    flow run --slurm job.slurm
    ```

    **Start here:**
    - [SLURM migration](cli/slurm-migration.md)
    - [Inference](cli/inference.md)
    - [Training](cli/training.md)
    - [Fine-tuning](cli/fine-tuning.md)

-   :material-terraform: **Infrastructure as Code**
    ---
    Declarative deployments for platform teams and CI/CD.

    ```hcl
    resource "flow_task" "training" {
      command       = "python train.py"
      instance_type = "8xa100"
      max_price     = 20.0
    }
    ```

    **Start here:**
    - [Terraform](iac/terraform.md)
    - [Pulumi](iac/pulumi.md)
    - [Examples](iac/examples/)

-   :material-notebook-outline: **Jupyter Notebooks**
    ---
    Interactive exploration with immediate feedback.

    ```python
    %load_ext flow
    %flow run --instance-type a100 --interactive
    ```

    **Start here:**
    - [Getting started](notebook/getting-started.ipynb)
    - [Inference](notebook/inference.ipynb)
    - [Training](notebook/training.ipynb)
    - [Fine-tuning](notebook/fine-tuning.ipynb)

{: .grid .cards}

## By use case

- **Model inference**: [SDK](sdk/inference.md) · [CLI](cli/inference.md) · [IaC](iac/terraform.md#inference) · [Notebook](notebook/inference.ipynb)
- **Model training**: [SDK](sdk/training.md) · [CLI](cli/training.md) · [IaC](iac/terraform.md#training) · [Notebook](notebook/training.ipynb)
- **Fine-tuning**: [SDK](sdk/fine-tuning.md) · [CLI](cli/fine-tuning.md) · [IaC](iac/terraform.md#fine-tuning) · [Notebook](notebook/fine-tuning.ipynb)

## Instance types & pricing

| GPU Type | Memory | Use Case |
|----------|--------|----------|
| `a100` | 1×80GB | Training, fine-tuning |
| `2xa100` | 2×80GB | Medium-scale training |
| `4xa100` | 4×80GB | Distributed training |
| `8xa100` | 8×80GB | Large scale training |
| `h100` | 8×80GB | Latest architecture (8 GPUs) |

Note: All A100s are 80GB with SXM4. H100 defaults to 8× configuration.

Pricing: use `flow pricing --market` to see current availability and spot prices.

## Prerequisites

1. Install Flow: `pip install flow-compute` or see install options in [Getting Started](../getting-started/quickstart.md)
2. Configure API key: `flow init` (get a key at [app.mithril.ai/account/apikeys][api_keys])
3. Verify: `flow test-gpu`

[api_keys]: {{ WEB_BASE }}/account/apikeys

## Helpful links

- [Core concepts](../getting-started/core-concepts.md)
- [Authentication](../getting-started/authentication.md)
- [Examples]({{ REPO_BASE }}/tree/main/examples)
- [Troubleshooting](../troubleshooting/)

Ready to start? Pick a card above and launch a GPU task in minutes.