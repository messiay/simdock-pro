r# Database Integration Walkthrough

## Overview
We have introduced a lightweight SQLite database integration (`project.db`) for each project to efficiently store docking results and session metadata. This replaces the reliance on scattered CSV files for data persistence while maintaining the ability to export results to CSV for analysis.

## Changes

### 1. Core: Database Manager
**File:** `core/database_manager.py`
- Created a new `DatabaseManager` class.
- Handles initialization of `project.db` with `sessions` and `results` tables.
- Provides methods to:
    - `save_session`: Save session metadata and all docking results (poses, scores, parameters).
    - `get_session_results`: Retrieve results for a session.
    - `export_to_csv`: Export results to a CSV file.

### 2. Core: Project Manager Integration
**File:** `core/project_manager.py`
- Integrated `DatabaseManager` into `ProjectManager`.
- Automatically initializes the database when creating or loading a project.
- Saves every docking session to the database automatically upon completion.

### 3. GUI: Selective CSV Export
**File:** `gui/components.py` (`ResultsTab`)
- Updated the Results tab to support **selective export**.
- Users can now select specific rows in the batch results table (e.g., specific ligand-receptor pairs).
- Clicking "Save Results" will:
    - If rows are selected: Export detailed results (all modes) for the selected pairs.
    - If no rows are selected: Export detailed results for the entire batch.
- The exported CSV now includes comprehensive data:
    - Receptor & Ligand names
    - Mode index
    - Affinity (kcal/mol)
    - RMSD values
    - Engine used
    - Output file paths
r# Database Integration Walkthrough

## Overview
We have introduced a lightweight SQLite database integration (`project.db`) for each project to efficiently store docking results and session metadata. This replaces the reliance on scattered CSV files for data persistence while maintaining the ability to export results to CSV for analysis.

## Changes

### 1. Core: Database Manager
**File:** `core/database_manager.py`
- Created a new `DatabaseManager` class.
- Handles initialization of `project.db` with `sessions` and `results` tables.
- Provides methods to:
    - `save_session`: Save session metadata and all docking results (poses, scores, parameters).
    - `get_session_results`: Retrieve results for a session.
    - `export_to_csv`: Export results to a CSV file.

### 2. Core: Project Manager Integration
**File:** `core/project_manager.py`
- Integrated `DatabaseManager` into `ProjectManager`.
- Automatically initializes the database when creating or loading a project.
- Saves every docking session to the database automatically upon completion.

### 3. GUI: Selective CSV Export
**File:** `gui/components.py` (`ResultsTab`)
- Updated the Results tab to support **selective export**.
- Users can now select specific rows in the batch results table (e.g., specific ligand-receptor pairs).
- Clicking "Save Results" will:
    - If rows are selected: Export detailed results (all modes) for the selected pairs.
    - If no rows are selected: Export detailed results for the entire batch.
- The exported CSV now includes comprehensive data:
    - Receptor & Ligand names
    - Mode index
    - Affinity (kcal/mol)
    - RMSD values
    - Engine used
    - Output file paths

## Verification
- Verified the database schema creation and data insertion using a test script.
- Verified that results can be retrieved and exported to CSV format correctly.
- The CSV output contains both the normalized database fields and the original full parameter set.

## 3. Auto-Installer & Standalone Executable

SimDock Pro is now a fully portable, self-contained application.

### Features
*   **Standalone EXE**: The `SimDockPro.exe` file contains all necessary code and docking engines (Smina, Vina, LeDock, etc.).
*   **Auto-Installation**: On first run, the application checks for required external tools (**ChimeraX** and **OpenBabel**).
*   **One-Click Setup**: If dependencies are missing, a "First Time Setup" dialog appears to automatically download and install them silently.

### How to Build
To generate the standalone executable yourself:
1.  Open a terminal in the project directory.
2.  Run the build script:
    ```bash
    python build_exe.py
    ```
3.  The executable will be created in the `dist` folder.

### How to Use
1.  Share the `SimDockPro.exe` file.
2.  Double-click to run.
3.  Follow the prompts if it's the first time running on a new machine.

## How to Use
1. **Run Docking**: Perform single or batch docking as usual.
2. **View Results**: Go to the "Results" tab.
3. **Select Results**: Click to select rows in the results table (hold Ctrl/Shift for multiple).
4. **Export**: Click "Save Results" to download the CSV.
