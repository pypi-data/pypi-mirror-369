import gzip
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, List, Optional, TypeVar

import datasets
import importlib_resources
import torch.distributed as dist
from importlib_resources.abc import Traversable


def _get_data_traversable(data_rel_path: str) -> Traversable:
    return importlib_resources.files("olmo_eval").joinpath(data_rel_path)


def is_data_dir(data_rel_path: str) -> bool:
    return _get_data_traversable(data_rel_path).is_dir()


def is_data_file(data_rel_path: str) -> bool:
    return _get_data_traversable(data_rel_path).is_file()


@contextmanager
def get_data_path(data_rel_path: str) -> Generator[Path, None, None]:
    try:
        with importlib_resources.as_file(_get_data_traversable(data_rel_path)) as path:
            yield path
    finally:
        pass


def load_hf_dataset(path: str, name: Optional[str], split: str):
    """
    Loads a HuggingFace dataset. The dataset is assumed to be saved using
    `save_hf_dataset_to_disk` and located in `olmo_data/hf_datasets`.
    """
    dataset_rel_path = os.path.join("hf_datasets", path, name or "none", split)
    with get_data_path(dataset_rel_path) as dataset_path:
        if not dataset_path.is_dir():
            raise NotADirectoryError(
                f"HF dataset {path} name {name} split {split} not found in directory {dataset_rel_path}"
            )
        return datasets.load_from_disk(str(dataset_path))


def load_oe_eval_requests(path: str, name: Optional[str] = None, split: Optional[str] = None):
    """
    Loads an oe-eval request file from this package.
    TODO: Add support from loading from S3 instead?
    """
    dataset_rel_path = os.path.join("oe_eval_tasks", path)
    if name is not None:
        dataset_rel_path = os.path.join(dataset_rel_path, name)
    with get_data_path(dataset_rel_path) as dataset_path:
        if not dataset_path.is_dir():
            raise NotADirectoryError(f"OE Eval dataset not found in directory {dataset_rel_path}")
        data_file = dataset_path / "requests.jsonl.gz"
        if not data_file.is_file():
            data_file = dataset_path / "requests.jsonl"
        if not data_file.is_file():
            raise FileNotFoundError(
                f"OE Eval dataset file requests-{split}.jsonl(.gz) missing in directory {dataset_rel_path}"
            )
        requests = []
        if data_file.suffix == ".gz":
            with gzip.open(data_file, "r") as file:
                for line in file:
                    requests.append(json.loads(line.decode("utf-8").strip()))
        else:
            with open(data_file, "r") as file:
                for line2 in file:
                    requests.append(json.loads(line2.strip()))
        config = None
        config_file = dataset_path / "config.json"
        if config_file.is_file():
            with open(config_file, "r") as file:
                config = json.load(file)
        return config, requests


def is_distributed() -> bool:
    """
    Check if in a distributed context.
    """
    return dist.is_available() and dist.is_initialized()


def get_world_size(group: Optional[dist.ProcessGroup] = None) -> int:
    """
    Get the world size of the default distributed process group.

    .. warning::
        This will always return 1 if a distributed group has not been initialized.
    """
    if is_distributed():
        return dist.get_world_size(group)
    else:
        return 0


T = TypeVar("T")


def all_gather_object(obj: T, group: Optional[dist.ProcessGroup] = None) -> List[T]:
    """
    All-gather an object using pickle to all ranks in a process group.
    """
    if not is_distributed():
        return [obj]

    output_list = [obj] * get_world_size(group)
    dist.all_gather_object(output_list, obj, group=group)
    return output_list
