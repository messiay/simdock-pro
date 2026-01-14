
import zipfile
import os

zip_path = "bin/qvina_repo.zip"

if os.path.exists(zip_path):
    print(f"Listing contents of {zip_path}:")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if "exe" in file:
                print(file)
else:
    print(f"File not found: {zip_path}")
