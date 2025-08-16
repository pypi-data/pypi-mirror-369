<div align="center">

# Megatron Bridge

<!-- [![codecov](https://codecov.io/github/NVIDIA-NeMo/Megatron-Bridge/graph/badge.svg?token=4NMKZVOW2Z)](https://codecov.io/github/NVIDIA-NeMo/Megatron-Hub) -->
[![CICD NeMo](https://github.com/NVIDIA-NeMo/Megatron-Bridge/actions/workflows/cicd-main.yml/badge.svg)](https://github.com/NVIDIA-NeMo/Megatron-Bridge/actions/workflows/cicd-main.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/release/python-3100/)
<!-- [![GitHub Stars](https://img.shields.io/github/stars/NVIDIA-NeMo/Megatron-Bridge.svg?style=social&label=Star&maxAge=2592000)](https://github.com/NVIDIA-NeMo/Megatron-Bridge/stargazers/) -->

[Documentation](https://nemo-framework-documentation.gitlab-master-pages.nvidia.com/megatron-bridge-build/) | [Recipes](#supported-models) | [Examples](https://github.com/NVIDIA-NeMo/Megatron-Bridge/tree/main/examples) | [Contributing](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/CONTRIBUTING.md)
</div>

## Overview

Megatron Bridge is an extension of NVIDIA's Megatron Core library that enables pretraining and finetuning HuggingFace models using a performant and scalable training loop, with features like model parallelisms and FP8 precision.

Megatron Bridge is designed for researchers and engineers who need to train large-scale models efficiently while maintaining flexibility for experimentation and customization.

## 🔧 Installation

For quick exploration of Megatron-Bridge, we recommend installing our pip package:

```bash
pip install megatron-bridge
```

### 📦 Pip install with TransformerEngine support

For TransformerEngine support, the following system requirements need to be fulfilled:

- Python 3.12
- PyTorch 2.7
- CUDA 12.8
- Ubuntu 24.04

Use the following to install Megatron-Bridge with TransformerEngine:

```bash
pip install torch setuptools pybind11 wheel_stub  # Required for TE
pip install --no-build-isolation megatron-bridge[te]
```

### 🐳 NeMo-FW container

Best experience, highest performance and full feature support is guaranteed by the [NeMo Framework container](https://catalog.ngc.nvidia.com/orgs/nvidia/containers/nemo/tags). Please fetch the most recent $TAG and run the following command to start a container:

```bash
docker run --rm -it -w /workdir -v $(pwd):/workdir \
  --entrypoint bash \
  --gpus all \
  nvcr.io/nvidia/nemo:${TAG}
```

### uv

For installing Megatron-Bridge with uv, please refer to our [Contribution guide](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/CONTRIBUTING.md)

## 🚀 Key Features

- **Model Conversion**: Seamless bidirectional conversion between Hugging Face and Megatron formats for interoperability
- **Training Infrastructure**: Configurable training loop with near linear performance scalability to thousands of nodes that handles data loading, distributed training, checkpointing, and logging
- **Parameter-Efficient Finetuning**: PEFT implementation tailored for Megatron-based models that supports LoRA, DoRA, and user-defined PEFT methods
- **Training Recipes**: Pre-configured production-ready training recipes for popular models like Llama 3, with optimized hyperparameters and distributed training configuration
- **Performance Optimization**: Built-in support for FP8 training, model parallelisms, and memory-efficient techniques

## Supported Models

Megatron Hub provides out-of-the-box recipes for a wide range of models, built on top of base model architectures from Megatron Core:

### Large Language Models

| Model                  | Style     | Sizes     | Pretrain     | Finetune     |
|------------------------|-----------|-----------|--------------|--------------|
| Llama 3                | [GPT](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/models/gpt_provider.py)       | [8b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama3_8b.py), [70b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama3_70b.py)   | ✅ | ❌ |
| Llama 3.1              | [GPT](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/models/gpt_provider.py)       | [8b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama31_8b.py), [70b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama31_70b.py), [405b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama31_405b.py)    | ✅ | ❌ |
| Llama 3.2              | [GPT](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/models/gpt_provider.py)       | [1b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama32_1b.py), [3b](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/src/megatron/bridge/recipes/llama/llama32_3b.py)           | ✅ | ❌ |

#### Launching Recipes

All recipes are ready to train out of the box, using mock data by default. For an example of how to override the default configuration through YAML or Hydra-style CLI overrides, please have a look at this [script](https://github.com/NVIDIA-NeMo/Megatron-Bridge/examples/recipes/llama3_8b/pretrain_llama3_8b.py). The script can then be launched with `torchrun`. For example, with the aforementioned script:

```sh
torchrun --nproc-per-node=2 pretrain_llama3_8b.py model.tensor_model_parallel_size=1 <additional overrides ...>
```

Optionally, Megatron Bridge also supports launching with [NeMo-Run](https://github.com/NVIDIA-NeMo/Run). See the following examples for reference on launching with NeMo-Run:

- [pretrain_llama3_8b_nemo_run_script.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/examples/recipes/llama3_8b/pretrain_llama3_8b_nemo_run_script.py)
- [pretrain_llama3_8b_nemo_run_partial.py](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/examples/recipes/llama3_8b/pretrain_llama3_8b_nemo_run_partial.py)

These examples can also be run as is with the Llama 3 8b recipe (with NeMo-Run installed).

Launch Llama 3 8b Pretraining with NeMo-Run's `run.Script`:

```sh
uv run python pretrain_llama3_8b_nemo_run_script.py \
    --nproc-per-node=2 \
    model.pipeline_model_parallel_size=1 \
    train.train_iters=10 # this script passes Hydra-style overrides to the target script
```

Launch Llama 3 8b Pretraining with NeMo-Run's `run.Partial`

```sh
uv run python pretrain_llama3_8b_nemo_run_partial.py \
    --nproc-per-node=2
```

<!-- ### Vision-Language Models -->

## Performance Benchmarks

Coming soon ...

## Project Structure

```
Megatron-Bridge/
├── examples/
│   ├── models/                  # Bridge usage examples
│   └── recipes/                 # Training examples
├── src/megatron/bridge/
│   ├── data/                    # Dataloaders and iterators
│   ├── models/                  # HuggingFace bridge infrastructure and model-specific implementations
│   │   ├── llama/               # Llama model providers
│   │   └── .../                 # Other models (gpt, t5, etc.)
│   ├── peft/                    # PEFT transformations and wrappers
│   ├── recipes/                 # Complete training recipes
│   ├── training/                # Training loop components
│   │   ├── tokenizers/          # Tokenizer library
│   │   └── utils/               # Training-specific utilities
│   └── utils/                   # Generic utilities for repo-wide usage
└── tests/                       # Comprehensive test suite
```

## Contributing

We welcome community contributions! Please see our [Contributor Guidelines](https://github.com/NVIDIA-NeMo/Megatron-Bridge/blob/main/CONTRIBUTING.md) for more information on how to get involved.
