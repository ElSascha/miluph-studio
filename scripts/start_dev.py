#!/usr/bin/env python3
import os
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = ROOT / "backend" / "miluph_studio"
FRONTEND_DIR = ROOT / "frontend"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def ensure_prerequisites() -> None:
    if not VENV_PYTHON.exists():
        raise FileNotFoundError("Virtual environment not found. Run: python3 -m venv .venv")
    if not (FRONTEND_DIR / "package.json").exists():
        raise FileNotFoundError("Frontend folder not found")


def stream_output(process: subprocess.Popen[str], name: str) -> None:
    assert process.stdout is not None
    for line in process.stdout:
        print(f"[{name}] {line.rstrip()}")
        sys.stdout.flush()


def main() -> None:
    ensure_prerequisites()

    backend_cmd = [
        str(VENV_PYTHON),
        "-m",
        "uvicorn",
        "backend.miluph_studio.server:app",
        "--reload",
        "--reload-dir",
        str(BACKEND_DIR),
        "--port",
        "8080",
    ]
    frontend_cmd = ["npm", "run", "dev", "--", "--host", "127.0.0.1"]

    print("Starting backend and frontend...")

    backend = subprocess.Popen(
        backend_cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    frontend = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    threads = [
        threading.Thread(target=stream_output, args=(backend, "backend"), daemon=True),
        threading.Thread(target=stream_output, args=(frontend, "frontend"), daemon=True),
    ]
    for thread in threads:
        thread.start()

    def shutdown(signum: int, _frame: object) -> None:
        print("\nStopping services...")
        for proc in (backend, frontend):
            if proc.poll() is None:
                proc.terminate()
        for proc in (backend, frontend):
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while backend.poll() is None and frontend.poll() is None:
            time.sleep(1)
    except KeyboardInterrupt:
        shutdown(signal.SIGINT, None)

    # NEU: sauber aufräumen statt nur zu loggen
    if backend.poll() is not None:
        print(f"Backend exited unexpectedly (code {backend.returncode})")
    if frontend.poll() is not None:
        print(f"Frontend exited unexpectedly (code {frontend.returncode})")

    shutdown(signal.SIGINT, None)  # beendet den jeweils anderen noch laufenden Prozess

    if backend.poll() is not None:
        print(f"Backend exited unexpectedly (code {backend.returncode})")
    if frontend.poll() is not None:
        print(f"Frontend exited unexpectedly (code {frontend.returncode})")


if __name__ == "__main__":
    main()
