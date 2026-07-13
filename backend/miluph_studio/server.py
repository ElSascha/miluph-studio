import sys
import subprocess
from pathlib import Path
from typing import Optional

import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response, StreamingResponse

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.miluph_studio.config import MiluphcudaInstance, load_instances
from backend.miluph_studio.file_templates import (
    DEFAULT_MILUPHCUDA_CONFIG,
    DEFAULT_PARAMETER_H,
    load_miluphcuda_config,
    read_text_file,
    write_miluphcuda_config,
    write_parameter_header,
)
from backend.miluph_studio.miluphcuda_check import check_local, check_remote

app = FastAPI()
CONFIG_PATH = ROOT_DIR / "config.yaml"
process = None


def resolve_parameter_header_target(instance_name: Optional[str], config_path: Optional[Path] = None, fallback_path: Optional[Path] = None) -> Path:
    target_path = fallback_path or (ROOT_DIR / "parameter.h")
    if not instance_name:
        return target_path

    config_file = config_path or CONFIG_PATH
    if not config_file.exists():
        return target_path

    instances = load_instances(config_file)
    instance = next((item for item in instances if item.name == instance_name), None)
    if not instance:
        return target_path

    if instance.mode == "local" and instance.path:
        return Path(instance.path) / "parameter.h"

    if instance.mode == "remote_ssh" and instance.remote_path:
        return Path(instance.remote_path) / "parameter.h"

    return target_path


def resolve_config_target(instance_name: Optional[str], config_path: Optional[Path] = None, fallback_path: Optional[Path] = None) -> Path:
    target_path = fallback_path or (ROOT_DIR / "material.cfg")
    if not instance_name:
        return target_path

    config_file = config_path or CONFIG_PATH
    if not config_file.exists():
        return target_path

    instances = load_instances(config_file)
    instance = next((item for item in instances if item.name == instance_name), None)
    if not instance:
        return target_path

    if instance.mode == "local" and instance.path:
        project_dir = Path(instance.path)
        simulation_dir = project_dir / "simulation"
        simulation_dir.mkdir(parents=True, exist_ok=True)
        return simulation_dir / "material.cfg"

    if instance.mode == "remote_ssh" and instance.remote_path:
        return Path(instance.remote_path) / "simulation" / "material.cfg"

    return target_path


@app.get("/")
def root():
    return {"status": "ok", "service": "miluph-studio"}


@app.get("/favicon.ico")
def favicon():
    return Response(status_code=204)


@app.get("/apple-touch-icon.png")
@app.get("/apple-touch-icon-precomposed.png")
def apple_touch_icon():
    return Response(status_code=204)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/simulation/start")
async def start_simulation(request: Request):
    global process
    if process and process.poll() is None:
        return {"status": "Simulation already running"}

    payload = await request.json() if request.headers.get("content-length") else {}
    instance_name = payload.get("instance_name") if isinstance(payload, dict) else None

    if instance_name:
        instances = load_instances(CONFIG_PATH)
        selected = next((item for item in instances if item.name == instance_name), None)
        if selected is None:
            raise HTTPException(status_code=404, detail="Installation not found")

    process = subprocess.Popen(
        ["echo", f"miluphcuda starting for {instance_name or 'default'} ..."],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {"status": "Simulation started", "instance": instance_name or "default"}


@app.post("/api/simulation/status")
def get_status():
    if process is None:
        return {"status": "No simulation running"}
    if process.poll() is None:
        return {"status": "Simulation running"}
    return {"status": "Simulation finished"}


@app.post("/api/simulation/stop")
def stop_simulation():
    global process
    if process and process.poll() is None:
        process.terminate()
        return {"status": "Simulation stopped"}
    return {"status": "No simulation running"}


@app.get("/api/simulation/logs")
async def stream_logs():
    if process is None:
        return {"error": "no simulation running"}

    def generate():
        for line in iter(process.stdout.readline, b""):
            yield f"data: {line.decode()}\n\n"

    return StreamingResponse(generate(), media_type="text/event-stream")


@app.get("/api/instances")
def list_instances():
    instances = load_instances(CONFIG_PATH)
    result = []
    for instance in instances:
        status = check_local(instance) if instance.mode == "local" else check_remote(instance)
        result.append({"instance": instance.model_dump(exclude_none=True), "status": status})
    return result


@app.get("/api/templates/parameter-h")
def get_parameter_header(instance_name: Optional[str] = None):
    path = resolve_parameter_header_target(instance_name)
    return {"content": read_text_file(path, DEFAULT_PARAMETER_H), "target": str(path)}


@app.post("/api/templates/parameter-h")
def update_parameter_header(payload: dict):
    instance_name = payload.get("instance_name")
    target_path = resolve_parameter_header_target(instance_name)

    values = {key: value for key, value in payload.items() if key != "instance_name"}
    content = write_parameter_header(target_path, values)

    if payload.get("instance_name"):
        fallback_path = ROOT_DIR / "parameter.h"
        write_parameter_header(fallback_path, values)

    return {"status": "ok", "content": content, "target": str(target_path)}


@app.get("/api/templates/miluphcuda-config")
def get_miluphcuda_config(instance_name: Optional[str] = None):
    path = resolve_config_target(instance_name, fallback_path=ROOT_DIR / "material.cfg")
    values = load_miluphcuda_config(path, DEFAULT_MILUPHCUDA_CONFIG)
    content = read_text_file(path, "")
    if not content:
        content = write_miluphcuda_config(path, values)
    return {"content": content, "values": values, "target": str(path)}


@app.post("/api/templates/miluphcuda-config")
def update_miluphcuda_config(payload: dict):
    instance_name = payload.get("instance_name")
    target_path = resolve_config_target(instance_name, fallback_path=ROOT_DIR / "material.cfg")
    values = {key: value for key, value in payload.items() if key != "instance_name"}
    content = write_miluphcuda_config(target_path, values)

    if payload.get("instance_name"):
        fallback_path = ROOT_DIR / "material.cfg"
        write_miluphcuda_config(fallback_path, values)

    return {"status": "ok", "content": content, "target": str(target_path)}


@app.post("/api/instances")
def add_instance(instance: MiluphcudaInstance):
    if instance.mode == "local" and not instance.path:
        raise HTTPException(status_code=400, detail="Local installations need a path")
    if instance.mode == "remote_ssh" and (not instance.host or not instance.user or not instance.remote_path):
        raise HTTPException(status_code=400, detail="Remote SSH installations need host, user and remote_path")

    if not CONFIG_PATH.exists():
        data = {"miluphcuda_instances": []}
    else:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {"miluphcuda_instances": []}

    existing = data.get("miluphcuda_instances") or []
    if any(item.get("name") == instance.name for item in existing):
        raise HTTPException(status_code=400, detail="Name already taken")

    existing.append(instance.model_dump(exclude_none=True))
    data["miluphcuda_instances"] = existing

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False)

    return {"status": "ok"}