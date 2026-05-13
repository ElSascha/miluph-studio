# miluph-studio

**miluph-studio** is a browser-based graphical user interface for **miluphcuda**, a GPU-accelerated Smoothed Particle Hydrodynamics (SPH) simulation code written in CUDA C++.

The goal of miluph-studio is to make miluphcuda accessible to users who want to set up, run, and visualize SPH simulations without interacting with the command line.

## How users run it

Users install and launch miluph-studio locally:

```bash
pip install miluph-studio
miluph-studio
```

The app opens automatically in a browser at `http://localhost:8080`, similar to JupyterLab. This setup also works on remote HPC systems using standard SSH port forwarding.

## Architecture

- **Backend (Python + FastAPI)**
  - Starts `miluphcuda` as a subprocess
  - Streams stdout logs to the frontend with Server-Sent Events (SSE)
  - Reads HDF5 output files via `h5py` and `numpy`
  - Serves the built React frontend as static files
- **Frontend (TypeScript + React + Vite)**
  - Uses Three.js for 3D particle visualization

## Core views

1. **Setup** — form-based editing of simulation parameters and configuration files
2. **Run** — start/stop controls, live logs, and diagnostics (for example energy conservation)
3. **Visualize** — 3D rendering of particle output with timestep slider and color mapping (for example density or pressure)

## Key constraints

- Everything runs locally on the user’s machine (no cloud services)
- Users do not need Node.js installed; the built frontend is bundled in the Python package
- The backend locates `miluphcuda` via `$PATH` or a user-defined binary path in settings
- Primary audience: scientists and students using miluphcuda for astrophysical or fluid-dynamics simulations
