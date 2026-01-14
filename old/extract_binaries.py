import zipfile
import os
import shutil

zip_path = "bin/qvina_repo.zip"
extract_dir = "bin"

with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    for file in zip_ref.namelist():
        if file.endswith("qvina-master/bin/qvina02_win32.exe"):
            print(f"Extracting {file}...")
            source = zip_ref.open(file)
            target = open(os.path.join(extract_dir, "qvina.exe"), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
            print("Extracted qvina.exe")
            
        elif file.endswith("qvina-master/bin/vina.exe"):
            print(f"Extracting {file}...")
            source = zip_ref.open(file)
            target = open(os.path.join(extract_dir, "vina.exe"), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
            print("Extracted vina.exe")

print("Extraction complete.")
