"""
Conversion Routes - PDB to PDBQT using OpenBabel
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import tempfile
import os
import subprocess

from utils.config import OBABEL_PATH

router = APIRouter()

class ConversionRequest(BaseModel):
    pdb_content: str
    add_hydrogens: bool = True
    
class ConversionResponse(BaseModel):
    pdbqt_content: str
    success: bool
    message: str

@router.post("/pdb-to-pdbqt", response_model=ConversionResponse)
async def convert_pdb_to_pdbqt(request: ConversionRequest):
    """
    Convert PDB content to PDBQT format using OpenBabel.
    
    This performs proper:
    - Gasteiger partial charge calculation
    - AutoDock atom type assignment
    - Hydrogen addition (optional)
    """
    if not OBABEL_PATH or not os.path.exists(OBABEL_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"OpenBabel not found at {OBABEL_PATH}. Please install OpenBabel."
        )
    
    try:
        # Create temp files
        with tempfile.TemporaryDirectory() as temp_dir:
            input_pdb = os.path.join(temp_dir, "input.pdb")
            output_pdbqt = os.path.join(temp_dir, "output.pdbqt")
            
            # Write input PDB
            with open(input_pdb, 'w') as f:
                f.write(request.pdb_content)
            
            # Build OpenBabel command
            # -ipdb: input format PDB
            # -opdbqt: output format PDBQT
            # -xr: receptor mode (no torsions)
            # --partialcharge gasteiger: calculate Gasteiger charges
            cmd = [
                OBABEL_PATH,
                "-ipdb", input_pdb,
                "-opdbqt", "-O", output_pdbqt,
                "-xr",  # Receptor mode
                "--partialcharge", "gasteiger"
            ]
            
            # Add hydrogens if requested
            if request.add_hydrogens:
                cmd.insert(3, "-h")  # Add hydrogens
            
            # Run OpenBabel
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown OpenBabel error"
                raise HTTPException(
                    status_code=500,
                    detail=f"OpenBabel conversion failed: {error_msg}"
                )
            
            # Read output
            if not os.path.exists(output_pdbqt):
                raise HTTPException(
                    status_code=500,
                    detail="OpenBabel did not produce output file"
                )
            
            with open(output_pdbqt, 'r') as f:
                pdbqt_content = f.read()
            
            if not pdbqt_content.strip():
                raise HTTPException(
                    status_code=500,
                    detail="OpenBabel produced empty output"
                )
            
            return ConversionResponse(
                pdbqt_content=pdbqt_content,
                success=True,
                message=f"Successfully converted PDB to PDBQT ({len(pdbqt_content)} bytes)"
            )
            
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=504,
            detail="OpenBabel conversion timed out"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Conversion error: {str(e)}"
        )


class SdfConversionRequest(BaseModel):
    sdf_content: str
    add_hydrogens: bool = True

@router.post("/sdf-to-pdbqt", response_model=ConversionResponse)
async def convert_sdf_to_pdbqt(request: SdfConversionRequest):
    """
    Convert SDF/MOL content to PDBQT format using OpenBabel.
    Suitable for ligand preparation.
    """
    if not OBABEL_PATH or not os.path.exists(OBABEL_PATH):
        raise HTTPException(
            status_code=500, 
            detail=f"OpenBabel not found at {OBABEL_PATH}."
        )
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_sdf = os.path.join(temp_dir, "input.sdf")
            output_pdbqt = os.path.join(temp_dir, "output.pdbqt")
            
            with open(input_sdf, 'w') as f:
                f.write(request.sdf_content)
            
            # Ligand mode (no -xr flag)
            cmd = [
                OBABEL_PATH,
                "-isdf", input_sdf,
                "-opdbqt", "-O", output_pdbqt,
                "--partialcharge", "gasteiger"
            ]
            
            if request.add_hydrogens:
                cmd.insert(3, "-h")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"OpenBabel failed: {result.stderr}")
            
            if not os.path.exists(output_pdbqt):
                raise HTTPException(status_code=500, detail="OpenBabel did not produce output")
            
            with open(output_pdbqt, 'r') as f:
                pdbqt_content = f.read()
            
            return ConversionResponse(
                pdbqt_content=pdbqt_content,
                success=True,
                message=f"Converted SDF to PDBQT ({len(pdbqt_content)} bytes)"
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Conversion timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


class SmilesConversionRequest(BaseModel):
    smiles: str
    name: str = "ligand"

@router.post("/smiles-to-pdbqt", response_model=ConversionResponse)
async def convert_smiles_to_pdbqt(request: SmilesConversionRequest):
    """
    Convert SMILES string to 3D PDBQT using OpenBabel.
    Generates 3D coordinates and calculates charges.
    """
    if not OBABEL_PATH or not os.path.exists(OBABEL_PATH):
        raise HTTPException(status_code=500, detail="OpenBabel not found.")
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            input_smi = os.path.join(temp_dir, "input.smi")
            output_pdbqt = os.path.join(temp_dir, "output.pdbqt")
            
            with open(input_smi, 'w') as f:
                f.write(f"{request.smiles} {request.name}")
            
            # Generate 3D with --gen3d
            cmd = [
                OBABEL_PATH,
                "-ismi", input_smi,
                "-opdbqt", "-O", output_pdbqt,
                "--gen3d",  # Generate 3D coordinates
                "-h",       # Add hydrogens
                "--partialcharge", "gasteiger"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                raise HTTPException(status_code=500, detail=f"OpenBabel failed: {result.stderr}")
            
            if not os.path.exists(output_pdbqt):
                raise HTTPException(status_code=500, detail="OpenBabel did not produce output")
            
            with open(output_pdbqt, 'r') as f:
                pdbqt_content = f.read()
            
            return ConversionResponse(
                pdbqt_content=pdbqt_content,
                success=True,
                message=f"Converted SMILES to 3D PDBQT ({len(pdbqt_content)} bytes)"
            )
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=504, detail="Conversion timed out")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")
