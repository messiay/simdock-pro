import sys
print(f"Python: {sys.version}")

packages = ["openbabel", "rdkit", "numba", "fastapi", "uvicorn", "pydantic", "celery", "redis"]

for pkg in packages:
    try:
        if pkg == "openbabel":
            from openbabel import pybel
        else:
            __import__(pkg)
        print(f"{pkg}: Installed")
    except ImportError:
        print(f"{pkg}: Missing")
    except Exception as e:
        print(f"{pkg}: Error ({e})")
