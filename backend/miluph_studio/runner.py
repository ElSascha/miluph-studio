from backend.miluph_studio.config import MiluphcudaInstance

def build_run_command(instance: MiluphcudaInstance, sim_args: str) -> list[str]:
    if instance.mode == "local":
        if instance.executor == "direct":
            return [f"{instance.path}/miluphcuda", sim_args]
        elif instance.executor == "slurm":
            return ["sbatch", "-p", instance.slurm_partition, f"{instance.path}/miluphcuda", sim_args]
    elif instance.mode == "remote_ssh":
        ssh_command = [
            "ssh",
            f"{instance.user}@{instance.host}",
            f"cd {instance.remote_path} && "
        ]
        if instance.executor == "direct":
            ssh_command.append(f"./miluphcuda {sim_args}")
        elif instance.executor == "slurm":
            ssh_command.append(f"sbatch -p {instance.slurm_partition} ./miluphcuda {sim_args}")
        return ssh_command
    else:
        raise ValueError(f"Unknown mode: {instance.mode}")