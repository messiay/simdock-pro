
import os
import subprocess
from pathlib import Path

def debug_autodock_run():
    # Setup paths
    base_dir = Path.cwd()
    bin_dir = base_dir / "bin"
    executable = bin_dir / "vina_gpu.exe"
    
    print(f"DEBUG: Checking for executable at: {executable}")
    if not executable.exists():
        print("ERROR: Executable not found!")
        return

    # Check for Kernel file
    kernel_file = bin_dir / "Kernel2_Opt.bin"
    if not kernel_file.exists():
        print("WARNING: Kernel2_Opt.bin not found in bin directory! This is likely the cause of silent failure.")
    else:
        print("DEBUG: Kernel2_Opt.bin found.")

    # Create dummy PDBQT files for testing if they don't exist
    # (We assume the user has some actual files, but for reproduction we need something valid-ish)
    # Actually, let's try to run a command that fails fast if files are missing, 
    # OR we can try to use the --help command to at least see if it runs fully.
    
    print("\nAttempting to run --help...")
    try:
        result = subprocess.run([str(executable), "--help"], capture_output=True, text=True)
        print("STDOUT:", result.stdout[:200]) # First 200 chars
        print("STDERR:", result.stderr[:200])
        print("Return Code:", result.returncode)
    except Exception as e:
        print(f"CRITICAL: Failed to run --help: {e}")

    # Now let's try a fake docking command to simulate the crash
    # We need paths to exist or Vina will just error out early.
    # Let's create empty dummy files
    rec_file = base_dir / "dummy_rec.pdbqt"
    lig_file = base_dir / "dummy_lig.pdbqt"
    
    with open(rec_file, "w") as f:
        f.write("ATOM      1  N   MET A   1      10.000  10.000  10.000  1.00  0.00     0.027 N\n")
    with open(lig_file, "w") as f:
        f.write("ATOM      1  C   LIG A   1      12.000  12.000  12.000  1.00  0.00     0.000 C\n")
        f.write("TORSDOF 0\n")

    print("\nAttempting simulated docking run...")
    cmd = [
        str(executable),
        "--receptor", str(rec_file),
        "--ligand", str(lig_file),
        "--center_x", "10", "--center_y", "10", "--center_z", "10",
        "--size_x", "15", "--size_y", "15", "--size_z", "15",
        "--search_depth", "8",
        "--thread", "1000"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    # Run inside the BIN directory just in case it needs the Kernel file in CWD
    try:
        os.chdir(bin_dir)
        print(f"CWD changed to: {os.getcwd()}")
        
        # Adjust paths to be absolute since we moved cwd
        cmd[1] = str(rec_file)
        cmd[3] = str(lig_file)
        cmd[0] = "./vina_gpu.exe"
        
        # Run with timeout to catch hanging
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        print("STDOUT:")
        print(result.stdout)
        print("STDERR:")
        print(result.stderr)
        print("Return Code:", result.returncode)
        
    except subprocess.TimeoutExpired:
        print("CRITICAL: Process timed out! It is hanging.")
    except Exception as e:
        print(f"CRITICAL: Execution failed: {e}")
    finally:
        # Cleanup
        os.chdir(base_dir)
        if rec_file.exists(): rec_file.unlink()
        if lig_file.exists(): lig_file.unlink()

if __name__ == "__main__":
    debug_autodock_run()
