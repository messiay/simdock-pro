import os
import subprocess
import sys
import shutil
from pathlib import Path

def build_executable():
    """Build the SimDock Pro standalone executable."""
    print("Starting build process...")
    
    # Check for PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("PyInstaller not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Define paths
    base_dir = Path(".").resolve()
    bin_dir = base_dir / "bin"
    assets_dir = base_dir / "assets" # Assuming assets exist, otherwise we skip
    icon_path = base_dir / "assets" / "icon.ico" # Example icon path
    
    # separator for add-data (semicolon for Windows)
    sep = ";" if os.name == 'nt' else ":"
    
    # Build command
    cmd = [
        "pyinstaller",
        "--name=SimDockPro",
        "--onefile",
        "--windowed",  # No console window
        "--clean",
        f"--paths={base_dir}", # Explicitly add current directory to search path
        # Add bin folder
        f"--add-data={bin_dir}{sep}bin",
        # Force collect everything from core and gui
        "--collect-all=core",
        "--collect-all=gui",
        "--collect-all=utils",
        # Specific hidden imports just in case
        "--hidden-import=PIL._tkinter_finder", 
        "--hidden-import=installer_logic",
        "--hidden-import=multiprocessing",
        "--collect-all=customtkinter",
        "main.py"
    ]
    
    # Add icon if exists
    if icon_path.exists():
        cmd.insert(3, f"--icon={icon_path}")
        
    print(f"Running command: {' '.join(str(c) for c in cmd)}")
    
    try:
        subprocess.run(cmd, check=True)
        print("\nBuild successful!")
        print(f"Executable is located in: {base_dir / 'dist' / 'SimDockPro.exe'}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed: {e}")

if __name__ == "__main__":
    build_executable()
