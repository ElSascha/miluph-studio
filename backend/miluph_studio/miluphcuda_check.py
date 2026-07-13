import subprocess
from pathlib import Path

from backend.miluph_studio.config import MiluphcudaInstance


# Check if the miluphcuda binary exists and is reachable for a given instance
def check_local(instance: MiluphcudaInstance) -> dict:
    if not instance.path:
        return {"reachable": False, "binary_exists": False, "makefile_exists": False}

    base_path = Path(instance.path)
    binary = base_path / "miluphcuda"
    return {
        "reachable": True,
        "binary_exists": binary.exists(),
        "makefile_exists": (base_path / "Makefile").exists(),
    }


def check_remote(instance: MiluphcudaInstance) -> dict:
    # Check if the miluphcuda binary exists and is reachable for a given instance via SSH
    if not instance.user or not instance.host or not instance.remote_path:
        return {"reachable": False, "binary_exists": False, "makefile_exists": False}

    ssh_command = [
        "ssh",
        f"{instance.user}@{instance.host}",
        f"test -f {instance.remote_path}/miluphcuda && echo 'exists' || echo 'not exists'",
    ]
    try:
        result = subprocess.run(ssh_command, capture_output=True, text=True, timeout=10)
        binary_exists = result.stdout.strip() == "exists"
        return {
            "reachable": True,
            "binary_exists": binary_exists,
            "makefile_exists": False,  # Not checking for Makefile on remote for now
        }
    except subprocess.TimeoutExpired:
        return {"reachable": False, "binary_exists": False, "makefile_exists": False}