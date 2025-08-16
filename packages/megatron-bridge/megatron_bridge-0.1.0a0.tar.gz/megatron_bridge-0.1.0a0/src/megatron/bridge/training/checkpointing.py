# Copyright (c) 2025, NVIDIA CORPORATION.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Input/output checkpointing."""

import contextlib
import os
import random
import shutil
import sys
import threading
from enum import Enum, auto
from functools import lru_cache
from logging import getLogger
from pathlib import Path
from time import time
from typing import Any, Callable, Optional, Union

import numpy as np
import torch
import yaml
from megatron.core import dist_checkpointing, mpu, tensor_parallel
from megatron.core.dist_checkpointing.mapping import ShardedObject
from megatron.core.dist_checkpointing.serialization import (
    get_default_load_sharded_strategy,
    get_default_save_sharded_strategy,
)
from megatron.core.dist_checkpointing.strategies.async_utils import AsyncRequest
from megatron.core.dist_checkpointing.strategies.fully_parallel import (
    FullyParallelLoadStrategyWrapper,
    FullyParallelSaveStrategyWrapper,
)
from megatron.core.num_microbatches_calculator import update_num_microbatches
from megatron.core.rerun_state_machine import get_rerun_state_machine

from megatron.bridge.peft.base import PEFT
from megatron.bridge.training import fault_tolerance
from megatron.bridge.training.config import CheckpointConfig, ConfigContainer
from megatron.bridge.training.state import GlobalState, TrainState
from megatron.bridge.training.utils import wandb_utils
from megatron.bridge.training.utils.log_utils import append_to_progress_log
from megatron.bridge.utils.common_utils import (
    get_rank_safe,
    get_world_size_safe,
    is_last_rank,
    print_rank_0,
    unwrap_model,
)
from megatron.bridge.utils.import_utils import safe_import


_, HAVE_RESIL = safe_import("nvidia_resiliency_ext.checkpointing")

# [ModelOpt]: Import
try:
    from modelopt.torch.opt.plugins import (
        restore_modelopt_state,
        restore_sharded_modelopt_state,
        save_modelopt_state,
        save_sharded_modelopt_state,
    )

    has_nvidia_modelopt = True
except Exception:
    has_nvidia_modelopt = False

TRAIN_STATE_FILE = "train_state.pt"
TRACKER_PREFIX = "latest"
CONFIG_FILE = "run_config.yaml"
_CHECKPOINT_VERSION = None

logger = getLogger(__name__)
_NON_PERSISTENT_CKPT_SUBDIR = "non_persistent"


# ============================================================================
# Checkpoint version and utilities
# ============================================================================


def set_checkpoint_version(value: float) -> None:
    """Set the global checkpoint version number.

    Args:
        value: The checkpoint version number (e.g., 3.0).
    """
    global _CHECKPOINT_VERSION
    if _CHECKPOINT_VERSION is not None:
        assert _CHECKPOINT_VERSION == value, "checkpoint versions do not match"
    _CHECKPOINT_VERSION = value


def get_checkpoint_version() -> Optional[float]:
    """Get the global checkpoint version number.

    Returns:
        The checkpoint version number, or None if not set.
    """
    global _CHECKPOINT_VERSION
    return _CHECKPOINT_VERSION


def ensure_directory_exists(filename: str, check_parent: bool = True) -> None:
    """Ensure that the directory for a given filename exists.

    Args:
        filename: The path whose directory should be checked/created.
        check_parent: If True (default), checks the parent directory of the filename.
                      If False, treats the filename itself as the directory path.
    """
    dirname = os.path.dirname(filename) if check_parent else filename
    os.makedirs(dirname, exist_ok=True)


def get_checkpoint_name(checkpoints_path: str, iteration: int, release: bool = False) -> str:
    """Determine the directory name for a specific checkpoint.

    Constructs the path based on iteration number or release flag.

    Args:
        checkpoints_path: Base directory where checkpoints are stored.
        iteration: The training iteration number.
        release: If True, uses 'release' as the directory name instead of iteration.

    Returns:
        The full path to the checkpoint directory.
    """
    if release:
        directory = "release"
    else:
        directory = "iter_{:07d}".format(iteration)

    common_path = os.path.join(checkpoints_path, directory)
    return common_path


def find_checkpoint_rank_0(checkpoints_path: str, iteration: int, release: bool = False) -> Optional[str]:
    """Find the checkpoint directory for a given iteration, assuming distributed checkpoints.

    Args:
        checkpoints_path: Base directory where checkpoints are stored.
        iteration: The training iteration number.
        release: If True, searches within the 'release' directory.

    Returns:
        The full path to the checkpoint directory if it's a valid distributed checkpoint, else None.
    """
    # Get the base directory for the iteration using the simplified get_checkpoint_name
    checkpoint_dir = get_checkpoint_name(checkpoints_path, iteration, release=release)

    # Check if this directory is a valid distributed checkpoint
    if dist_checkpointing.check_is_distributed_checkpoint(checkpoint_dir):
        return checkpoint_dir

    return None


def get_checkpoint_train_state_filename(checkpoints_path: str, prefix: Optional[str] = None) -> str:
    """Get the filename for the train state tracker file.

    This file typically stores metadata about the latest checkpoint, like the iteration number.

    Args:
        checkpoints_path: Base directory where checkpoints are stored.
        prefix: Optional prefix (e.g., 'latest') to prepend to the filename.

    Returns:
        The full path to the train state tracker file.
    """
    if prefix is None:
        return os.path.join(checkpoints_path, TRAIN_STATE_FILE)
    else:
        return os.path.join(checkpoints_path, f"{prefix}_{TRAIN_STATE_FILE}")


def get_checkpoint_run_config_filename(checkpoints_path: str) -> str:
    """Get the filename for the run configuration file within a checkpoint directory.

    Args:
        checkpoints_path: Base directory where checkpoints are stored.

    Returns:
        The full path to the run configuration file (e.g., run_config.yaml).
    """
    return os.path.join(checkpoints_path, CONFIG_FILE)


def checkpoint_exists(checkpoints_path: str) -> bool:
    """Check if a checkpoint directory exists.

    Args:
        checkpoints_path: Path to the potential checkpoint directory.

    Returns:
        True if the path exists, False otherwise.
    """
    if checkpoints_path is None:
        return False
    return os.path.exists(os.path.join(checkpoints_path, f"{TRACKER_PREFIX}_{TRAIN_STATE_FILE}"))


@lru_cache()
def read_train_state(train_state_filename: str) -> TrainState:
    """Read the train state metadata from a YAML file (rank 0 only).

    Reads the file on rank 0 and broadcasts the result to other ranks.

    Args:
        train_state_filename: Path to the train state YAML file.

    Returns:
        An initialized TrainState object.
    """
    state_obj = [None]
    if get_rank_safe() == 0:
        try:
            state_dict = torch.load(train_state_filename, map_location="cpu")
            ts = TrainState()
            ts.load_state_dict(state_dict)
            state_obj[0] = ts
        except Exception as e:
            error_msg = f"ERROR: Unable to load train state file {train_state_filename}: {e}"
            sys.stderr.write(error_msg + "\n")
            state_obj[0] = {"error": True, "msg": error_msg}

    if torch.distributed.is_initialized():
        print_rank_0(f"Broadcasting TrainState from rank 0 to all {get_world_size_safe()} ranks")
        torch.distributed.broadcast_object_list(state_obj, src=0)

    if isinstance(state_obj[0], dict) and state_obj[0].get("error", False):
        raise RuntimeError(state_obj[0]["msg"])

    return state_obj[0]


@lru_cache()
def read_run_config(run_config_filename: str) -> dict[str, Any]:
    """Read the run configuration from a YAML file (rank 0 only).

    Reads the file on rank 0 and broadcasts the result to other ranks.

    Args:
        run_config_filename: Path to the run config YAML file.

    Returns:
        A dictionary containing the run configuration.

    Raises:
        RuntimeError: If reading the config file fails on rank 0.
    """
    config_obj = [None]

    if get_rank_safe() == 0:
        try:
            with open(run_config_filename, "r") as f:
                config_dict = yaml.safe_load(f)
            config_obj[0] = config_dict
        except Exception as e:
            error_msg = f"ERROR: Unable to load config file {run_config_filename}: {e}"
            sys.stderr.write(error_msg + "\n")
            config_obj[0] = {"error": True, "msg": error_msg}

    if torch.distributed.is_initialized():
        print_rank_0(f"Broadcasting config from rank 0 to all {get_world_size_safe()} ranks")
        torch.distributed.broadcast_object_list(config_obj, src=0)

    if isinstance(config_obj[0], dict) and config_obj[0].get("error", False):
        raise RuntimeError(config_obj[0]["msg"])

    return config_obj[0]


# ============================================================================
# Async checkpoint utilities
# ============================================================================


def schedule_async_save(global_state: GlobalState, async_request: AsyncRequest) -> None:
    """Schedule the async save request.

    Args:
        global_state: The global training state containing the async calls queue.
        async_request: the async save request.
    """
    async_queue = global_state.async_calls_queue
    if async_queue is not None:
        async_queue.schedule_async_request(async_request)


def maybe_finalize_async_save(
    global_state: GlobalState, ckpt_cfg: CheckpointConfig, blocking: bool = False, terminate: bool = False
) -> None:
    """Finalizes active async save calls.

    Args:
        global_state: The global training state containing the async calls queue.
        ckpt_cfg (CheckpointConfig): The checkpoint configuration.
        blocking (bool, optional): if True, will wait until all active requests
            are done. Otherwise, finalizes only the async request that already
            finished. Defaults to False.
        terminate (bool, optional): if True, the asynchronous queue will
                be closed as the last action of this function.
    """
    if not ckpt_cfg.async_save:
        return

    async_queue = global_state.async_calls_queue
    if async_queue is None:
        return

    if blocking and not is_empty_async_queue(global_state):
        print_rank_0("Unfinalized async checkpoint saves. Finalizing them synchronously now.")

    async_queue.maybe_finalize_async_calls(blocking)

    if terminate:
        async_queue.close()


def is_empty_async_queue(global_state: GlobalState) -> bool:
    """Check if async calls queue is empty. This result is consistent across ranks.

    Args:
        global_state: The global training state containing the async calls queue.

    Returns:
        bool: True if there is any ongoing async call.
    """
    async_queue = global_state.async_calls_queue
    if async_queue is None:
        return True
    return async_queue.get_num_unfinalized_calls() == 0


def get_rng_state(data_parallel_random_init: bool) -> ShardedObject:
    """Get the random number generator states for all necessary libraries.

    Collects states from random, numpy, torch, cuda, and the Megatron RNG tracker.
    Optionally gathers states across data parallel ranks.
    Always wraps the result in a ShardedObject for distributed checkpointing.

    Args:
        data_parallel_random_init: If True, gathers RNG states across data parallel ranks.

    Returns:
        A ShardedObject containing the RNG states.
    """
    rng_state = {
        "random_rng_state": random.getstate(),
        "np_rng_state": np.random.get_state(),
        "torch_rng_state": torch.get_rng_state(),
        "cuda_rng_state": torch.cuda.get_rng_state(),
        "rng_tracker_states": tensor_parallel.get_cuda_rng_tracker().get_states(),
    }

    rng_state_list = None
    if torch.distributed.is_initialized() and mpu.get_data_parallel_world_size() > 1 and data_parallel_random_init:
        rng_state_list = [None for i in range(mpu.get_data_parallel_world_size())]
        torch.distributed.all_gather_object(rng_state_list, rng_state, group=mpu.get_data_parallel_group())
    else:
        rng_state_list = [rng_state]

    pp_rank = mpu.get_pipeline_model_parallel_rank()
    pp_size = mpu.get_pipeline_model_parallel_world_size()
    tp_rank = mpu.get_tensor_model_parallel_rank()
    tp_size = mpu.get_tensor_model_parallel_world_size()
    rng_state_list = ShardedObject(
        "rng_state",
        rng_state_list,
        (pp_size, tp_size),
        (pp_rank, tp_rank),
        replica_id=mpu.get_data_parallel_rank(with_context_parallel=True),
    )

    return rng_state_list


class CheckpointType(Enum):
    """Types of checkpoints to save."""

    LOCAL = auto()
    GLOBAL = auto()


def save_checkpoint(
    state: GlobalState,
    model: Union[torch.nn.Module, list[torch.nn.Module]],
    optimizer: Optional[torch.optim.Optimizer],
    opt_param_scheduler: Optional[Any],
    num_floating_point_operations_so_far: int,
    checkpointing_context: Optional[dict[str, Any]] = None,
    pipeline_rank: Optional[int] = None,
    tensor_rank: Optional[int] = None,
    non_persistent_ckpt: bool = False,
    train_data_iterator: Optional[Any] = None,
    preprocess_common_state_dict_fn: Optional[Callable[[dict[str, Any]], dict[str, Any]]] = None,
) -> None:
    """Save a model checkpoint.

    Handles saving the model state, optimizer state, scheduler state, RNG state,
    and other metadata based on the configuration and checkpoint type (global or local).
    Supports synchronous and asynchronous saving.

    Args:
        state: The GlobalState object.
        model: The model module(s) to save.
        optimizer: The optimizer instance.
        opt_param_scheduler: The optimizer parameter scheduler instance.
        num_floating_point_operations_so_far: Total FLOPs computed so far.
        checkpointing_context: Dictionary to store context across saves (e.g., strategies).
        pipeline_rank: Pipeline parallel rank (defaults to current rank).
        tensor_rank: Tensor parallel rank (defaults to current rank).
        non_persistent_ckpt: If True, saves as a non-persistent checkpoint.
        train_data_iterator: The training data iterator (for saving state if supported).
        preprocess_common_state_dict_fn: Optional function to preprocess the common state dict
                                         before consistency checks in distributed checkpointing.
    """

    train_state = state.train_state
    start_ckpt = time()
    cfg = state.cfg
    ckpt_cfg = cfg.checkpoint

    if ckpt_cfg.async_save and not is_empty_async_queue(state):
        print_rank_0(
            "WARNING: Starting a checkpoint save before previous has finished. "
            "Consider increasing the checkpoint interval."
        )

    # Monitor for the checkpointing timeout (no-op if FT is not enabled)
    fault_tolerance.on_checkpointing_start(state)

    # Only rank zero of the data parallel writes to the disk.
    model = unwrap_model(model)

    # Determine checkpoint type and save directory
    save_dir = ckpt_cfg.save
    if non_persistent_ckpt and ckpt_cfg.non_persistent_ckpt_type == "local":
        ckpt_type = CheckpointType.LOCAL
        save_dir = checkpointing_context["local_checkpoint_manager"].local_ckpt_dir
    elif non_persistent_ckpt and ckpt_cfg.non_persistent_ckpt_type == "global":
        ckpt_type = CheckpointType.GLOBAL
        save_dir = (
            ckpt_cfg.non_persistent_global_ckpt_dir
            if ckpt_cfg.non_persistent_global_ckpt_dir
            else os.path.join(save_dir, _NON_PERSISTENT_CKPT_SUBDIR)
        )
        # TODO Can we ensure the previous checkpoint is saved? We don't want to allow two saves in parallel.
        cleanup_old_non_persistent_checkpoint(save_dir, leave_ckpt_num=1, do_async=ckpt_cfg.async_save)
    elif non_persistent_ckpt:
        # Invalid non_persistent_ckpt_type value
        raise ValueError(
            f"Invalid non_persistent_ckpt_type: {ckpt_cfg.non_persistent_ckpt_type}. Must be 'local' or 'global'."
        )
    else:
        # Regular persistent checkpoint - always GLOBAL
        ckpt_type = CheckpointType.GLOBAL

    ckpt_format = ckpt_cfg.ckpt_format if ckpt_type == CheckpointType.GLOBAL else "torch"  # torch for local
    print_rank_0(f"saving checkpoint at iteration {train_state.step:7d} to {save_dir} in {ckpt_format} format")

    # Collect rng state across data parallel ranks.
    rng_state = get_rng_state(data_parallel_random_init=cfg.rng.data_parallel_random_init)

    # Collect rerun state across all ranks
    rerun_state_machine = get_rerun_state_machine()
    rerun_state = rerun_state_machine.state_dict(
        data_iterator=train_data_iterator,
        ckpt_format=ckpt_cfg.ckpt_format,
    )

    # Checkpoint name.
    checkpoint_name = get_checkpoint_name(save_dir, train_state.step, release=False)

    # Save dataloader state if the dataloader supports it (currently only Megatron Energon).
    maybe_save_dataloader_state(train_data_iterator, train_state.step, getattr(cfg.dataset, "dataloader_save", None))

    async_save_request = None
    if ckpt_cfg.async_save:
        if ckpt_type == CheckpointType.GLOBAL and ckpt_cfg.ckpt_format != "torch_dist":
            raise NotImplementedError(
                f"Async checkpoint save not implemented for {ckpt_cfg.ckpt_format} distributed checkpoint format"
            )

    rank = torch.distributed.get_rank() if torch.distributed.is_initialized() else 0

    # Collect cfg, model, RNG.
    sharded_sd_metadata = _build_sharded_state_dict_metadata(
        cfg.optimizer.use_distributed_optimizer, ckpt_cfg.fully_parallel_save
    )
    if cfg.optimizer.use_distributed_optimizer:
        print_rank_0(
            f"Storing distributed optimizer sharded state of type {sharded_sd_metadata['distrib_optim_sharding_type']}"
        )

    state_dict = generate_state_dict(
        cfg,
        model,
        optimizer,
        opt_param_scheduler,
        rng_state,
        iteration=train_state.step,
        optim_sd_kwargs=dict(metadata=sharded_sd_metadata),
        model_sd_kwargs=dict(metadata=sharded_sd_metadata),
        rerun_state=rerun_state,
    )

    # Apply PEFT filtering to save adapter-only checkpoints
    if cfg.peft is not None:
        state_dict = apply_peft_adapter_filter_to_state_dict(state_dict, cfg.peft)

    if ckpt_type == CheckpointType.GLOBAL:
        if not torch.distributed.is_initialized() or torch.distributed.get_rank() == 0:
            # TODO Handle non-empty directories (e.g., after a crash during saving).
            ensure_directory_exists(checkpoint_name, check_parent=False)
        if checkpointing_context is not None and "save_strategy" in checkpointing_context:
            save_strategy = checkpointing_context["save_strategy"]
            # Already saved once before - don't need to rerun sharding validation
            validate_sharding_integrity = not ckpt_cfg.ckpt_assume_constant_structure
        else:
            validate_sharding_integrity = True
            save_strategy = get_default_save_sharded_strategy(ckpt_cfg.ckpt_format)
            if ckpt_cfg.ckpt_assume_constant_structure and ckpt_cfg.ckpt_format == "torch_dist":
                save_strategy.use_cached_ckpt_structure = ckpt_cfg.ckpt_assume_constant_structure
                if checkpointing_context is not None and "load_strategy" in checkpointing_context:
                    cached_global_metadata = getattr(
                        checkpointing_context["load_strategy"], "cached_global_metadata", None
                    )
                    if cached_global_metadata is not None:
                        logger.debug("Plugging in the read metadata from the load strategy...")
                        save_strategy.cached_global_metadata = cached_global_metadata
                    else:
                        logger.debug("Failed to plug in the read metadata from the load strategy...")

            if ckpt_cfg.fully_parallel_save:
                save_strategy = FullyParallelSaveStrategyWrapper(
                    save_strategy,
                    mpu.get_data_parallel_group(with_context_parallel=True),
                    ckpt_cfg.ckpt_assume_constant_structure,
                )
        # Store save strategy for future checkpoint saves
        if checkpointing_context is not None:
            checkpointing_context["save_strategy"] = save_strategy
        end_ckpt = time()
        logger.debug(f"rank: {rank}, takes {end_ckpt - start_ckpt} to prepare state dict for ckpt ")
        async_save_request = dist_checkpointing.save(
            state_dict,
            checkpoint_name,
            save_strategy,
            async_sharded_save=ckpt_cfg.async_save,
            validate_access_integrity=validate_sharding_integrity,
            preprocess_common_before_consistancy_check=preprocess_common_state_dict_fn,
            content_metadata=sharded_sd_metadata,
        )
        # [ModelOpt]: save sharded modelopt_state
        if has_nvidia_modelopt:
            save_sharded_modelopt_state(model, checkpoint_name, (ckpt_cfg.ckpt_format, 1))
    else:
        # [ModelOpt]: Inject modelopt_state into state_dict
        if has_nvidia_modelopt:
            if ckpt_type == CheckpointType.LOCAL:
                print_rank_0("WARNING: Local checkpointing does not support nvidia_modelopt.")
            else:  # GLOBAL checkpoint type
                save_modelopt_state(model, state_dict)

        end_ckpt = time()
        logger.debug(f"rank: {rank}, takes {end_ckpt - start_ckpt} to prepare state dict for ckpt ")
        if ckpt_type == CheckpointType.LOCAL:
            try:
                from megatron.core.dist_checkpointing.tensor_aware_state_dict import MCoreTensorAwareStateDict
            except ModuleNotFoundError:
                raise RuntimeError(
                    "The 'nvidia_resiliency_ext' module is required for local "
                    "checkpointing but was not found. Please ensure it is installed."
                )
            algo = ckpt_cfg.non_persistent_local_ckpt_algo
            cached_metadata = None
            if ckpt_cfg.ckpt_assume_constant_structure and "local_checkpoint_cache" in checkpointing_context:
                cached_metadata = checkpointing_context["local_checkpoint_cache"]
            state_dict_for_save, cacheable_metadata = MCoreTensorAwareStateDict.from_state_dict(
                state_dict,
                algo=algo,
                cached_metadata=cached_metadata,
                parallelization_group=mpu.get_data_parallel_group(with_context_parallel=True),
            )
            async_save_request = checkpointing_context["local_checkpoint_manager"].save(
                state_dict_for_save, train_state.step, is_async=bool(ckpt_cfg.async_save)
            )
            checkpointing_context["local_checkpoint_cache"] = cacheable_metadata

    start_misc = time()
    if ckpt_type != CheckpointType.LOCAL:
        if not ckpt_cfg.async_save:
            assert async_save_request is None
            # Wait so everyone is done (necessary)
            if torch.distributed.is_initialized():
                torch.distributed.barrier()

    # And update the latest train state
    if get_rank_safe() == 0:
        train_state_local_filename = get_checkpoint_train_state_filename(checkpoint_name)
        train_state_global_filename = get_checkpoint_train_state_filename(save_dir, prefix=TRACKER_PREFIX)
        config_filename = get_checkpoint_run_config_filename(checkpoint_name)
        if ckpt_type == CheckpointType.LOCAL:

            def train_state_finalize_fn():
                print_rank_0(f"  successfully saved local checkpoint from iteration {train_state.step:7d}")
                if cfg.logger.log_progress and ckpt_cfg.async_save:
                    append_to_progress_log(
                        ckpt_cfg.save, f"Saved async local checkpoint\tIteration: {train_state.step}", barrier=False
                    )

        else:
            train_state_dict = train_state.state_dict()

            def train_state_finalize_fn() -> None:
                train_state_dict["floating_point_operations_so_far"] = torch.tensor(
                    num_floating_point_operations_so_far, dtype=torch.float32
                )
                torch.save(train_state_dict, train_state_local_filename)
                shutil.copy(train_state_local_filename, train_state_global_filename)
                cfg.to_yaml(config_filename)

                tp_rank = (tensor_rank if tensor_rank is not None else mpu.get_tensor_model_parallel_rank()) + 1
                tp_world_size = mpu.get_tensor_model_parallel_world_size()
                pp_rank = (pipeline_rank if pipeline_rank is not None else mpu.get_pipeline_model_parallel_rank()) + 1
                pp_world_size = mpu.get_pipeline_model_parallel_world_size()
                print_rank_0(
                    f"  successfully saved checkpoint from iteration {train_state_dict['step'].item():7d} "
                    f"to {ckpt_cfg.save} [ t {tp_rank}/{tp_world_size}, p {pp_rank}/{pp_world_size} ]"
                )

                if cfg.logger.log_progress and ckpt_cfg.async_save:
                    append_to_progress_log(
                        ckpt_cfg.save,
                        f"Saved async checkpoint\tIteration: {train_state_dict['step'].item()}",
                        barrier=False,
                    )

        if ckpt_cfg.async_save:
            assert async_save_request is not None
            async_save_request.add_finalize_fn(train_state_finalize_fn)
        else:
            train_state_finalize_fn()

    # Additional callback for wandb (last rank)
    if not torch.distributed.is_initialized() or is_last_rank():

        def wandb_finalize_fn() -> None:
            wandb_utils.on_save_checkpoint_success(
                checkpoint_name,
                save_dir,
                train_state.step,
                wandb_writer=state.wandb_logger,
            )

        if ckpt_cfg.async_save:
            assert async_save_request is not None
            async_save_request.add_finalize_fn(wandb_finalize_fn)
        else:
            wandb_finalize_fn()

    if ckpt_cfg.async_save:
        schedule_async_save(state, async_save_request)
        print_rank_0(f"  scheduled an async checkpoint save at iteration {train_state.step:7d} to {save_dir}")

    # Wait so everyone is done (not necessary)
    if torch.distributed.is_initialized():
        torch.distributed.barrier()

    end_misc = time()
    logger.debug(f"rank: {rank}, takes {end_misc - start_misc} to finalize ckpt save ")

    fault_tolerance.on_checkpointing_end(global_state=state, is_async_finalization=False)


def cleanup_old_non_persistent_checkpoint(save_dir: str, leave_ckpt_num: int = 1, do_async: bool = False) -> None:
    """Clean up old non-persistent checkpoints in a directory.

    Keeps the specified number of latest checkpoints and removes older ones.
    Currently only cleans up directories matching "iter_*".

    Args:
        save_dir: The directory containing non-persistent checkpoints.
        leave_ckpt_num: The number of latest checkpoints to keep.
        do_async: If True, performs cleanup in a background thread.
    """
    if torch.distributed.is_initialized() and torch.distributed.get_rank() != 0:
        return
    save_dir = Path(save_dir)

    iter_prefix = "iter_"
    iter_ckpts = save_dir.rglob(f"{iter_prefix}*")
    sorted_iter_ckpts = sorted(iter_ckpts, key=lambda ckpt_name: int(ckpt_name.name[len(iter_prefix) :]))
    if not sorted_iter_ckpts:
        return
    rm_iter_ckpts = sorted_iter_ckpts[:-leave_ckpt_num]
    print_rank_0(f"Non-persistent checkpoints scheduled for removal: {rm_iter_ckpts}")
    print_rank_0(f"Non-persistent checkpoints to be kept: {sorted_iter_ckpts[-leave_ckpt_num:]}")

    def remove_iter_ckpts(_iter_ckpts):
        for ckpt in _iter_ckpts:
            shutil.rmtree(ckpt)

    if do_async:
        threading.Thread(target=remove_iter_ckpts, args=(rm_iter_ckpts,)).start()
    else:
        remove_iter_ckpts(rm_iter_ckpts)


def maybe_save_dataloader_state(train_iterator: Any, iteration: int, dataloader_save_path: Optional[str]) -> None:
    """Save the dataloader state if the iterator supports it.

    Checks if the train_iterator has a `save_state` method and calls it.

    Args:
        train_iterator: The training data iterator.
        iteration: The current training iteration.
        dataloader_save_path: The path where the dataloader state should be saved.
    """
    # If no dataloader or saving path is provided, exit early, otherwise, raise an error.
    if train_iterator is None or dataloader_save_path is None or dataloader_save_path == "":
        return

    # If dataloader doesn't support saving state, raise an error.
    if not hasattr(train_iterator.iterable, "save_state"):
        raise RuntimeError(f"Could not find a save_state for the train_iterator of type {type(train_iterator)}")

    # Save dataloader state for each data parallel rank only once.
    first_rank = mpu.is_pipeline_first_stage() and mpu.get_tensor_model_parallel_rank() == 0
    if not first_rank:
        return

    dp_rank = mpu.get_data_parallel_rank()
    print(f"saving dataloader checkpoint at iteration {iteration} to {dataloader_save_path}")
    train_dataloader_state_dict = train_iterator.iterable.save_state()
    # Get the base directory for the current iteration
    iter_dir = get_checkpoint_name(dataloader_save_path, iteration)
    # Construct the specific filename within that iteration directory
    data_state_save_path = os.path.join(iter_dir, f"train_dataloader_dprank{dp_rank:03d}.pt")

    torch.distributed.barrier(group=mpu.get_data_parallel_group())

    if mpu.get_data_parallel_rank() == 0:
        ensure_directory_exists(data_state_save_path)

    torch.distributed.barrier(group=mpu.get_data_parallel_group())

    dataloader_save_dict = {}
    dataloader_save_dict["dataloader_state_dict"] = train_dataloader_state_dict
    torch.save(dataloader_save_dict, data_state_save_path)


def generate_state_dict(
    cfg: ConfigContainer,
    model: Union[torch.nn.Module, list[torch.nn.Module]],
    optimizer: Optional[torch.optim.Optimizer],
    opt_param_scheduler: Optional[Any],
    rng_state: ShardedObject,
    iteration: Optional[int] = None,
    optim_sd_kwargs: Optional[dict[str, Any]] = None,
    model_sd_kwargs: Optional[dict[str, Any]] = None,
    rerun_state: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Generate the state dictionary to be saved in a checkpoint.

    Args:
        cfg: The configuration container.
        model: The model module(s).
        optimizer: The optimizer instance.
        opt_param_scheduler: The optimizer parameter scheduler instance.
        rng_state: Collected RNG states as a ShardedObject.
        iteration: The current training iteration.
        optim_sd_kwargs: Additional keyword arguments for optimizer state dict generation.
        model_sd_kwargs: Metadata for model state dict generation.
        rerun_state: State dictionary from the rerun state machine.

    Returns:
        A dictionary containing the complete state to be saved.
    """
    # Arguments, iteration, and model.
    state_dict = {}
    state_dict["checkpoint_version"] = 3.0
    if iteration is not None:
        state_dict["iteration"] = iteration

    if len(model) == 1:
        state_dict["model"] = model[0].sharded_state_dict(**(model_sd_kwargs or {}))
    else:
        for i in range(len(model)):
            state_dict["model%d" % i] = model[i].sharded_state_dict(**(model_sd_kwargs or {}))

    # Optimizer stuff.
    if cfg.checkpoint.save_optim:
        if optimizer is not None and not getattr(optimizer, "is_stub_optimizer", False):
            state_dict["optimizer"] = optimizer.sharded_state_dict(state_dict, **(optim_sd_kwargs or {}))
        if opt_param_scheduler is not None:
            state_dict["opt_param_scheduler"] = opt_param_scheduler.state_dict()

    # Rerun state
    state_dict["rerun_state_machine"] = rerun_state

    # RNG states.
    if cfg.checkpoint.save_rng:
        state_dict["rng_state"] = rng_state
    return state_dict


def load_checkpoint(
    state: GlobalState,
    model: Union[torch.nn.Module, list[torch.nn.Module]],
    optimizer: Optional[torch.optim.Optimizer],
    opt_param_scheduler: Optional[Any],
    strict: bool = True,
    checkpointing_context: Optional[dict[str, Any]] = None,
    skip_load_to_model_and_opt: bool = False,
) -> tuple[int, int]:
    """Load a model checkpoint.

    Handles loading model state, optimizer state, scheduler state, RNG state,
    and other metadata based on the configuration and checkpoint type.
    Supports loading global distributed and local non-persistent checkpoints.

    Args:
        state: The GlobalState object.
        model: The model module(s) to load state into.
        optimizer: The optimizer instance to load state into.
        opt_param_scheduler: The scheduler instance to load state into.
        strict: Whether to enforce strict loading (see torch.nn.Module.load_state_dict).
        checkpointing_context: Dictionary to store context across loads (e.g., strategies).
        skip_load_to_model_and_opt: If True, only loads metadata (iteration, rng) but
                                      skips loading state into model and optimizer modules.

    Returns:
        A tuple containing:
        - iteration: The training iteration number.
        - num_floating_point_operations_so_far: The total FLOPs computed so far.
    """
    cfg = state.cfg
    load_dir = cfg.checkpoint.load

    # Finetuning directories
    pretrained_dir = cfg.checkpoint.pretrained_checkpoint
    if pretrained_dir is not None and not checkpoint_exists(load_dir):
        print_rank_0(
            f"Checkpoint file not found in load directory {load_dir}. "
            f"Attempting to finetune with checkpoint in {pretrained_dir}"
        )
        load_dir = pretrained_dir
        if not checkpoint_exists(load_dir):
            raise FileNotFoundError("No checkpoint found in load directory or pretrained directory")
        cfg.checkpoint.finetune = True

    return _load_checkpoint_from_path(
        load_dir, state, model, optimizer, opt_param_scheduler, strict, checkpointing_context
    )


def _load_checkpoint_from_path(
    load_dir: str,
    state: GlobalState,
    model: Union[torch.nn.Module, list[torch.nn.Module]],
    optimizer: Optional[torch.optim.Optimizer],
    opt_param_scheduler: Optional[Any],
    strict: bool = True,
    checkpointing_context: Optional[dict[str, Any]] = None,
    skip_load_to_model_and_opt: bool = False,
) -> tuple[int, int]:
    """Load a checkpoint from a given path.

    Args:
        load_dir: The directory containing the checkpoint.
        state: The GlobalState object.
        model: The model module(s) to load state into.
        optimizer: The optimizer instance to load state into.
        opt_param_scheduler: The scheduler instance to load state into.
        strict: Whether to enforce strict loading (see torch.nn.Module.load_state_dict).
        checkpointing_context: Dictionary to store context across loads (e.g., strategies).
        skip_load_to_model_and_opt: If True, only loads metadata (iteration, rng) but
                                      skips loading state into model and optimizer modules.

    Returns:
        A tuple containing:
        - iteration: The training iteration number.
        - num_floating_point_operations_so_far: The total FLOPs computed so far.
    """
    cfg = state.cfg

    model = unwrap_model(model)

    load_kwargs = {}
    state_dict, checkpoint_name, release, ckpt_type = _load_base_checkpoint(
        load_dir,
        cfg,
        rank0=True,
        checkpointing_context=checkpointing_context,
    )

    # Checkpoint not loaded.
    if state_dict is None:
        # Iteration and num_floating_point_operations_so_far default to 0.
        return 0, 0

    run_config = read_run_config(get_checkpoint_run_config_filename(checkpoint_name))

    # TODO: Make read_run_config() return a ConfigContainer object
    ckpt_tp_pp = (
        run_config["model"]["tensor_model_parallel_size"],
        run_config["model"]["pipeline_model_parallel_size"],
        run_config["model"].get("encoder_tensor_model_parallel_size", 0),
        run_config["model"].get("encoder_pipeline_model_parallel_size", 0),
    )
    run_tp_pp = (
        cfg.model.tensor_model_parallel_size,
        cfg.model.pipeline_model_parallel_size,
        getattr(cfg.model, "encoder_tensor_model_parallel_size", 0),
        getattr(cfg.model, "encoder_pipeline_model_parallel_size", 0),
    )
    mismatch_msg = "(TP, PP, encoder TP, encoder PP) mismatch after resume ({} vs {} from checkpoint)".format(
        run_tp_pp, ckpt_tp_pp
    )
    # Determine if RNG state will be loaded
    if (
        ckpt_tp_pp == run_tp_pp
        and not release
        and not cfg.checkpoint.finetune
        and cfg.checkpoint.load_rng
        and run_config["checkpoint"]["save_rng"]
    ):
        # we can load the rng state
        gen_sd_rng_state = get_rng_state(data_parallel_random_init=cfg.rng.data_parallel_random_init)
    else:
        gen_sd_rng_state = None
        if ckpt_tp_pp != run_tp_pp:
            print_rank_0("{}: RNG state will be ignored".format(mismatch_msg))

    sharded_sd_metadata = dist_checkpointing.load_content_metadata(preloaded_state_dict=state_dict)
    print_rank_0(f"sharded_state_dict metadata loaded from the checkpoint: {sharded_sd_metadata}")
    # Determine if optimizer state will be loaded
    if (
        not release
        and not cfg.checkpoint.finetune
        and cfg.checkpoint.load_optim
        and run_config["checkpoint"]["save_optim"]
    ):
        gen_sd_optim = optimizer
        gen_sd_opt_param_scheduler = opt_param_scheduler

        if cfg.optimizer.use_distributed_optimizer:
            if sharded_sd_metadata is None:
                # Backward-compatibility with old checkpoints which don't have content versioning
                # Can be removed after ending support for optimizer checkpoints with MCore < v0.13
                # (for MCore v0.13+ checkpoints `sharded_sd_metadata is not None`)
                sharded_sd_metadata = {
                    "distrib_optim_sharding_type": (
                        "fully_sharded_model_space"
                        if run_config["checkpoint"]["fully_parallel_save"]
                        else "dp_zero_gather_scatter"
                    ),
                }
            if (
                ckpt_tp_pp != run_tp_pp
                and sharded_sd_metadata["distrib_optim_sharding_type"] != "fully_sharded_model_space"
            ):
                raise RuntimeError(
                    f"{mismatch_msg}: not supported for DistributedOptimizer with sharding type"
                    f" {sharded_sd_metadata['distrib_optim_sharding_type']}."
                    f" Please use `checkpoint_config.fully_parallel_save=True` for checkpoint saving."
                )

    else:
        gen_sd_optim = None
        gen_sd_opt_param_scheduler = None

    optim_sd_kwargs = dict(metadata=sharded_sd_metadata, is_loading=True)
    model_sd_kwargs = dict(metadata=sharded_sd_metadata)

    # Determine if rerun state will be loaded
    if ckpt_tp_pp == run_tp_pp and not release and not cfg.checkpoint.finetune and "rerun_state_machine" in state_dict:
        rerun_state_machine = get_rerun_state_machine()
        gen_sd_rerun_state = rerun_state_machine.state_dict(data_iterator=None, ckpt_format="torch_dist")
    else:
        gen_sd_rerun_state = None
        if ckpt_tp_pp != run_tp_pp:
            print_rank_0("{}: Rerun state will be ignored".format(mismatch_msg))

    # [ModelOpt]: IMPORTANT! Restoring modelopt_state (sharded or not) must be performed
    # after the model instance has been created and before _load_base_checkpoint is called.
    if has_nvidia_modelopt:
        if ckpt_type == CheckpointType.LOCAL:
            print_rank_0("WARNING: Local checkpointing does not support nvidia_modelopt.")
        elif ckpt_type == CheckpointType.GLOBAL:
            restore_modelopt_state(model, state_dict)
        else:
            restore_sharded_modelopt_state(model, checkpoint_name)

    # [ModelOpt]: Initial loading from non-resume sharded checkpoint to a Distillation Model
    # will result in key mismatch with loss modules potentially containing parameters, since
    # it requires generating a state_dict before loading. Here we hide those modules if present.
    with contextlib.ExitStack() as stack:  # Allows multiple context managers for each model shard
        if cfg.checkpoint.finetune and hasattr(model[0], "hide_loss_modules"):
            for m in model:
                stack.enter_context(m.hide_loss_modules())
        load_kwargs["sharded_state_dict"] = generate_state_dict(
            cfg,
            model,
            gen_sd_optim,
            gen_sd_opt_param_scheduler,
            gen_sd_rng_state,
            optim_sd_kwargs=optim_sd_kwargs,
            model_sd_kwargs=model_sd_kwargs,
            rerun_state=gen_sd_rerun_state,
        )

    # For PEFT, check if resuming from a checkpoint saved during training, which contains only the PEFT adapter states
    # This situation occurs when:
    # 1. The PEFT config is set
    # 2. Loading from a checkpoint saved during training (not loading from a pretrained checkpoint)
    # 3. Not in finetune mode
    is_peft_resume = (
        cfg.peft is not None
        and cfg.checkpoint.load is not None
        and load_dir == cfg.checkpoint.load
        and load_dir != cfg.checkpoint.pretrained_checkpoint
        and not cfg.checkpoint.finetune
    )

    if is_peft_resume:
        load_kwargs["sharded_state_dict"] = apply_peft_adapter_filter_to_state_dict(
            load_kwargs["sharded_state_dict"], cfg.peft
        )

    state_dict, checkpoint_name, release, ckpt_type = _load_base_checkpoint(
        load_dir, cfg, rank0=False, checkpointing_context=checkpointing_context, **load_kwargs
    )

    # Set checkpoint version.
    set_checkpoint_version(state_dict.get("checkpoint_version", 0))

    # Check arguments.
    assert state.train_state.consumed_train_samples == 0
    assert state.train_state.skipped_train_samples == 0
    assert state.train_state.consumed_valid_samples == 0

    state.train_state = read_train_state(get_checkpoint_train_state_filename(checkpoint_name))
    # Set iteration.
    if cfg.checkpoint.finetune or release:
        state.train_state.step = 0

    if not cfg.checkpoint.finetune:
        # check_checkpoint_args(checkpoint_args)
        update_num_microbatches(consumed_samples=state.train_state.consumed_train_samples, verbose=True)

    def load_model_state_dict(module: torch.nn.Module, state_dict: dict[str, Any], strict: bool):
        """Helper function to load state dict with fallback for missing extra states."""
        try:
            module.load_state_dict(state_dict, strict=strict)
        except Exception:
            if strict:
                # Fallback support for backward compatibility breaking changes in TransformerEngine
                load_return = module.load_state_dict(state_dict, strict=False)
                print(f"load_return: {load_return}")

    # Model.
    if not skip_load_to_model_and_opt:
        load_strict = False if is_peft_resume else strict
        if len(model) == 1:
            load_model_state_dict(model[0], state_dict["model"], load_strict)
        else:
            for i in range(len(model)):
                # If there is no corresponding model in the state_dict, it will be ignored.
                # It means that this is an empty stage.
                model_key = "model%d" % i
                if model_key not in state_dict:
                    continue
                load_model_state_dict(model[i], state_dict[model_key], load_strict)

    # Fix up query/key/value matrix ordering if needed.
    checkpoint_version = get_checkpoint_version()
    print_rank_0(f" checkpoint version {checkpoint_version}")
    # fix_query_key_value_ordering(model, checkpoint_version) # Assuming this is not needed if only v3.0 is supported

    # Optimizer.
    if not release and not cfg.checkpoint.finetune and cfg.checkpoint.load_optim:
        try:
            # Load state dict.
            if (
                not skip_load_to_model_and_opt
                and optimizer is not None
                and not getattr(optimizer, "is_stub_optimizer", False)
            ):
                optimizer.load_state_dict(state_dict["optimizer"])

            # Load distributed optimizer's custom parameter state.
            # For distributed checkpoint it's already loaded in load_state_dict above
            # if cfg.optimizer.use_distributed_optimizer and not is_dist_ckpt:
            #     # NOTE: this is a manual read of the tracker file.
            #     # This code should not be reached when reading from a non_persistent checkpoint
            #     assert not is_dist_ckpt
            #     tracker_filename = get_checkpoint_train_state_filename(load_dir, prefix="latest")
            #     iteration, release = read_train_state(tracker_filename)
            #     model_checkpoint_name = get_checkpoint_name(load_dir, iteration, release)
            #     optim_checkpoint_name = get_distributed_optimizer_checkpoint_name(model_checkpoint_name)
            #     optimizer.load_parameter_state(
            #         optim_checkpoint_name,
            #         update_legacy_format=cfg.checkpoint.ckpt_convert_update_legacy_dist_opt_format,
            #     )

            # Load scheduler.
            if opt_param_scheduler is not None:
                if "lr_scheduler" in state_dict:  # backward compatibility
                    opt_param_scheduler.load_state_dict(state_dict["lr_scheduler"])
                else:
                    opt_param_scheduler.load_state_dict(state_dict["opt_param_scheduler"])
        except KeyError as e:
            print_rank_0(
                "Unable to load optimizer from checkpoint {}. "
                "Specify --no-load-optim or --finetune to prevent "
                "attempting to load the optimizer state, "
                "exiting ...".format(checkpoint_name)
            )
            raise e
    else:
        if (cfg.model.fp16 or cfg.model.bf16) and optimizer is not None:
            if cfg.checkpoint.load_main_params_from_ckpt:
                optimizer.reload_model_params(state_dict=state_dict)
            else:
                optimizer.reload_model_params()
    # rerun state
    try:
        if "rerun_state_machine" in state_dict:
            get_rerun_state_machine().load_state_dict(state_dict["rerun_state_machine"])
    except Exception as e:
        print(f"Unable to restore RerunMachine from checkpoint: {e}")
        sys.exit()

    # rng states.
    if not release and not cfg.checkpoint.finetune and cfg.checkpoint.load_rng:
        try:
            if "rng_state" in state_dict:
                # access rng_state for data parallel rank
                if cfg.rng.data_parallel_random_init:
                    rng_state = state_dict["rng_state"][mpu.get_data_parallel_rank()]
                else:
                    rng_state = state_dict["rng_state"][0]
                random.setstate(rng_state["random_rng_state"])
                np.random.set_state(rng_state["np_rng_state"])
                torch.set_rng_state(rng_state["torch_rng_state"])
                torch.cuda.set_rng_state(rng_state["cuda_rng_state"])
                # Check for empty states array
                if not rng_state["rng_tracker_states"]:
                    raise KeyError
                tensor_parallel.get_cuda_rng_tracker().set_states(rng_state["rng_tracker_states"])
            else:  # backward compatibility
                random.setstate(state_dict["random_rng_state"])
                np.random.set_state(state_dict["np_rng_state"])
                torch.set_rng_state(state_dict["torch_rng_state"])
                torch.cuda.set_rng_state(state_dict["cuda_rng_state"])
                # Check for empty states array
                if not state_dict["rng_tracker_states"]:
                    raise KeyError
                tensor_parallel.get_cuda_rng_tracker().set_states(state_dict["rng_tracker_states"])
        except KeyError:
            print_rank_0(
                "Unable to load rng state from checkpoint {}. "
                "Specify --no-load-rng or --finetune to prevent "
                "attempting to load the rng state, "
                "exiting ...".format(checkpoint_name)
            )
            sys.exit()

    # Some utilities want to load a checkpoint without distributed being initialized
    if torch.distributed.is_initialized():
        torch.distributed.barrier()

    print_rank_0(
        f"  successfully loaded checkpoint from {load_dir} "
        f"[ t {mpu.get_tensor_model_parallel_rank() + 1}/{mpu.get_tensor_model_parallel_world_size()}, "
        f"p {mpu.get_pipeline_model_parallel_rank() + 1}/{mpu.get_pipeline_model_parallel_world_size()} ] "
        f"at iteration {state.train_state.step}"
    )

    # Additional callback for wandb (last rank)
    if not torch.distributed.is_initialized() or is_last_rank():
        wandb_utils.on_load_checkpoint_success(checkpoint_name, load_dir, state.wandb_logger)

    torch.cuda.empty_cache()

    if state.train_state.step > 0:
        # Notify FT that a checkpoint was loaded.
        is_local_chkpt = ckpt_type == CheckpointType.LOCAL
        fault_tolerance.on_checkpoint_loaded(is_local_chkpt=is_local_chkpt, global_state=state)

    return state.train_state.step, state.train_state.floating_point_operations_so_far


def init_async_checkpoint_worker(global_state: GlobalState) -> None:
    """Initialize the async checkpoint worker if enabled.

    Creates a persistent background worker for handling asynchronous checkpoint saves
    when both async_save and use_persistent_ckpt_worker are enabled in the configuration.

    Args:
        global_state: The GlobalState instance containing the configuration and async queue.
    """
    from megatron.bridge.utils.common_utils import print_rank_0

    checkpoint_config = global_state.cfg.checkpoint

    if (
        checkpoint_config.save is not None
        and checkpoint_config.async_save
        and checkpoint_config.use_persistent_ckpt_worker
    ):
        # Access the async_calls_queue property to trigger lazy initialization
        # This creates the persistent worker immediately during setup
        _ = global_state.async_calls_queue
        print_rank_0("Initialized persistent async checkpoint worker")


def init_checkpointing_context(checkpoint_config: CheckpointConfig) -> dict[str, Any]:
    """Initialize the checkpointing context, primarily for local checkpointing support.

    If `non_persistent_ckpt_type` is set to "local", this function sets up
    the `LocalCheckpointManager` and replication strategy based on the provided
    `checkpoint_config`.

    Args:
        checkpoint_config: The checkpoint configuration object.

    Returns:
        A dictionary containing the checkpointing context. This will include
        a `local_checkpoint_manager` if local checkpointing is enabled,
        otherwise it will be an empty dictionary.

    Raises:
        RuntimeError: If local checkpointing is configured but the
                      `nvidia_resiliency_ext` module is not found.
    """
    if checkpoint_config.non_persistent_ckpt_type != "local":
        return {}

    if not HAVE_RESIL:
        raise RuntimeError(
            "The 'nvidia_resiliency_ext' module is required for local "
            "checkpointing but was not found. Please ensure it is installed."
        )

    from nvidia_resiliency_ext.checkpointing.local.ckpt_managers.local_manager import LocalCheckpointManager
    from nvidia_resiliency_ext.checkpointing.local.replication.strategies import CliqueReplicationStrategy

    if checkpoint_config.replication:
        repl_strategy = CliqueReplicationStrategy.from_replication_params(
            checkpoint_config.replication_jump,
            checkpoint_config.replication_factor,
        )
    else:
        repl_strategy = None

    checkpointing_context = {
        "local_checkpoint_manager": LocalCheckpointManager(
            checkpoint_config.non_persistent_local_ckpt_dir,
            repl_strategy=repl_strategy,
        )
    }
    return checkpointing_context


def apply_peft_adapter_filter_to_state_dict(state_dict: dict[str, Any], peft_config: PEFT) -> dict[str, Any]:
    """Filter state dict to contain only PEFT adapter parameters in model sections.

    This function takes a complete state dict (generated by generate_state_dict) and
    filters it to retain only PEFT adapter parameters for checkpoint saving.
    Follows the same key logic pattern as generate_state_dict for consistency.

    Args:
        state_dict: Complete state dict from generate_state_dict()
        peft_config: PEFT configuration for filtering logic

    Returns:
        Filtered state dict containing only adapter parameters in model weights,
        while preserving all non-model metadata (checkpoint_version, iteration, etc.)
    """
    return {
        checkpoint_section_key: (
            # Filter model parameters to only include adapter weights
            {
                parameter_name: parameter_value
                for parameter_name, parameter_value in checkpoint_section_value.items()
                if peft_config.adapter_key_filter(parameter_name)
            }
            if _is_model_section(checkpoint_section_key)
            else checkpoint_section_value
        )
        for checkpoint_section_key, checkpoint_section_value in state_dict.items()
    }


def _is_model_section(section_key: str) -> bool:
    """Check if a checkpoint section contains model parameters.

    Model sections are named:
    - "model" (single model)
    - "model0", "model1", etc. (pipeline parallel models)

    Non-model sections include: "optimizer", "iteration", "checkpoint_version", etc.
    """
    is_single_model = section_key == "model"
    is_pipeline_model = (
        section_key.startswith("model")
        and section_key != "model"
        and section_key[5:].isdigit()  # to match virtual pipeline state dict handling
    )
    return is_single_model or is_pipeline_model


def _transpose_first_dim(
    t: torch.Tensor, num_splits: int, num_splits_first: bool, model: torch.nn.Module
) -> torch.Tensor:
    """Helper function to transpose first dimension of tensor t."""
    input_shape = t.size()
    # We use a self_attention module but the values extracted aren't
    # specific to self attention so should work for cross attention as well
    while hasattr(model, "module"):
        model = model.module
    attention_module = model.language_model.encoder.layers[0].self_attention
    hidden_size_per_attention_head = attention_module.hidden_size_per_attention_head
    num_attention_heads_per_partition = attention_module.num_attention_heads_per_partition
    if num_splits_first:
        """[num_splits * np * hn, h]
        -->(view) [num_splits, np, hn, h]
        -->(tranpose) [np, num_splits, hn, h]
        -->(view) [np * num_splits * hn, h]"""

        intermediate_shape = (
            num_splits,
            num_attention_heads_per_partition,
            hidden_size_per_attention_head,
        ) + input_shape[1:]

        t = t.view(*intermediate_shape)
        t = t.transpose(0, 1).contiguous()
    else:
        """[np * hn * num_splits, h]
        -->(view) [np, hn, num_splits, h]
        -->(tranpose) [np, num_splits, hn, h]
        -->(view) [np * num_splits * hn, h]"""

        intermediate_shape = (
            num_attention_heads_per_partition,
            hidden_size_per_attention_head,
            num_splits,
        ) + input_shape[1:]

        t = t.view(*intermediate_shape)
        t = t.transpose(1, 2).contiguous()
    t = t.view(*input_shape)

    return t


def _get_non_persistent_iteration(
    non_persistent_global_dir: str,
    cfg: ConfigContainer,
    checkpointing_context: Optional[dict[str, Any]] = None,
) -> int:
    """Get iteration number from non-persistent checkpoint."""
    if cfg.checkpoint.non_persistent_ckpt_type is None:
        return -1
    elif cfg.checkpoint.non_persistent_ckpt_type == "global":
        train_state_filename = get_checkpoint_train_state_filename(non_persistent_global_dir, prefix=TRACKER_PREFIX)
        if os.path.isfile(train_state_filename):
            train_state = read_train_state(train_state_filename)
            iteration = train_state.step
            # if train_state.release:
            #     raise RuntimeError("Non-persistent checkpoint can't be a release checkpoint")
        else:
            iteration = -1
            print_rank_0("WARNING: could not find the metadata file {}".format(train_state_filename))
            print_rank_0("    will not load any non-persistent checkpoint")
        return iteration
    elif cfg.checkpoint.non_persistent_ckpt_type == "local":
        return checkpointing_context["local_checkpoint_manager"].find_latest()
    else:
        raise ValueError(
            f"Please use local or global non-persistent checkpoints. Got: {cfg.checkpoint.non_persistent_ckpt_type})"
        )


def _load_non_persistent_base_checkpoint(
    non_persistent_global_dir: str,
    cfg: ConfigContainer,
    rank0: bool,
    sharded_state_dict: Optional[dict[str, Any]],
    non_persistent_iteration: int,
    checkpointing_context: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], str, bool, CheckpointType]:
    """Load the base state_dict from a non-persistent distributed checkpoint."""
    assert cfg.checkpoint.non_persistent_ckpt_type is not None
    if cfg.checkpoint.non_persistent_ckpt_type == "global":
        if not rank0:
            print_rank_0(f"Loading from a non-persistent checkpoint (non-persistent iter {non_persistent_iteration})")
        return _load_global_dist_base_checkpoint(
            non_persistent_global_dir,
            cfg,
            rank0,
            sharded_state_dict,
            non_persistent_iteration,
            False,
            checkpointing_context=checkpointing_context,
        )
    elif cfg.checkpoint.non_persistent_ckpt_type == "local":
        intermediate_state_dict, checkpoint_name = checkpointing_context["local_checkpoint_manager"].load()
        state_dict = intermediate_state_dict.to_state_dict(
            sharded_state_dict,
            algo=cfg.checkpoint.non_persistent_local_ckpt_algo,
            parallelization_group=mpu.get_data_parallel_group(with_context_parallel=True),
        )
        return state_dict, checkpoint_name, False, CheckpointType.LOCAL
    else:
        raise ValueError(
            f"Please use local or global non-persistent checkpoints. Got: {cfg.checkpoint.non_persistent_ckpt_type})"
        )


def _load_global_dist_base_checkpoint(
    load_dir: str,
    cfg: ConfigContainer,
    rank0: bool,
    sharded_state_dict: Optional[dict[str, Any]],
    iteration: int,
    release: bool,
    checkpointing_context: Optional[dict[str, Any]] = None,
) -> tuple[dict[str, Any], str, bool, CheckpointType]:
    """Load the base state_dict from the given directory containing the global distributed checkpoint."""
    if rank0:
        checkpoint_name = find_checkpoint_rank_0(load_dir, iteration, release)
        state_dict = dist_checkpointing.load_common_state_dict(checkpoint_name)
        return state_dict, checkpoint_name, release, CheckpointType.GLOBAL

    if sharded_state_dict is None:
        raise RuntimeError("Detected load from a distributed checkpoint, but sharded state dict is not provided.")

    checkpoint_name = get_checkpoint_name(load_dir, iteration, release)
    load_strategy = get_default_load_sharded_strategy(checkpoint_name)
    if cfg.checkpoint.fully_parallel_load:
        load_strategy = FullyParallelLoadStrategyWrapper(
            load_strategy, mpu.get_data_parallel_group(with_context_parallel=True)
        )
    if checkpointing_context is not None:
        checkpointing_context["load_strategy"] = load_strategy
    state_dict = dist_checkpointing.load(
        sharded_state_dict, checkpoint_name, load_strategy, strict=cfg.checkpoint.dist_ckpt_strictness
    )
    return state_dict, checkpoint_name, release, CheckpointType.GLOBAL


def _load_base_checkpoint(
    load_dir: Optional[str],
    cfg: ConfigContainer,
    rank0: bool = False,
    sharded_state_dict: Optional[dict[str, Any]] = None,
    checkpointing_context: Optional[dict[str, Any]] = None,
) -> tuple[Optional[dict[str, Any]], str, bool, Optional[CheckpointType]]:
    """Load the base state_dict from the given directory."""
    # Try to load non-persistent checkpoint first
    non_persistent_global_dir = (
        cfg.checkpoint.non_persistent_global_ckpt_dir
        if cfg.checkpoint.non_persistent_global_ckpt_dir or load_dir is None
        else os.path.join(load_dir, _NON_PERSISTENT_CKPT_SUBDIR)
    )
    non_persistent_iteration = _get_non_persistent_iteration(non_persistent_global_dir, cfg, checkpointing_context)
    iteration, release = -1, False
    tracker_filename = "because load directory is not defined"
    if load_dir is not None:
        tracker_filename = get_checkpoint_train_state_filename(load_dir, prefix=TRACKER_PREFIX)
        if os.path.isfile(tracker_filename):
            train_state = read_train_state(tracker_filename)
            iteration = train_state.step
            # release = train_state.release
    if non_persistent_iteration != -1:  # there is a non-persistent checkpoint
        if non_persistent_iteration >= iteration:
            return _load_non_persistent_base_checkpoint(
                non_persistent_global_dir,
                cfg,
                rank0,
                sharded_state_dict,
                non_persistent_iteration,
                checkpointing_context,
            )
        else:
            print_rank_0("WARNING: non-persistent checkpoints are older than persistent checkpoint")

    # Otherwise we are dealing with global checkpoints
    # If no tracker file, return nothing
    if iteration == -1:
        if not rank0:
            print_rank_0("WARNING: could not find the metadata file {}".format(tracker_filename))
            print_rank_0("    will not load any checkpoints and will start from random")
        # Conditionally exit if checkpoint not found.
        if cfg.checkpoint.exit_on_missing_checkpoint:
            print_rank_0(">> '--exit-on-missing-checkpoint' set ... exiting. <<")
            if torch.distributed.is_initialized():
                torch.distributed.barrier()
            sys.exit()

        return None, "", False, None

    # Determine the type of the checkpoint
    checkpoint_name_dir = get_checkpoint_name(load_dir, iteration, release)
    is_dist_ckpt = dist_checkpointing.check_is_distributed_checkpoint(checkpoint_name_dir)
    if not rank0:
        dist_infix = "distributed " if is_dist_ckpt else ""
        if release:
            print_rank_0(f" loading release {dist_infix}checkpoint from {load_dir}")
        else:
            print_rank_0(f" loading {dist_infix}checkpoint from {load_dir} at iteration {iteration}")

    # Handle global distributed checkpoint
    if is_dist_ckpt:
        return _load_global_dist_base_checkpoint(
            load_dir, cfg, rank0, sharded_state_dict, iteration, release, checkpointing_context=checkpointing_context
        )
    else:
        # This path implies a non-distributed checkpoint, which is no longer supported.
        # All checkpoints should now be distributed (either GLOBAL or LOCAL types).
        raise RuntimeError(
            "Loading non-distributed checkpoints is no longer supported. Please use distributed checkpointing formats."
        )


def _build_sharded_state_dict_metadata(use_distributed_optimizer: bool, ckpt_fully_parallel_save: bool) -> dict:
    """Builds metadata used for sharded_state_dict versioning.

    The whole content metadata is passed to ``shared_state_dict`` model and optimizer methods
    and therefore affects only the logic behind sharded_state_dict creation.
    The content metadata should be minimalistic, ideally flat (or with a single nesting level)
    and with semantically meaningful flag names (e.g. `distrib_optim_sharding_type`).
    In particular, a simple integer (or SemVer) versioning flag (e.g. `metadata['version'] = 3.4`)
    is discouraged, because the metadata serves for all models and optimizers and it's practically
    impossible to enforce a linearly increasing versioning for this whole space.

    Args:
        use_distributed_optimizer: Whether to use distributed optimizer.
        ckpt_fully_parallel_save: Whether to use fully parallel save.
    """
    metadata = {}
    if use_distributed_optimizer:
        if ckpt_fully_parallel_save:
            metadata["distrib_optim_sharding_type"] = "fully_sharded_model_space"
        else:
            metadata["distrib_optim_sharding_type"] = "dp_zero_gather_scatter"
    return metadata
