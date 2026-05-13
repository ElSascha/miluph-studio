from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import subprocess
import asyncio

app = FastAPI()

process = None

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/simulation/start")
async def start_simulation():
    global process
    if process and process.poll() is None:
        return {"status": "Simulation already running"}
    
    process = subprocess.Popen(
        ["echo", "miluphcuda starting ..."],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return {"status": "Simulation started"}


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