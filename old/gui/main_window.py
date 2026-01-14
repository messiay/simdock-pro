import subprocess
import sys
import concurrent.futures
import multiprocessing
import os
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
import threading
from typing import Dict, List, Optional, Any
import tkinter as tk
import traceback
import webbrowser # Added

from core.docking_manager import DockingManager
from core.file_manager import FileManager
from core.file_processor import FileProcessor
from core.session_manager import SessionManager
from core.project_manager import ProjectManager

from gui.dialogs import AdvancedSettingsDialog, ResultsDialog, BatchResultsDialog
from gui.components import DockingSetupTab, ResultsTab, VisualizationTab
from utils.config import get_config_manager
from core.logger import get_logger


class MainWindow:
    """Main application window with modern GUI using customtkinter."""
    
    def __init__(self):
        # Initialize customtkinter
        ctk.set_appearance_mode("Dark")  # Modes: "System", "Dark", "Light"
        ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("SimDock 3.1 - Advanced Molecular Docking")
        self.root.geometry("1200x800")
        self.root.minsize(1000, 700)
        
        # Initialize core components
        self.docking_manager = DockingManager(default_engine="vina")
        self.file_manager = FileManager()
        self.file_processor = FileProcessor()
        self.session_manager = SessionManager()
        self.project_manager = ProjectManager()
        self.config_manager = get_config_manager()
        self.logger = get_logger()

        
        # Thread safety
        self.thread_lock = threading.Lock()
        self.docking_thread = None
        
        # Application state
        self._initialize_state()
        
        # Setup GUI
        self._setup_gui()
        
        # Setup project directory
        self._setup_project_directory()
    
    def _initialize_state(self):
        """Initialize application state variables."""
        # File paths
        self.receptor_path = tk.StringVar(value="")
        self.receptors_data = [] # List of dicts: {'path': str, 'center': tuple, 'size': tuple}
        self.current_receptor_index = -1
        self.pdb_id = tk.StringVar(value="")
        self.pubchem_id = tk.StringVar(value="")
        
        # Ligand management
        self.ligand_library = []
        self.selected_ligand_index = tk.IntVar(value=0)
        
        # Docking parameters
        # Coordinates (Use StringVar to avoid TclError when clearing field)
        self.center_x = tk.StringVar(value="0.0")
        self.center_y = tk.StringVar(value="0.0")
        self.center_z = tk.StringVar(value="0.0")
        
        self.size_x = tk.StringVar(value="20.0")
        self.size_y = tk.StringVar(value="20.0")
        self.size_z = tk.StringVar(value="20.0")
        self.exhaustiveness = tk.IntVar(value=8)
        
        # Engine selection
        self.selected_engine = tk.StringVar(value="vina")
        self.available_engines = self.docking_manager.get_available_engines()
        
        # Settings
        self.docking_mode = tk.StringVar(value="Blind Docking")
        self.viewer_choice = tk.StringVar(value="ChimeraX")
        self.use_adaptive_exhaustiveness = tk.BooleanVar(value=False)
        self.use_hierarchical_docking = tk.BooleanVar(value=False)
        self.refine_percentage = tk.IntVar(value=10)
        self.seed = tk.IntVar(value=0)  # 0 means random
        
        # Results
        self.last_results = []
        self.batch_results_summary = []
        self.full_batch_results = []
        self.last_run_type = None
        self.receptor_pdbqt_path = None
        self.single_docking_output_path = None
        
        # Project management
        self.current_project_path = tk.StringVar(value="")
        self.projects_directory = os.path.join(os.path.expanduser("~"), "SimDock_Projects")
        
        # Threading control
        self.is_calculating = False
        self.is_docking = False
        self.cancel_docking = False


    
    def _setup_gui(self):
        """Setup the main GUI components."""
        # Create main container (Split view)
        self.split_container = ctk.CTkFrame(self.root)
        self.split_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left side (Controls)
        self.main_container = ctk.CTkFrame(self.split_container)
        self.main_container.pack(side="left", fill="both", expand=True)
        

        
        # Create header
        self._create_header()
        
        # Create tabview for main interface
        self._create_main_tabs()
        
        # Create status bar
        self._create_status_bar()
    
    def _create_header(self):
        """Create application header with menu and project info."""
        header_frame = ctk.CTkFrame(self.main_container)
        header_frame.pack(fill="x", pady=(0, 10))
        
        # Title and logo
        title_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_frame.pack(side="left", fill="x", expand=True)
        
        title_label = ctk.CTkLabel(
            title_frame, 
            text="SimDock 3.1", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Project info
        project_label = ctk.CTkLabel(
            title_frame,
            textvariable=self.current_project_path,
            font=ctk.CTkFont(size=12)
        )
        project_label.pack(side="left", padx=20)
        
        # Menu buttons
        menu_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        menu_frame.pack(side="right", padx=10) # Modified padx
        

        
        new_project_btn = ctk.CTkButton( # Modified
            menu_frame, 
            text="New Project", 
            command=self._create_new_project, # Changed to _create_new_project
            width=100
        )
        new_project_btn.pack(side="left", padx=5)
        
        load_project_btn = ctk.CTkButton(
            menu_frame, 
            text="Load Project", 
            command=self._load_project,
            width=100
        )
        load_project_btn.pack(side="left", padx=5)
        
        # Settings button
        settings_btn = ctk.CTkButton(
            menu_frame,
            text="Settings",
            command=self._open_settings,
            width=80
        )
        settings_btn.pack(side="left", padx=5)
    
    def _create_main_tabs(self):
        """Create the main tabbed interface."""
        self.tabview = ctk.CTkTabview(self.main_container)
        self.tabview.pack(fill="both", expand=True)
        
        # Create tabs
        self.docking_tab = self.tabview.add("Docking Setup")
        self.results_tab = self.tabview.add("Results")
        self.visualization_tab = self.tabview.add("Visualization")
        
        # Initialize tab components - FIXED: Remove extra parameters
        self.docking_setup_tab = DockingSetupTab(self.docking_tab, self)
        self.results_tab_component = ResultsTab(self.results_tab, self)
        self.visualization_tab_component = VisualizationTab(self.visualization_tab, self)
    
    def _create_status_bar(self):
        """Create status bar at bottom of window."""
        status_frame = ctk.CTkFrame(self.main_container)
        status_frame.pack(fill="x", pady=(10, 0))
        
        # Status label
        self.status_label = ctk.CTkLabel(
            status_frame, 
            text="Ready to start docking...",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(status_frame)
        self.progress_bar.pack(side="right", padx=10, pady=5, fill="x", expand=True)
        self.progress_bar.set(0)
        
        # Cancel button (initially hidden)
        self.cancel_button = ctk.CTkButton(
            status_frame,
            text="Cancel",
            command=self.cancel_docking_process,
            width=80,
            fg_color="red",
            hover_color="darkred"
        )
        self.cancel_button.pack(side="right", padx=5)
        self.cancel_button.pack_forget()  # Hide initially
    
    def _setup_project_directory(self):
        """Setup projects directory if it doesn't exist."""
        os.makedirs(self.projects_directory, exist_ok=True)
    
    def _create_new_project(self):
        """Create a new project."""
        project_name = simpledialog.askstring(
            "New Project", 
            "Enter project name:",
            parent=self.root
        )
        
        if project_name:
            try:
                project_path = self.project_manager.create_new_project(
                    project_name, 
                    self.projects_directory
                )
                self.current_project_path.set(f"Project: {project_name}")
                self.update_status(f"Created new project: {project_name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create project: {e}")
    
    def _load_project(self):
        """Load an existing project."""
        project_path = filedialog.askdirectory(
            title="Select Project Folder",
            initialdir=self.projects_directory
        )
        
        if project_path:
            try:
                project_data = self.project_manager.load_project(project_path)
                project_name = project_data['project_info']['name']
                self.current_project_path.set(f"Project: {project_name}")
                
                # Load project data into application state
                self._load_project_data(project_data)
                
                self.update_status(f"Loaded project: {project_name}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load project: {e}")
    
    def _load_project_data(self, project_data: Dict[str, Any]):
        """Load project data into application state."""
        # Load receptor and ligands
        if project_data.get('files', {}).get('receptors'):
            receptor = project_data['files']['receptors'][0]
            self.receptor_path.set(receptor['path'])
        
        if project_data.get('files', {}).get('ligands'):
            self.ligand_library = [ligand['path'] for ligand in project_data['files']['ligands']]
            self.docking_setup_tab.refresh_ligand_list()
        
        # Load docking parameters if available
        if 'settings' in project_data:
            settings = project_data['settings']
            self.center_x.set(settings.get('center_x', 0.0))
            self.center_y.set(settings.get('center_y', 0.0))
            self.center_z.set(settings.get('center_z', 0.0))
            self.size_x.set(settings.get('size_x', 20.0))
            self.size_y.set(settings.get('size_y', 20.0))
            self.size_z.set(settings.get('size_z', 20.0))
    
    def _open_settings(self):
        """Open advanced settings dialog."""
        dialog = AdvancedSettingsDialog(self.root, self)
        dialog.show()
    
    def show_engine_info(self):
        """Show information about the selected engine."""
        engine_type = self.selected_engine.get()
        try:
            info = self.docking_manager.get_engine_info(engine_type)
            
            message = f"Engine: {info['name']}\n"
            message += f"Version: {info['version']}\n"
            message += f"Description: {info.get('description', 'No description available')}\n\n"
            message += "Default Parameters:\n"
            for key, value in info['default_parameters'].items():
                message += f"  {key}: {value}\n"
            
            messagebox.showinfo("Engine Information", message)
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not get engine info: {e}")
    
    # Core functionality methods
    def select_receptor_file(self):
        """Select receptor file."""
        file_path = filedialog.askopenfilename(
            title="Select Receptor File",
            filetypes=[
                ("PDB files", "*.pdb"),
                ("PDBQT files", "*.pdbqt"),
                ("All files", "*.*")
            ]
        )
        
        if file_path:
            self._add_receptor_to_list(file_path)

    def add_receptor(self):
        """Add a receptor to the list."""
        self.select_receptor_file()

    def remove_receptor(self):
        """Remove the currently selected receptor."""
        if self.current_receptor_index >= 0 and self.current_receptor_index < len(self.receptors_data):
            del self.receptors_data[self.current_receptor_index]
            
            if self.receptors_data:
                new_index = max(0, self.current_receptor_index - 1)
                self.select_receptor_by_index(new_index)
            else:
                self.current_receptor_index = -1
                self.receptor_path.set("")
                # Reset coordinates? Maybe keep last used.
            
            self.docking_setup_tab.refresh_receptor_list()

    def select_receptor_by_index(self, index):
        """Select a receptor by its index in the list."""
        if index < 0 or index >= len(self.receptors_data):
            return
            
        # Save current config before switching
        self._save_current_receptor_config()
        
        self.current_receptor_index = index
        data = self.receptors_data[index]
        
        self.receptor_path.set(data['path'])
        
        # Load coordinates
        if 'center' in data:
            self.center_x.set(data['center'][0])
            self.center_y.set(data['center'][1])
            self.center_z.set(data['center'][2])
        if 'size' in data:
            self.size_x.set(data['size'][0])
            self.size_y.set(data['size'][1])
            self.size_z.set(data['size'][2])
            
        # Update UI list selection
        self.docking_setup_tab.refresh_receptor_list()

    def _save_current_receptor_config(self):
        """Save current UI values to the current receptor data."""
        if self.current_receptor_index >= 0 and self.current_receptor_index < len(self.receptors_data):
            try:
                self.receptors_data[self.current_receptor_index]['center'] = (
                    float(self.center_x.get()), float(self.center_y.get()), float(self.center_z.get())
                )
                self.receptors_data[self.current_receptor_index]['size'] = (
                    float(self.size_x.get()), float(self.size_y.get()), float(self.size_z.get())
                )
            except ValueError:
                # If invalid, don't update data or set to 0.0? 
                # Better to keep old data or be safe. 
                pass

    def _add_receptor_to_list(self, file_path):
        """Add a receptor file to the list and select it."""
        # Check if already exists
        for i, r in enumerate(self.receptors_data):
            if r['path'] == file_path:
                self.select_receptor_by_index(i)
                return

        # Add new
        self._save_current_receptor_config() # Save previous
        
        # Default box (or auto-detect later)
        new_receptor = {
            'path': file_path,
            'center': (0.0, 0.0, 0.0),
            'size': (20.0, 20.0, 20.0)
        }
        
        self.receptors_data.append(new_receptor)
        self.select_receptor_by_index(len(self.receptors_data) - 1)
        
        # Trigger auto-detection of box if possible (optional)
        self.update_status(f"Added receptor: {os.path.basename(file_path)}")
        self._start_coordinate_calculation()

    def add_ligand_file(self):
        """Add a single ligand file to the library."""
        file_path = filedialog.askopenfilename(
            title="Select Ligand File",
            filetypes=[
                ("Ligand files", "*.pdb *.sdf *.mol2 *.pdbqt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            if file_path not in self.ligand_library:
                self.ligand_library.append(file_path)
                self.docking_setup_tab.refresh_ligand_list()
                self.update_status(f"Added ligand: {os.path.basename(file_path)}")
                self._start_coordinate_calculation()

    def select_ligand_file(self):
        """Select single ligand file (Legacy)."""
        self.add_ligand_file()
    
    def import_ligand_folder(self):
        """Import folder of ligand files."""
        folder_path = filedialog.askdirectory(title="Select Ligand Folder")
        
        if folder_path:
            try:
                self.ligand_library.clear()
                supported_formats = ('.pdb', '.sdf', '.mol2')
                
                for filename in os.listdir(folder_path):
                    if filename.lower().endswith(supported_formats):
                        file_path = os.path.join(folder_path, filename)
                        self.ligand_library.append(file_path)
                
                self.docking_setup_tab.refresh_ligand_list()
                self.update_status(f"Imported {len(self.ligand_library)} ligands")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import ligands: {e}")
    
    def fetch_pdb_structure(self):
        """Fetch receptor from PDB."""
        pdb_id = self.pdb_id.get().strip().upper()
        
        if not pdb_id or len(pdb_id) != 4:
            messagebox.showerror("Error", "Please enter a valid 4-character PDB ID")
            return
        
        def fetch_thread():
            try:
                self.update_status(f"Downloading {pdb_id} from PDB...")
                cleaned_path = self.file_processor.fetch_pdb_structure(pdb_id, self.projects_directory)
                
                if cleaned_path and os.path.exists(cleaned_path):
                    self.root.after(0, lambda: self._add_receptor_to_list(cleaned_path))
                    self.root.after(0, lambda: self.update_status(f"Loaded {pdb_id}"))
                else:
                    raise Exception("Download failed")
                    
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch PDB: {e}"))
                self.root.after(0, lambda: self.update_status("Ready"))
        
        threading.Thread(target=fetch_thread, daemon=True).start()

    def add_ligand_file(self):
        """Add a single ligand file to the library."""
        file_path = filedialog.askopenfilename(
            title="Select Ligand File",
            filetypes=[
                ("Ligand files", "*.pdb *.sdf *.mol2 *.pdbqt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            if file_path not in self.ligand_library:
                self.ligand_library.append(file_path)
                self.docking_setup_tab.refresh_ligand_list()
                self.update_status(f"Added ligand: {os.path.basename(file_path)}")
    
    def fetch_pubchem_ligand(self):
        """Fetch ligand(s) from PubChem."""
        input_str = self.pubchem_id.get().strip()
        
        if not input_str:
            messagebox.showerror("Error", "Please enter a PubChem CID or name")
            return
        
        # Split by comma or plus
        identifiers = [x.strip() for x in input_str.replace('+', ',').split(',') if x.strip()]
        
        def fetch_thread():
            self.update_status(f"Downloading {len(identifiers)} ligands from PubChem...")
            success_count = 0
            
            for identifier in identifiers:
                try:
                    if self.cancel_docking: break
                    
                    self.root.after(0, lambda i=identifier: self.update_status(f"Downloading {i}..."))
                    ligand_path = self.file_processor.fetch_pubchem_ligand(identifier, self.projects_directory)
                    
                    if ligand_path and os.path.exists(ligand_path):
                        self.root.after(0, lambda p=ligand_path, i=identifier: self._on_pubchem_fetched(p, i))
                        success_count += 1
                    else:
                        raise Exception("Download failed")
                        
                except Exception as e:
                    self.root.after(0, lambda s=f"PubChem {identifier}", err=str(e): self._on_fetch_error(s, err))
            
            if success_count > 0:
                self.root.after(0, lambda: self.update_status(f"Downloaded {success_count} ligands"))
                self._start_coordinate_calculation()
            else:
                self.root.after(0, lambda: self.update_status("Download failed"))
        
        threading.Thread(target=fetch_thread, daemon=True).start()
    
    def _on_pubchem_fetched(self, file_path: str, identifier: str):
        """Handle successful PubChem fetch."""
        if file_path not in self.ligand_library:
            self.ligand_library.append(file_path)
            self.docking_setup_tab.refresh_ligand_list()
            # self.update_status(f"Downloaded ligand: {identifier}") # Handled in thread loop now
    
    def _on_fetch_error(self, source: str, error: str):
        """Handle fetch errors."""
        self.logger.error(f"Failed to download from {source}: {error}")
        messagebox.showerror("Download Error", f"Failed to download from {source}:\n{error}")
        self.update_status("Download failed")
    
    def _start_coordinate_calculation(self):
        """Start coordinate calculation in background thread."""
        if self.is_calculating:
            return
        
        self.is_calculating = True
        
        def calculate_thread():
            try:
                receptor = self.receptor_path.get()
                if not receptor:
                    return
                
                # Calculate coordinates based on docking mode
                if self.docking_mode.get() == "Blind Docking":
                    coords = self.file_processor.get_coordinates_from_file(receptor, self.file_manager.create_temp_directory())
                    if coords:
                        center, size = self.file_processor.calculate_bounding_box(coords)
                        self.root.after(0, lambda c=center, s=size: self._on_coordinates_calculated(c, s))
                
                elif self.docking_mode.get() == "Targeted Docking" and self.ligand_library:
                    ligand_path = self.ligand_library[0]  # Use first ligand
                    coords = self.file_processor.get_coordinates_from_file(ligand_path, self.file_manager.create_temp_directory())
                    if coords:
                        center, size = self.file_processor.get_ligand_based_box(coords)
                        self.root.after(0, lambda c=center, s=size: self._on_coordinates_calculated(c, s))
                        
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._on_calculation_error(err))
            finally:
                self.is_calculating = False
        
        threading.Thread(target=calculate_thread, daemon=True).start()
        self.update_status("Calculating docking coordinates...")
    
    def _on_coordinates_calculated(self, center: tuple, size: tuple):
        """Handle calculated coordinates."""
        self.center_x.set(str(round(center[0], 3)))
        self.center_y.set(str(round(center[1], 3)))
        self.center_z.set(str(round(center[2], 3)))
        self.size_x.set(str(round(size[0], 3)))
        self.size_y.set(str(round(size[1], 3)))
        self.size_z.set(str(round(size[2], 3)))
        self.update_status("Coordinates calculated successfully")
    
    def _on_calculation_error(self, error: str):
        """Handle coordinate calculation errors."""
        self.logger.error(f"Coordinate calculation error: {error}")
        messagebox.showerror("Calculation Error", f"Failed to calculate coordinates:\n{error}")
        self.update_status("Coordinate calculation failed")
    
    def start_docking(self):
        """Start docking process."""
        if not self.receptor_path.get() or not self.ligand_library:
            messagebox.showerror("Error", "Please select a receptor and at least one ligand")
            return
        
        if self.is_docking:
            messagebox.showwarning("Warning", "Docking is already in progress")
            return
        
        self.is_docking = True
        self.cancel_docking = False
        self.progress_bar.set(0)
        
        # Show cancel button
        self.cancel_button.pack(side="right", padx=5)
        
        # Clear previous results under thread lock
        with self.thread_lock:
            self.last_results.clear()
            self.batch_results_summary.clear()
            self.full_batch_results.clear()
        
        def docking_thread():
            try:
                is_batch = len(self.ligand_library) > 1 or len(self.receptors_data) > 1
                
                if is_batch:
                    self._run_batch_docking()
                else:
                    self._run_single_docking()
                    
            except Exception as e:
                self.root.after(0, lambda err=str(e): self._on_docking_error(err))
            finally:
                self.is_docking = False
                self.cancel_docking = False
                # Hide cancel button
                self.root.after(0, lambda: self.cancel_button.pack_forget())
        
        self.docking_thread = threading.Thread(target=docking_thread, daemon=True)
        self.docking_thread.start()
    
    def cancel_docking_process(self):
        """Cancel ongoing docking process."""
        if self.is_docking:
            self.cancel_docking = True
            self.update_status("Cancelling docking...")
    
    def _run_single_docking(self):
        """Run single ligand docking."""
        try:
            engine = self.docking_manager.get_engine(self.selected_engine.get())
            
            # Check cancellation
            if self.cancel_docking:
                self.root.after(0, lambda: self.update_status("Docking cancelled", 0))
                return
            
            # Prepare files
            self.root.after(0, lambda: self.update_status(f"Preparing receptor with {engine.get_name()}...", 10))
            receptor_pdbqt = engine.prepare_receptor(self.receptor_path.get(), self.file_manager.create_temp_directory())
            
            if not receptor_pdbqt:
                raise Exception("Failed to prepare receptor")
            
            # Check cancellation
            if self.cancel_docking:
                self.root.after(0, lambda: self.update_status("Docking cancelled", 0))
                return
            
            self.root.after(0, lambda: self.update_status("Preparing ligand...", 30))
            ligand_pdbqt = engine.prepare_ligand(self.ligand_library[0], self.file_manager.create_temp_directory())
            
            if not ligand_pdbqt:
                raise Exception("Failed to prepare ligand")
            
            # Check cancellation
            if self.cancel_docking:
                self.root.after(0, lambda: self.update_status("Docking cancelled", 0))
                return
            
            # Run docking
            self.root.after(0, lambda: self.update_status(f"Running {engine.get_name()}...", 50))
            output_path = os.path.join(self.file_manager.create_temp_directory(), "docked_poses.pdbqt")
            
            try:
                center = (float(self.center_x.get()), float(self.center_y.get()), float(self.center_z.get()))
                size = (float(self.size_x.get()), float(self.size_y.get()), float(self.size_z.get()))
            except ValueError:
                raise Exception("Invalid dockng coordinates. Please ensure all Box Center and Size values are numbers.")
            
            # Calculate exhaustiveness
            if self.use_adaptive_exhaustiveness.get():
                current_exhaustiveness = engine.get_adaptive_exhaustiveness(ligand_pdbqt)
            else:
                current_exhaustiveness = self.exhaustiveness.get()
            
            result = engine.run_docking(
                receptor_pdbqt, ligand_pdbqt, output_path,
                center, size, exhaustiveness=self.exhaustiveness.get(),
                seed=self.seed.get() if self.seed.get() != 0 else None
            )
            
            # Check cancellation
            if self.cancel_docking:
                self.root.after(0, lambda: self.update_status("Docking cancelled", 0))
                return
            
            if result['success']:
                with self.thread_lock:
                    self.last_results = result['scores']
                    # Use the output file returned by the engine if available, otherwise use the requested path
                    self.single_docking_output_path = result.get('output_file', output_path)
                    self.receptor_pdbqt_path = receptor_pdbqt
                    self.last_run_type = 'single'
                
                self.root.after(0, lambda r=result: self._on_docking_complete(r))
            else:
                error_msg = result.get('error', 'Docking failed')
                raise Exception(error_msg)
                
        except Exception as e:
            self.root.after(0, lambda err=str(e): self._on_docking_error(err))
    
    def _prepare_ligands_batch(self, engine, ligand_paths):
        """Prepare multiple ligands in parallel."""
        prepared_ligands = {}
        max_workers = max(1, multiprocessing.cpu_count() - 1)
        
        self.root.after(0, lambda: self.update_status(f"Preparing {len(ligand_paths)} ligands...", 0))
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(
                    engine.prepare_ligand, 
                    path, 
                    self.file_manager.create_temp_directory()
                ): path for path in ligand_paths
            }
            
            completed = 0
            for future in concurrent.futures.as_completed(future_to_path):
                if self.cancel_docking:
                    executor.shutdown(wait=False)
                    return {}
                
                path = future_to_path[future]
                try:
                    pdbqt_path = future.result()
                    if pdbqt_path:
                        prepared_ligands[path] = pdbqt_path
                except Exception as e:
                    print(f"Failed to prepare {path}: {e}")
                
                completed += 1
                progress = (completed/len(ligand_paths))*10
                self.root.after(0, lambda p=progress: self.update_status(f"Preparing ligands... ({completed}/{len(ligand_paths)})", p))
                
        return prepared_ligands

    def _run_batch_docking(self):
        """Run batch docking with multiple receptors and ligands."""
        try:
            # Ensure current config is saved
            self._save_current_receptor_config()
            
            if not self.receptors_data:
                raise Exception("No receptors added. Please add at least one receptor.")
                
            engine = self.docking_manager.get_engine(self.selected_engine.get())
            
            # Initialize results under thread lock
            with self.thread_lock:
                self.batch_results_summary.clear()
                self.full_batch_results.clear()
                self.last_run_type = 'batch'
            
            # [OPTIMIZATION] Create Master Temporary Directory for this batch run
            master_temp_dir = self.file_manager.create_temp_directory()
            self.root.after(0, lambda: self.update_status(f"Batch workspace: {os.path.basename(master_temp_dir)}"))

            # 1. Prepare all ligands in parallel first
            prepared_ligands = self._prepare_ligands_batch(engine, self.ligand_library)
            
            if not prepared_ligands:
                if self.cancel_docking:
                    self.root.after(0, lambda: self.update_status("Docking cancelled", 0))
                    return
                raise Exception("Failed to prepare any ligands")

            total_tasks = len(self.receptors_data) * len(prepared_ligands)
            processed_count = 0
            
            # Determine docking strategy
            use_hierarchical = self.use_hierarchical_docking.get()
            
            # Prepare tasks
            # Use max_workers for threading, but limit CPU per Vina instance
            max_workers = max(1, multiprocessing.cpu_count() - 1)
            cpu_per_instance = 1 # Force 1 CPU per instance to avoid thrashing
            
            # Outer loop: Receptors
            for receptor_idx, receptor_data in enumerate(self.receptors_data):
                if self.cancel_docking:
                    break
                    
                receptor_path = receptor_data['path']
                receptor_name = os.path.basename(receptor_path)
                
                self.root.after(0, lambda n=receptor_name: self.update_status(f"Preparing receptor {n}...", 10))
                
                # Prepare receptor
                receptor_pdbqt = engine.prepare_receptor(receptor_path, master_temp_dir)
                if not receptor_pdbqt:
                    print(f"Failed to prepare receptor {receptor_name}")
                    continue
                
                # Get receptor-specific box
                center = receptor_data.get('center', (0,0,0))
                size = receptor_data.get('size', (20,20,20))
                seed = self.seed.get() if self.seed.get() != 0 else None
                
                # Determine exhaustiveness
                if use_hierarchical:
                    exhaustiveness = 4
                elif self.use_adaptive_exhaustiveness.get():
                    exhaustiveness = None
                else:
                    exhaustiveness = self.exhaustiveness.get()
                
                # Run docking for this receptor
                screening_results = []
                
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future_to_ligand = {
                        executor.submit(
                            self._process_single_ligand, 
                            engine, receptor_pdbqt, prepared_ligands[ligand_path], ligand_path,
                            center, size, exhaustiveness, seed, cpu_per_instance, master_temp_dir
                        ): ligand_path for ligand_path in prepared_ligands
                    }
                    
                    for future in concurrent.futures.as_completed(future_to_ligand):
                        if self.cancel_docking:
                            executor.shutdown(wait=False)
                            self.root.after(0, lambda: self.update_status("Docking cancelled", 0))
                            return

                        ligand_path = future_to_ligand[future]
                        ligand_name = os.path.basename(ligand_path)
                        
                        try:
                            result = future.result()
                            processed_count += 1
                            progress = 10 + (processed_count / total_tasks) * 90 # Scale 10-100%
                            self.root.after(0, lambda p=progress, ln=ligand_name, rn=receptor_name: self.update_status(f"Docking {ln} @ {rn}", p))
                            
                            if result:
                                # Check if it was an error result
                                error_msg = result.get('error_msg')
                                affinity_display = "Error" if error_msg else result['affinity']
                                status_display = "Failed" if error_msg else "Success"

                                # Add receptor name to result
                                result['receptor_name'] = receptor_name
                                
                                if use_hierarchical and not error_msg:
                                    screening_results.append(result)
                                else:
                                    # Always append to summary even on error, so user sees it
                                    with self.thread_lock:
                                        summary_item = {
                                            'Receptor': receptor_name,
                                            'Ligand': result['ligand_name'], 
                                            'Best Affinity (kcal/mol)': affinity_display, 
                                            'OutputFile': result['output_path'],
                                            'Engine': engine.get_name(),
                                            'ReceptorPath': receptor_pdbqt,
                                            'Status': status_display
                                        }
                                        if error_msg:
                                            summary_item['Error'] = error_msg
                                            
                                        self.batch_results_summary.append(summary_item)
                                        
                                        if result.get('scores'):
                                            for score in result['scores']:
                                                self.full_batch_results.append({
                                                    'Receptor': receptor_name,
                                                    'Ligand': result['ligand_name'], 
                                                    **score
                                                })
                        except Exception as e:
                            print(f"Error processing future: {e}")

                # Refinement Phase (per receptor)
                if use_hierarchical and screening_results:
                    screening_results.sort(key=lambda x: x['affinity'])
                    top_n = max(1, int(len(screening_results) * (self.refine_percentage.get() / 100)))
                    top_candidates = screening_results[:top_n]
                    
                    # Add skipped
                    with self.thread_lock:
                        for res in screening_results[top_n:]:
                            self.batch_results_summary.append({
                                'Receptor': receptor_name,
                                'Ligand': res['ligand_name'], 
                                'Best Affinity (kcal/mol)': res['affinity'], 
                                'OutputFile': res['output_path'],
                                'Engine': engine.get_name(),
                                'Status': 'Skipped',
                                'ReceptorPath': receptor_pdbqt
                            })
                    
                    # Refine
                    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                        future_to_cand = {
                            executor.submit(
                                self._process_single_ligand,
                                engine, receptor_pdbqt, cand['ligand_pdbqt'], cand['ligand_path'],
                                center, size, max(32, self.exhaustiveness.get() * 2), seed, cpu_per_instance, master_temp_dir
                            ): cand for cand in top_candidates
                        }
                        
                        for future in concurrent.futures.as_completed(future_to_cand):
                            if self.cancel_docking: return
                            try:
                                result = future.result()
                                if result:
                                    # Handle refinement success/failure
                                    error_msg = result.get('error_msg')
                                    affinity_display = "Error" if error_msg else result['affinity']
                                    status_display = "Refined" if not error_msg else "Refinement Failed"

                                    with self.thread_lock:
                                        self.batch_results_summary.append({
                                            'Receptor': receptor_name,
                                            'Ligand': result['ligand_name'], 
                                            'Best Affinity (kcal/mol)': affinity_display, 
                                            'OutputFile': result['output_path'],
                                            'Engine': engine.get_name(),
                                            'Status': status_display,
                                            'ReceptorPath': receptor_pdbqt
                                        })
                                        if result.get('scores'):
                                            for score in result['scores']:
                                                self.full_batch_results.append({
                                                    'Receptor': receptor_name,
                                                    'Ligand': result['ligand_name'], 
                                                    **score
                                                })
                            except Exception as e:
                                print(f"Refine error: {e}")

            # [FAILSAFE] If no results were generated, add a placeholder error
            with self.thread_lock:
                if not self.batch_results_summary:
                    self.batch_results_summary.append({
                        'Receptor': 'System',
                        'Ligand': 'None', 
                        'Best Affinity (kcal/mol)': 'Error', 
                        'OutputFile': None,
                        'Engine': engine.get_name(),
                        'Status': 'Failed',
                        'Error': 'No results generated. Check receptor preparation.'
                    })

            self.root.after(0, lambda: self.update_status("Batch Docking Completed", 100))
            self.root.after(0, self._on_batch_docking_complete)
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self._on_docking_error(err))
            
        except Exception as e:
            self.root.after(0, lambda err=str(e): self._on_docking_error(err))
    
    def _process_single_ligand(self, engine, receptor_pdbqt, ligand_pdbqt, ligand_path, center, size, exhaustiveness, seed, cpu=None, temp_dir=None):
        """Process a single ligand (docking only, preparation done beforehand)."""
        try:
            ligand_name = os.path.basename(ligand_path)
            
            # Determine exhaustiveness if adaptive
            current_exh = exhaustiveness
            if current_exh is None: # Adaptive mode
                current_exh = engine.get_adaptive_exhaustiveness(ligand_pdbqt)
            
            # [OPTIMIZATION] Use shared temp directory if provided
            if temp_dir:
                output_dir = temp_dir
            else:
                output_dir = self.file_manager.create_temp_directory()

            output_path = os.path.join(output_dir, f"{ligand_name}_out.pdbqt")
            
            # Prepare kwargs
            kwargs = {'exhaustiveness': current_exh, 'seed': seed}
            if cpu is not None:
                kwargs['cpu'] = cpu
            
            # [OPTIMIZATION] Pass temp_dir to engine (Crucial for RDock)
            result = engine.run_docking(
                receptor_pdbqt, ligand_pdbqt, output_path,
                center, size, temp_dir=temp_dir, **kwargs
            )
            
            actual_output_path = result.get('output_file', output_path)
            best_score = 999.9
            scores = []
            error_msg = None
            
            if result['success'] and result['scores']:
                best_score = result['scores'][0]['Affinity (kcal/mol)']
                scores = result['scores']
            elif not result['success']:
                error_msg = result.get('error', 'Docking Failed (Unknown Error)')

            return {
                'ligand_name': ligand_name,
                'ligand_path': ligand_path,
                'ligand_pdbqt': ligand_pdbqt,
                'affinity': best_score,
                'output_path': actual_output_path,
                'scores': scores,
                'error_msg': error_msg
            }
            
        except Exception as e:
            error_str = str(e)
            print(f"Exception in _process_single_ligand for {ligand_path}: {error_str}")
            
            # [DEBUG] Write error to file for agent inspection
            try:
                debug_log = r"C:\Users\user\.gemini\antigravity\brain\67679a53-90aa-4c37-a49a-d06e7396b911\docking_failure.log"
                with open(debug_log, "a") as f:
                    f.write(f"\n[{ligand_name}] ERROR:\n{error_str}\n{'-'*50}\n")
            except:
                pass

            # Return error result instead of None, so the user sees it in the table
            return {
                'ligand_name': os.path.basename(ligand_path),
                'ligand_path': ligand_path,
                'ligand_pdbqt': ligand_pdbqt,
                'affinity': 999.9,
                'output_path': None,
                'scores': [],
                'error_msg': error_str
            }

    def _on_docking_complete(self, result: Dict[str, Any]):
        """Handle single docking completion."""
        self.update_status("Docking completed successfully!", 100)
        self.is_docking = False
        self.cancel_docking = False
        
        # Switch to results tab
        self.tabview.set("Results")
        self.results_tab_component.show_single_results(self.last_results)
        

    


    def _add_receptor_to_list(self, file_path):
        """Add a receptor file to the list and select it."""
        # Check if already exists
        for i, r in enumerate(self.receptors_data):
            if r['path'] == file_path:
                self.select_receptor_by_index(i)
                return

        # Add new
        self._save_current_receptor_config() # Save previous
        
        # Default box (or auto-detect later)
        new_receptor = {
            'path': file_path,
            'center': (0.0, 0.0, 0.0),
            'size': (20.0, 20.0, 20.0)
        }
        
        self.receptors_data.append(new_receptor)
        self.select_receptor_by_index(len(self.receptors_data) - 1)
        
        # Trigger auto-detection of box if possible (optional)
        self.update_status(f"Added receptor: {os.path.basename(file_path)}")
        self._start_coordinate_calculation()
        


    def select_receptor_by_index(self, index):
        """Select a receptor by its index in the list."""
        if index < 0 or index >= len(self.receptors_data):
            return
            
        # Save current config before switching
        self._save_current_receptor_config()
        
        self.current_receptor_index = index
        data = self.receptors_data[index]
        
        self.receptor_path.set(data['path'])
        
        # Load coordinates
        if 'center' in data:
            self.center_x.set(data['center'][0])
            self.center_y.set(data['center'][1])
            self.center_z.set(data['center'][2])
        if 'size' in data:
            self.size_x.set(data['size'][0])
            self.size_y.set(data['size'][1])
            self.size_z.set(data['size'][2])
            
        # Update UI list selection
        self.docking_setup_tab.refresh_receptor_list()
        


    def add_ligand_file(self):
        """Add a single ligand file to the library."""
        file_path = filedialog.askopenfilename(
            title="Select Ligand File",
            filetypes=[
                ("Ligand files", "*.pdb *.sdf *.mol2 *.pdbqt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            if file_path not in self.ligand_library:
                self.ligand_library.append(file_path)
                self.docking_setup_tab.refresh_ligand_list()
                self.update_status(f"Added ligand: {os.path.basename(file_path)}")
                self._start_coordinate_calculation()
                


    def _on_pubchem_fetched(self, file_path: str, identifier: str):
        """Handle successful PubChem fetch."""
        if file_path not in self.ligand_library:
            self.ligand_library.append(file_path)
            self.docking_setup_tab.refresh_ligand_list()
            




    def _on_batch_docking_complete(self):
        """Handle batch docking completion."""
        self.update_status("Batch docking completed!", 100) # Modified
        self.is_docking = False
        self.cancel_docking = False
        
        # Switch to results tab
        self.tabview.set("Results") # Modified
        self.results_tab_component.show_batch_results(self.batch_results_summary, self.full_batch_results) # Modified
        

    
    def _on_docking_error(self, error: str):
        """Handle docking errors."""
        self.logger.error(f"Docking error: {error}")
        error_msg = f"Docking failed:\n{error}"
        if self.cancel_docking:
            error_msg = "Docking was cancelled by user"
        
        self.root.after(0, lambda: messagebox.showerror("Docking Error", error_msg))
        self.update_status("Docking failed" if not self.cancel_docking else "Docking cancelled")
        self.is_docking = False
        self.cancel_docking = False
        self.progress_bar.set(0)
    
    def visualize_results(self):
        """Visualize docking results."""
        if self.last_run_type == 'single' and self.single_docking_output_path:
            # Switch to visualization tab first
            self.tabview.set("Visualization")
            self.visualization_tab_component.visualize_single_results(
                self.receptor_pdbqt_path, 
                self.single_docking_output_path,
                self.viewer_choice.get()
            )
        elif self.last_run_type == 'batch':
            # Switch to visualization tab and show batch options
            self.tabview.set("Visualization")
            self.visualization_tab_component.show_batch_visualization(self.batch_results_summary)
    
    def update_status(self, message: str, progress: Optional[float] = None):
        """Update status bar and progress."""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.set(progress / 100)
        self.root.update_idletasks()
    
    def run(self):
        """Start the application."""
        self.root.mainloop()
