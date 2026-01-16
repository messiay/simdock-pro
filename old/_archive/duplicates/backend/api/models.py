from pydantic import BaseModel, Field
from typing import List, Optional, Tuple, Dict, Any, Literal

class ProjectCreate(BaseModel):
    name: str = Field(..., description="Name of the project")
    description: Optional[str] = Field(None, description="Project description")

class ProjectResponse(BaseModel):
    name: str
    path: str
    files: List[str]
    receptors: List[str] = []
    ligands: List[str] = []

class GridBoxConfig(BaseModel):
    center_x: float
    center_y: float
    center_z: float
    size_x: float
    size_y: float
    size_z: float

class DockingConfig(BaseModel):
    engine: Literal["vina", "smina"] = Field("vina", description="Docking engine to use (allowed: 'vina', 'smina')")
    receptor_file: str = Field(..., description="Filename of receptor in project")
    ligand_file: str = Field(..., description="Filename of ligand in project")
    config: GridBoxConfig
    exhaustiveness: int = Field(8, gt=0, description="Search exhaustiveness (must be > 0)")
    num_modes: int = Field(9, gt=0, description="Max binding modes (must be > 0)")
    energy_range: float = Field(3.0, gt=0, description="Energy range (kcal/mol)")

class JobResponse(BaseModel):
    job_id: str
    status: str
    project_name: str
    engine: str
    error: Optional[str] = None

class BatchDockingConfig(BaseModel):
    engine: Literal["vina", "smina"] = Field("vina", description="Docking engine (allowed: 'vina', 'smina')")
    receptor_file: str = Field(..., description="Receptor filename")
    ligands_zip: str = Field(..., description="Uploaded ZIP filename containing ligands")
    config: GridBoxConfig
    exhaustiveness: int = Field(8, gt=0, description="Search exhaustiveness")

class GridBoxResponse(BaseModel):
    center_x: float
    center_y: float
    center_z: float
    size_x: float
    size_y: float
    size_z: float
    notes: Optional[str] = None
