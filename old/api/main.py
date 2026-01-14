from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from api.routes import projects, docking, analysis, system
from core.project_manager import ProjectManager

app = FastAPI(
    title="SimDock Pro 3.1 API",
    description="REST API for SimDock Pro Desktop Backend",
    version="3.1.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (Project Data) for Visualization
projects_dir = Path("SimDock_Projects").resolve()
projects_dir.mkdir(exist_ok=True)
app.mount("/files", StaticFiles(directory=str(projects_dir)), name="files")

# Include Routers
app.include_router(projects.router, prefix="/projects", tags=["Projects"])
app.include_router(docking.router, prefix="/docking", tags=["Docking"])
app.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(system.router, prefix="/system", tags=["System"])

@app.get("/")
def read_root():
    return {"status": "online", "service": "SimDock Pro 3.1 API"}
