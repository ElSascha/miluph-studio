from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


class MiluphcudaInstance(BaseModel):
    name: str
    mode: str  # "local" or "remote_ssh"
    path: Optional[str] = None  # None if mode is "remote_ssh"
    host: Optional[str] = None  # None if mode is "local"
    user: Optional[str] = None  # None if mode is "local"
    remote_path: Optional[str] = None  # None if mode is "local"
    executor: str = "direct"  # "direct" or "slurm"
    slurm_partition: Optional[str] = None  # None if executor is "direct"


def load_instances(config_path: Path) -> list[MiluphcudaInstance]:
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    raw_instances = data.get("miluphcuda_instances") or data.get("instances", [])
    return [MiluphcudaInstance(**instance) for instance in raw_instances]
