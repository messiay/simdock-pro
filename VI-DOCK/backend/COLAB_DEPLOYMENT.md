# Google Colab Backend Guide for VI DOCK Pro 3.1

This guide provides a single script to host your VI DOCK backend on Google Colab for free with **4 vCPUs** and high-speed docking.

## 1. Open Google Colab
Go to [colab.research.google.com](https://colab.research.google.com) and create a **New Notebook**.

## 2. Copy and Paste this Code
Copy the entire block below into the first cell of your Colab notebook and run it (Play button).

> [!IMPORTANT]
> **Copy ONLY the code between the lines.** Do NOT copy the triple backticks (```python) at the start or end.

```python
# === 1. Install System & Molecular Tools ===
print("Installing OpenBabel and system libraries...")
!apt-get update -qq
!apt-get install -y -qq openbabel libxrender1 libxext6 libgl1-mesa-glx > /dev/null

# === 2. Install Python Dependencies ===
print("Installing Python dependencies (FastAPI, RDKit, Meeko)...")
!pip install -q fastapi uvicorn[standard] python-multipart rdkit meeko requests httpx

# === 3. Clone the Project Code ===
import os
if not os.path.exists('simdock-pro'):
    print("Cloning the repository...")
    !git clone https://github.com/messiay/simdock-pro.git
else:
    print("Repository already exists. Updating...")
    %cd simdock-pro
    !git pull
    %cd ..

# Navigate to backend directory
os.chdir('/content/simdock-pro/VI-DOCK/backend')

# === 4. Download Vina and Smina Binaries ===
print("Downloading Vina and Smina...")
!mkdir -p bin
!wget -q https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_linux_x86_64 -O bin/vina
!wget -q https://github.com/gnina/smina/releases/download/v2020.12.10/smina.static -O bin/smina
!chmod +x bin/vina bin/smina

# === 5. Setup Network Tunnel (localtunnel) ===
print("Setting up Localtunnel...")
!npm install -g localtunnel -q > /dev/null

# === 6. Start the API Server ===
import subprocess
import time

print("\nStarting VI DOCK API Server...")
# Start uvicorn in the background
proc = subprocess.Popen(["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"], 
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

# Wait for server to be ready
time.sleep(5)

# === 7. Expose it to the Web ===
print("\n--- DEPLOYMENT COMPLETE ---")
print("1. Your 'Password' for the Tunnel link below is your Colab Instance IP.")
print("2. Run the command below in a NEW cell to see your Tunnel Password:")
print("   !curl ipv4.icanhazip.com")
print("3. Click the link provided by 'lt' below.")

# Run localtunnel
!lt --port 8000
```

## 3. How to Connect
1.  When you run the script, it will print a link (e.g., `https://forty-humans-like.loca.lt`).
2.  **IP Verification**: If the link asks for a password, run `!curl ipv4.icanhazip.com` in a new Colab cell to get the IP, and paste it in the website.
3.  **Update Frontend**: Copy the URL and set it as your `VITE_API_BASE_URL` in Vercel or your local `.env` file.

## ⚠️ Important
Keep the Colab tab open. If the notebook disconnects, the backend will stop. You can reconnect and run the cell again at any time to get a new URL.
