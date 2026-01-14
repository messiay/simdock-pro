import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
from typing import List, Dict, Optional, Callable
import customtkinter as ctk
import subprocess
import sys
from core.pocket_finder import PocketFinder
from gui.dialogs import PocketSelectionDialog


class DockingSetupTab:
    """Docking setup tab component."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the docking setup tab UI."""
        # Main frame with scrollbar
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create scrollable frame
        self.canvas = tk.Canvas(main_frame, bg='#2b2b2b', highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ctk.CTkFrame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Ensure scrollable frame expands to fill canvas
        self.canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Bind mousewheel to canvas
        # Bind mousewheel to canvas and scrollable frame
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.scrollable_frame.bind("<MouseWheel>", self._on_mousewheel)
        
        # Setup content
        self._create_receptor_section()
        self._create_ligand_section()
        self._create_docking_section()
        self._create_control_buttons()
        
        # Recursively bind mousewheel to all children
        self._bind_mousewheel_recursive(self.scrollable_frame)

    def _bind_mousewheel_recursive(self, widget):
        """Recursively bind mousewheel event to widget and its children."""
        widget.bind("<MouseWheel>", self._on_mousewheel)
        for child in widget.winfo_children():
            self._bind_mousewheel_recursive(child)
    
    def _on_canvas_configure(self, event):
        """Handle canvas resize to stretch the inner frame."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.itemconfig(self.canvas.find_withtag("all")[0], width=event.width)

    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling."""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def _create_receptor_section(self):
        """Create receptor selection section."""
        receptor_frame = ctk.CTkFrame(self.scrollable_frame)
        receptor_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Title
        title_label = ctk.CTkLabel(
            receptor_frame, 
            text="Receptor Setup", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Receptor List
        list_frame = ctk.CTkFrame(receptor_frame)
        list_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(list_frame, text="Receptors:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(5, 0), padx=5)
        
        # Create listbox with scrollbar
        list_container = ctk.CTkFrame(list_frame)
        list_container.pack(fill="x", padx=5, pady=5)
        
        self.receptor_listbox = tk.Listbox(
            list_container, 
            height=6,
            bg='#343638',
            fg='white',
            selectbackground='#3b8ed0',
            selectforeground='white',
            font=("Roboto", 12)
        )
        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        
        self.receptor_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.receptor_listbox.yview)
        
        self.receptor_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind selection event
        self.receptor_listbox.bind('<<ListboxSelect>>', self._on_receptor_select)
        
        # Buttons
        btn_frame = ctk.CTkFrame(receptor_frame, fg_color="transparent")
        btn_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkButton(
            btn_frame, 
            text="+ Add Receptor", 
            command=self.app.add_receptor,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame, 
            text="- Remove", 
            command=self.app.remove_receptor,
            fg_color="#cf3a3a",
            hover_color="#a62e2e",
            width=80
        ).pack(side="left", padx=5)
        
        # PDB download
        pdb_frame = ctk.CTkFrame(receptor_frame, fg_color="transparent")
        pdb_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(pdb_frame, text="Or fetch from PDB:").pack(side="left")
        self.pdb_entry = ctk.CTkEntry(
            pdb_frame, 
            textvariable=self.app.pdb_id,
            placeholder_text="PDB ID",
            width=80
        )
        self.pdb_entry.pack(side="left", padx=5)
        self.pdb_entry.bind('<Return>', lambda e: self.app.fetch_pdb_structure())
        ctk.CTkButton(
            pdb_frame, 
            text="Download", 
            command=self.app.fetch_pdb_structure,
            width=80
        ).pack(side="right", padx=5)

    def _on_receptor_select(self, event):
        """Handle receptor list selection."""
        selection = self.receptor_listbox.curselection()
        if selection:
            index = selection[0]
            self.app.select_receptor_by_index(index)
    
    def _create_ligand_section(self):
        """Create ligand selection section."""
        ligand_frame = ctk.CTkFrame(self.scrollable_frame)
        ligand_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Title
        title_label = ctk.CTkLabel(
            ligand_frame, 
            text="Ligand Setup", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Single ligand selection
        single_frame = ctk.CTkFrame(ligand_frame, fg_color="transparent")
        single_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkButton(
            single_frame, 
            text="+ Add Ligand File", 
            command=self.app.add_ligand_file,
            width=150
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            single_frame, 
            text="Import Folder", 
            command=self.app.import_ligand_folder,
            width=150
        ).pack(side="left", padx=5)
        
        # PubChem download
        pubchem_frame = ctk.CTkFrame(ligand_frame, fg_color="transparent")
        pubchem_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(pubchem_frame, text="Or fetch from PubChem:").pack(side="left")
        self.pubchem_entry = ctk.CTkEntry(
            pubchem_frame, 
            textvariable=self.app.pubchem_id,
            placeholder_text="Enter CID or name",
            width=150
        )
        self.pubchem_entry.pack(side="left", padx=5)
        self.pubchem_entry.bind('<Return>', lambda e: self.app.fetch_pubchem_ligand())
        ctk.CTkButton(
            pubchem_frame, 
            text="Download", 
            command=self.app.fetch_pubchem_ligand,
            width=80
        ).pack(side="right", padx=5)
        
        # Ligand list
        list_frame = ctk.CTkFrame(ligand_frame)
        list_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(list_frame, text="Selected Ligands:", font=ctk.CTkFont(size=14)).pack(anchor="w", pady=(5, 0), padx=5)
        
        # Create listbox with scrollbar
        list_container = ctk.CTkFrame(list_frame)
        list_container.pack(fill="x", padx=5, pady=5)
        
        self.ligand_listbox = tk.Listbox(
            list_container, 
            height=8,
            bg='#343638',
            fg='white',
            selectbackground='#3b8ed0',
            selectforeground='white',
            font=("Roboto", 12)
        )
        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        
        self.ligand_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.ligand_listbox.yview)
        
        self.ligand_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def _create_docking_section(self):
        """Create docking parameters section."""
        docking_frame = ctk.CTkFrame(self.scrollable_frame)
        docking_frame.pack(fill="x", pady=(0, 10), padx=10)
        
        # Title
        title_label = ctk.CTkLabel(
            docking_frame, 
            text="Docking Parameters", 
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(anchor="w", pady=(10, 5), padx=10)
        
        # Docking mode
        mode_frame = ctk.CTkFrame(docking_frame, fg_color="transparent")
        mode_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(mode_frame, text="Docking Mode:", font=ctk.CTkFont(size=14)).pack(side="left")
        mode_combo = ctk.CTkComboBox(
            mode_frame,
            values=["Blind Docking", "Targeted Docking"],
            variable=self.app.docking_mode,
            state="readonly",
            width=150,
            command=lambda _: self.app._start_coordinate_calculation()
        )
        mode_combo.pack(side="left", padx=5)
        
        ctk.CTkButton(
            mode_frame,
            text="Detect Active Sites",
            command=self._detect_active_sites,
            width=120,
            fg_color="#5c5c5c",
            hover_color="#4a4a4a"
        ).pack(side="left", padx=5)
        
        # Engine selection
        engine_frame = ctk.CTkFrame(docking_frame, fg_color="transparent")
        engine_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(engine_frame, text="Docking Engine:", font=ctk.CTkFont(size=14)).pack(side="left")
        engine_combo = ctk.CTkComboBox(
            engine_frame,
            values=self.app.available_engines,
            variable=self.app.selected_engine,
            state="readonly",
            width=150
        )
        engine_combo.pack(side="left", padx=5)
        
        ctk.CTkButton(
            engine_frame,
            text="Info",
            command=self.app.show_engine_info,
            width=60
        ).pack(side="left", padx=5)
        
        # Coordinates
        coords_frame = ctk.CTkFrame(docking_frame)
        coords_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(coords_frame, text="Docking Box Center (Å):").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        ctk.CTkLabel(coords_frame, text="X:").grid(row=0, column=1, padx=2)
        ctk.CTkEntry(coords_frame, textvariable=self.app.center_x, width=80).grid(row=0, column=2, padx=2)
        ctk.CTkLabel(coords_frame, text="Y:").grid(row=0, column=3, padx=2)
        ctk.CTkEntry(coords_frame, textvariable=self.app.center_y, width=80).grid(row=0, column=4, padx=2)
        ctk.CTkLabel(coords_frame, text="Z:").grid(row=0, column=5, padx=2)
        ctk.CTkEntry(coords_frame, textvariable=self.app.center_z, width=80).grid(row=0, column=6, padx=2)
        
        ctk.CTkLabel(coords_frame, text="Docking Box Size (Å):").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        ctk.CTkLabel(coords_frame, text="X:").grid(row=1, column=1, padx=2)
        ctk.CTkEntry(coords_frame, textvariable=self.app.size_x, width=80).grid(row=1, column=2, padx=2)
        ctk.CTkLabel(coords_frame, text="Y:").grid(row=1, column=3, padx=2)
        ctk.CTkEntry(coords_frame, textvariable=self.app.size_y, width=80).grid(row=1, column=4, padx=2)
        ctk.CTkLabel(coords_frame, text="Z:").grid(row=1, column=5, padx=2)
        ctk.CTkEntry(coords_frame, textvariable=self.app.size_z, width=80).grid(row=1, column=6, padx=2)
        
        # Exhaustiveness
        exh_frame = ctk.CTkFrame(docking_frame, fg_color="transparent")
        exh_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(exh_frame, text="Exhaustiveness:", font=ctk.CTkFont(size=14)).pack(side="left")
        ctk.CTkEntry(exh_frame, textvariable=self.app.exhaustiveness, width=80).pack(side="left", padx=5)
        
        ctk.CTkCheckBox(
            exh_frame,
            text="Adaptive Exhaustiveness",
            variable=self.app.use_adaptive_exhaustiveness
        ).pack(side="left", padx=20)
    
    def _create_control_buttons(self):
        """Create control buttons section."""
        button_frame = ctk.CTkFrame(self.scrollable_frame)
        button_frame.pack(fill="x", pady=10, padx=10)
        
        ctk.CTkButton(
            button_frame,
            text="Advanced Settings",
            command=self.app._open_settings,
            width=120
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Calculate Coordinates",
            command=self.app._start_coordinate_calculation,
            width=140
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Start Docking",
            command=self.app.start_docking,
            fg_color="#2aa876",
            hover_color="#228c61",
            width=120
        ).pack(side="right", padx=5)
    
    def refresh_ligand_list(self):
        """Refresh the ligand listbox."""
        self.ligand_listbox.delete(0, tk.END)
        for path in self.app.ligand_library:
            self.ligand_listbox.insert(tk.END, os.path.basename(path))

    def refresh_receptor_list(self):
        """Refresh the receptor listbox."""
        self.receptor_listbox.delete(0, tk.END)
        for receptor in self.app.receptors_data:
            name = os.path.basename(receptor['path'])
            self.receptor_listbox.insert(tk.END, name)
        
        # Restore selection if possible
        if self.app.current_receptor_index >= 0 and self.app.current_receptor_index < len(self.app.receptors_data):
            self.receptor_listbox.selection_set(self.app.current_receptor_index)

    def _detect_active_sites(self):
        """Detect active sites in the receptor."""
        receptor_path = self.app.receptor_path.get()
        if not receptor_path:
            messagebox.showwarning("No Receptor", "Please select a receptor first.")
            return
            
        # Try to find original PDB if available (for better metadata)
        # Our FileProcessor saves it as {pdb_id}_original.pdb
        # If the user selected a file manually, we just use that.
        
        target_path = receptor_path
        directory = os.path.dirname(receptor_path)
        filename = os.path.basename(receptor_path)
        
        # Heuristic: if file is X_cleaned.pdb, look for X_original.pdb
        if "_cleaned.pdb" in filename:
            original_name = filename.replace("_cleaned.pdb", "_original.pdb")
            original_path = os.path.join(directory, original_name)
            if os.path.exists(original_path):
                target_path = original_path
        
        try:
            finder = PocketFinder()
            pockets = finder.find_pockets(target_path)
            
            if not pockets:
                messagebox.showinfo("No Sites Detected", 
                                  "No active sites detected in PDB metadata or co-crystallized ligands.\n\n"
                                  "Please define the binding box manually.")
                return
                
            # Show selection dialog
            dialog = PocketSelectionDialog(self.parent, pockets, self._on_pocket_selected)
            dialog.show()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to detect active sites: {e}")
            
    def _on_pocket_selected(self, pocket: Dict):
        """Handle pocket selection."""
        # Set mode to Targeted Docking
        self.app.docking_mode.set("Targeted Docking")
        
        # Update coordinates
        center = pocket['center']
        size = pocket['size']
        
        self.app.center_x.set(round(center[0], 3))
        self.app.center_y.set(round(center[1], 3))
        self.app.center_z.set(round(center[2], 3))
        
        self.app.size_x.set(round(size[0], 3))
        self.app.size_y.set(round(size[1], 3))
        self.app.size_z.set(round(size[2], 3))
        
        messagebox.showinfo("Site Selected", f"Selected: {pocket['name']}\nCoordinates updated.")


class ResultsTab:
    """Results display tab component."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.current_page = 0
        self.page_size = 50
        self.current_data = [] # Stores full dataset
        self.total_pages = 0
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the results tab UI."""
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            main_frame,
            text="Docking Results",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 10))
        
        # Results container
        self.results_frame = ctk.CTkFrame(main_frame)
        self.results_frame.pack(fill="both", expand=True)
        
        # Initial message
        self.initial_label = ctk.CTkLabel(
            self.results_frame,
            text="No docking results yet. Run a docking simulation to see results here.",
            font=ctk.CTkFont(size=16)
        )
        self.initial_label.pack(expand=True)
        
        # [PAGINATION] Pagination Controls Frame (Below results, above actions)
        self.pagination_frame = ctk.CTkFrame(main_frame, fg_color="transparent", height=30)
        
        self.btn_prev = ctk.CTkButton(self.pagination_frame, text="< Prev", width=60, command=self._prev_page, state="disabled")
        self.btn_prev.pack(side="left", padx=5)
        
        self.lbl_page = ctk.CTkLabel(self.pagination_frame, text="Page 1 of 1")
        self.lbl_page.pack(side="left", padx=10)
        
        self.btn_next = ctk.CTkButton(self.pagination_frame, text="Next >", width=60, command=self._next_page, state="disabled")
        self.btn_next.pack(side="left", padx=5)
        
        # Buttons frame (initially hidden)
        self.button_frame = ctk.CTkFrame(main_frame)
        
        self.visualize_button = ctk.CTkButton(
            self.button_frame,
            text="Visualize Results",
            command=self.app.visualize_results,
            width=120
        )
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save Results",
            command=self._save_results,
            width=120
        )
        
    def _clear_results(self):
        """Clear existing results from the view."""
        self.initial_label.pack_forget()
        self.pagination_frame.pack_forget()
        self.button_frame.pack_forget()
        
        # Destroy all children of results_frame EXCEPT initial_label 
        # (Wait, initial_label is child of results_frame?)
        # Yes: self.initial_label = ctk.CTkLabel(self.results_frame, ...)
        
        # Safer: Just destroy all children of results_frame and recreate initial_label if needed?
        # Or iterate and destroy frames
        for widget in self.results_frame.winfo_children():
            if widget != self.initial_label:
                widget.destroy()

    def _show_message(self, message: str):
        """Show a message in the results area."""
        self._clear_results()
        self.initial_label.configure(text=message)
        self.initial_label.pack(expand=True)
    
    def show_single_results(self, results: List[Dict]):
        """Show single docking results."""
        self._clear_results()
        self.title_label.configure(text="Single Docking Results")
        
        # Hide pagination for single results (usually small)
        self.pagination_frame.pack_forget()
        
        if not results:
            self._show_message("No results to display.")
            return
        
        # Create results table
        tree_frame = ctk.CTkFrame(self.results_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Create treeview
        from tkinter import ttk
        
        # Configure treeview style
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Roboto', 12, 'bold'))
        style.configure("Treeview", font=('Roboto', 11), rowheight=25)
        
        columns = ('mode', 'affinity', 'rmsd_lb', 'rmsd_ub')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=12)
        
        # Configure columns
        self.tree.heading('mode', text='Mode')
        self.tree.heading('affinity', text='Affinity (kcal/mol')
        self.tree.heading('rmsd_lb', text='RMSD L.B.')
        self.tree.heading('rmsd_ub', text='RMSD U.B.')
        
        self.tree.column('mode', width=80, anchor=tk.CENTER)
        self.tree.column('affinity', width=120, anchor=tk.CENTER)
        self.tree.column('rmsd_lb', width=100, anchor=tk.CENTER)
        self.tree.column('rmsd_ub', width=100, anchor=tk.CENTER)
        
        # Populate data
        for score in results:
            # Handle missing RMSD values (e.g., for rDock, LeDock)
            affinity = score.get('Affinity (kcal/mol)', '')
            rmsd_lb = score.get('RMSD L.B.', '')
            rmsd_ub = score.get('RMSD U.B.', '')
            
            self.tree.insert('', tk.END, values=(
                score.get('Mode', ''),
                f"{affinity:.2f}" if isinstance(affinity, (int, float)) else affinity,
                f"{rmsd_lb:.2f}" if isinstance(rmsd_lb, (int, float)) else 'N/A',
                f"{rmsd_ub:.2f}" if isinstance(rmsd_ub, (int, float)) else 'N/A'
            ))
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Show buttons
        self._show_buttons()
    
    def show_batch_results(self, summary_results: List[Dict], full_results: List[Dict]):
        """Show batch docking results with pagination."""
        self._clear_results()
        self.title_label.configure(text=f"Batch Docking Results ({len(summary_results)} ligands)")
        
        if not summary_results:
            self._show_message("No results to display.")
            return
            
        # [PAGINATION] Initialize data
        self.current_data = summary_results
        self.current_page = 0
        from math import ceil
        self.total_pages = ceil(len(summary_results) / self.page_size)
        
        # Establish TreeView structure ONE TIME
        tree_frame = ctk.CTkFrame(self.results_frame)
        tree_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        from tkinter import ttk
        columns = ('receptor', 'ligand', 'affinity', 'engine', 'status', 'message')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=15)
        
        self.tree.heading('receptor', text='Receptor')
        self.tree.heading('ligand', text='Ligand')
        self.tree.heading('affinity', text='Best Affinity (kcal/mol)')
        self.tree.heading('engine', text='Engine')
        self.tree.heading('status', text='Status')
        self.tree.heading('message', text='Message')
        
        self.tree.column('receptor', width=120, anchor='w')
        self.tree.column('ligand', width=150, anchor='w')
        self.tree.column('affinity', width=100, anchor=tk.CENTER)
        self.tree.column('engine', width=80, anchor=tk.CENTER)
        self.tree.column('status', width=80, anchor=tk.CENTER)
        self.tree.column('message', width=250, anchor='w')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # [PAGINATION] Show controls if needed
        if self.total_pages > 1:
            self.pagination_frame.pack(pady=5, before=self.button_frame) # Ensure it's above action buttons
        else:
            self.pagination_frame.pack_forget()
            
        # Render initial page
        self._update_table()
        
        # Show buttons
        self._show_buttons()

    def _update_table(self):
        """Render the current page of data."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Calculate slice
        start_idx = self.current_page * self.page_size
        end_idx = start_idx + self.page_size
        page_items = self.current_data[start_idx:end_idx]
        
        # Populate
        for result in page_items:
            affinity = result.get('Best Affinity (kcal/mol)', 'N/A')
            if isinstance(affinity, (int, float)):
                affinity = f"{affinity:.2f}"
            
            self.tree.insert('', tk.END, values=(
                result.get('Receptor', 'N/A'),
                result['Ligand'],
                affinity,
                result.get('Engine', 'Vina'),
                result.get('Status', 'Unknown'),
                result.get('Error', '')
            ))
            
        # Update Controls
        self.lbl_page.configure(text=f"Page {self.current_page + 1} of {self.total_pages}")
        
        self.btn_prev.configure(state="normal" if self.current_page > 0 else "disabled")
        self.btn_next.configure(state="normal" if self.current_page < self.total_pages - 1 else "disabled")

    def _next_page(self):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self._update_table()
            
    def _prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._update_table()
            
    def _show_buttons(self):
        """Show action buttons."""
        self.button_frame.pack(fill="x", pady=(10, 0)) # Ensure pack order
        if not self.visualize_button.winfo_ismapped():
            self.visualize_button.pack(side="left", padx=5)
        if not self.save_button.winfo_ismapped():
            self.save_button.pack(side="left", padx=5)
    
    def _save_results(self):
        """Save results to file."""
        if not self.app.last_results and not self.app.batch_results_summary:
            messagebox.showwarning("Warning", "No results to save.")
            return
        
        # Check for selection
        selected_items = []
        if hasattr(self, 'tree'):
            selected_items = self.tree.selection()
            
        filename = filedialog.asksaveasfilename(
            title="Save Results As",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', newline='') as f:
                    writer = csv.writer(f)
                    
                    if self.app.last_run_type == 'single' and self.app.last_results:
                        # Save single results
                        writer.writerow(['Mode', 'Affinity (kcal/mol)', 'RMSD L.B.', 'RMSD U.B.', 'Engine', 'Receptor', 'Ligand'])
                        
                        receptor = os.path.basename(self.app.receptor_path.get())
                        ligand = os.path.basename(self.app.ligand_library[0]) if self.app.ligand_library else "Unknown"
                        
                        for result in self.app.last_results:
                            writer.writerow([
                                result.get('Mode', ''),
                                result.get('Affinity (kcal/mol)', ''),
                                result.get('RMSD L.B.', ''),
                                result.get('RMSD U.B.', ''),
                                result.get('Engine', 'Vina'),
                                receptor,
                                ligand
                            ])
                    
                    elif self.app.last_run_type == 'batch' and self.app.batch_results_summary:
                        # Determine which results to export
                        results_to_export = []
                        
                        if selected_items:
                            # Filter based on selection
                            # We need to map tree items back to results
                            # Tree items are in same order as summary list if we didn't sort
                            # But user might have sorted? Treeview doesn't sort by default unless configured.
                            # Assuming index matches for now as we just inserted them.
                            
                            # Get all items in tree to find indices on current page
                            all_items = self.tree.get_children()
                            
                            # Calculate offset for current page
                            page_offset = self.current_page * self.page_size
                            
                            # Map tree indices to global indices
                            selected_indices = [all_items.index(item) + page_offset for item in selected_items]
                            
                            # Get selected summary items
                            selected_summary = [self.app.batch_results_summary[i] for i in selected_indices if i < len(self.app.batch_results_summary)]
                            
                            # Now find corresponding full results
                            for summary in selected_summary:
                                receptor = summary['Receptor']
                                ligand = summary['Ligand']
                                
                                # Find all modes for this pair in full_batch_results
                                modes = [r for r in self.app.full_batch_results 
                                        if r['Receptor'] == receptor and r['Ligand'] == ligand]
                                
                                if modes:
                                    results_to_export.extend(modes)
                                else:
                                    # Fallback if full results missing
                                    results_to_export.append(summary)
                        else:
                            # Export all
                            results_to_export = self.app.full_batch_results if self.app.full_batch_results else self.app.batch_results_summary

                        # Save batch results
                        # Get all keys for header
                        keys = ['Receptor', 'Ligand', 'Mode', 'Best Affinity (kcal/mol)', 'RMSD L.B.', 'RMSD U.B.', 'Engine', 'Status', 'Error', 'OutputFile']
                        writer.writerow(keys)
                        
                        for result in results_to_export:
                            # Handle affinity key variation
                            affinity = result.get('Affinity (kcal/mol)')
                            if affinity is None:
                                affinity = result.get('Best Affinity (kcal/mol)')
                                
                            writer.writerow([
                                result.get('Receptor', ''),
                                result.get('Ligand', ''),
                                result.get('Mode', ''),
                                affinity,
                                result.get('RMSD L.B.', ''),
                                result.get('RMSD U.B.', ''),
                                result.get('Engine', 'Vina'),
                                result.get('Status', 'Success'),
                                result.get('Error', ''),
                                result.get('OutputFile', '')
                            ])
                
                messagebox.showinfo("Success", f"Results saved to {filename}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save results: {e}")


class VisualizationTab:
    """Visualization tab component."""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the visualization tab UI."""
        main_frame = ctk.CTkFrame(self.parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title
        self.title_label = ctk.CTkLabel(
            main_frame,
            text="Results Visualization",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        self.title_label.pack(anchor="w", pady=(0, 10))
        
        # Content frame
        content_frame = ctk.CTkFrame(main_frame)
        content_frame.pack(fill="both", expand=True)
        
        # Initial message
        self.initial_label = ctk.CTkLabel(
            content_frame,
            text="Visualization options will appear here after docking.\n\n"
                 "You can visualize single docking results or browse batch results.",
            font=ctk.CTkFont(size=16),
            justify="left"
        )
        self.initial_label.pack(expand=True)
        
        # Visualization controls (initially hidden)
        self.controls_frame = ctk.CTkFrame(content_frame)
        
        # Batch results list
        self.batch_frame = ctk.CTkFrame(content_frame)
        self.batch_listbox = None
        self.visualize_batch_button = None
    
    def visualize_single_results(self, receptor_path: str, results_path: str, viewer: str = "ChimeraX"):
        """Visualize single docking results."""
        self._clear_visualization()
        
        try:
            info_text = f"""Ready to visualize results with {viewer}:

Receptor: {os.path.basename(receptor_path)}
Results: {os.path.basename(results_path)}

Click the button below to launch the visualization."""

            info_label = ctk.CTkLabel(
                self.controls_frame,
                text=info_text,
                font=ctk.CTkFont(size=12),
                justify="left"
            )
            info_label.pack(padx=10, pady=10, anchor="w")
            
            # Launch visualization button
            ctk.CTkButton(
                self.controls_frame,
                text=f"Launch {viewer}",
                command=lambda: self._launch_visualization(receptor_path, results_path, viewer),
                width=120,
                fg_color="#2aa876",
                hover_color="#228c61"
            ).pack(pady=10)
            
            self.controls_frame.pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Visualization Error", f"Failed to setup visualization: {e}")
    
    def _prompt_for_executable(self, name: str, title: str) -> Optional[str]:
        """Prompt user to select an executable."""
        messagebox.showinfo(f"{title} Not Found", 
                          f"Could not find {name} automatically.\n"
                          f"Please select the {name} executable file.")
        
        path = filedialog.askopenfilename(
            title=f"Select {title} Executable",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")]
        )
        
        if path:
            # Save to config
            try:
                from utils.config import get_config_manager
                config_manager = get_config_manager()
                platform_config = config_manager.get_platform_config()
                
                # Update platform specific setting
                config_manager.set_setting("platform_settings", sys.platform if sys.platform != 'win32' else 'windows',
                                         {**platform_config, name.lower(): path})
                config_manager.save_config()
                return path
            except Exception as e:
                print(f"Failed to save config: {e}")
                return path
        return None

    def _launch_visualization(self, receptor_path: str, results_path: str, viewer: str):
        """Launch external visualization tool."""
        try:
            if viewer == "VMD":
                self._launch_vmd(receptor_path, results_path)
            elif viewer == "ChimeraX":
                self._launch_chimerax(receptor_path, results_path)
            else:
                messagebox.showerror("Error", f"Unsupported viewer: {viewer}")
                
        except Exception as e:
            messagebox.showerror("Visualization Error", f"Failed to launch {viewer}: {e}")
    
    def _launch_vmd(self, receptor_path: str, results_path: str):
        """Launch VMD with receptor and results."""
        try:
            from utils.config import get_config_manager
            config_manager = get_config_manager()
            vmd_path = config_manager.get_executable_path("vmd")
            
            # Check if exists
            if not vmd_path or not os.path.exists(vmd_path):
                vmd_path = self._prompt_for_executable("vmd", "VMD")
                if not vmd_path:
                    return
            
            # Create a temporary script for VMD
            temp_dir = self.app.file_manager.create_temp_directory()
            script_path = os.path.join(temp_dir, "vmd_script.tcl")
            
            # Create VMD script
            script_content = f"""
# Load receptor
mol new "{receptor_path}" type pdbqt
# Load docked poses
mol new "{results_path}" type pdbqt

# Style settings
mol modstyle 0 0 NewCartoon
mol modcolor 0 0 Chain
mol modstyle 1 0 Licorice
mol modcolor 1 0 ColorID 1

# Zoom to see everything
scale by 1.2
"""
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Launch VMD
            cmd = [vmd_path, "-e", script_path]
            subprocess.Popen(cmd)
            messagebox.showinfo("Success", f"VMD launched with receptor and results!")
            
        except Exception as e:
            messagebox.showerror("VMD Error", f"Failed to launch VMD: {e}\n\nMake sure VMD is installed and configured in settings.")
    
    def _launch_chimerax(self, receptor_path: str, results_path: str):
        """Launch ChimeraX with receptor and results."""
        try:
            from utils.config import get_config_manager
            config_manager = get_config_manager()
            chimerax_path = config_manager.get_executable_path("chimerax")
            
            # Strict validation
            is_valid = False
            if chimerax_path and os.path.isfile(chimerax_path):
                filename = os.path.basename(chimerax_path).lower()
                if "chimerax" in filename and "python" not in filename and "simdock" not in filename:
                    is_valid = True
            
            if not is_valid:
                chimerax_path = self._prompt_for_executable("chimerax", "ChimeraX")
                if not chimerax_path:
                    return
            
            # Create a temporary script for ChimeraX
            temp_dir = self.app.file_manager.create_temp_directory()
            script_path = os.path.join(temp_dir, "chimerax_script.cxc")
            
            # Create ChimeraX script
            script_content = f"""
# Open receptor and results
open "{receptor_path}"
open "{results_path}"

# Style settings
cartoon
color bychain
style ligand ball
color ligand red

# View settings
view
"""
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            # Launch ChimeraX
            if not os.path.isfile(chimerax_path):
                messagebox.showerror("Error", f"ChimeraX path is not a file: {chimerax_path}")
                return

            cmd = [chimerax_path, "--script", script_path]
            # messagebox.showinfo("Debug", f"Launching: {chimerax_path}\nScript: {script_path}")
            subprocess.Popen(cmd)
            messagebox.showinfo("Success", f"ChimeraX launched with receptor and results!")
            
        except Exception as e:
            messagebox.showerror("ChimeraX Error", f"Failed to launch ChimeraX: {e}\n\nMake sure ChimeraX is installed and configured in settings.")
    
    def _clear_visualization(self):
        """Clear visualization area."""
        self.initial_label.pack_forget()
        self.controls_frame.pack_forget()
        self.batch_frame.pack_forget()
        
        for widget in self.controls_frame.winfo_children():
            widget.destroy()
        
        for widget in self.batch_frame.winfo_children():
            widget.destroy()
    
    def show_batch_visualization(self, results_summary: List[Dict]):
        """Show batch visualization options."""
        self._clear_visualization()
        
        if not results_summary:
            self._show_message("No batch results to visualize.")
            return
        
        # Recreate widgets
        self.batch_label = ctk.CTkLabel(
            self.batch_frame,
            text="Batch Results:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.batch_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # List container
        list_container = ctk.CTkFrame(self.batch_frame)
        list_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        scrollbar = ttk.Scrollbar(list_container, orient="vertical")
        
        self.batch_listbox = tk.Listbox(
            list_container,
            height=10,
            bg='#343638',
            fg='white',
            selectbackground='#3b8ed0',
            selectforeground='white',
            yscrollcommand=scrollbar.set
        )
        scrollbar.configure(command=self.batch_listbox.yview)
        
        self.batch_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Populate batch list
        for result in results_summary:
            self.batch_listbox.insert(tk.END, f"{result['Receptor']} - {result['Ligand']}")
            
        self.visualize_batch_button = ctk.CTkButton(
            self.batch_frame,
            text="Visualize Selected",
            command=self._visualize_selected_batch,
            width=120
        )
        self.visualize_batch_button.pack(pady=10)
        
        self.batch_frame.pack(fill="both", expand=True)
    
    def _visualize_selected_batch(self):
        """Visualize selected batch result."""
        try:
            # messagebox.showinfo("Debug", "Visualizing selected batch...")
            selection = self.batch_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "Please select a result to visualize.")
                return
            
            index = selection[0]
            if index < 0 or index >= len(self.app.batch_results_summary):
                 messagebox.showerror("Debug", f"Index {index} out of bounds (len={len(self.app.batch_results_summary)})")
                 return

            result = self.app.batch_results_summary[index]
            
            result_file = result.get('OutputFile')
            receptor_path = result.get('ReceptorPath')
            
            # Fallback to app's receptor path if not in result (legacy/single receptor batch)
            if not receptor_path:
                 receptor_path = self.app.receptor_pdbqt_path

            viewer = self.app.viewer_choice.get()
            # messagebox.showinfo("Debug", f"Viewer: {viewer}\nReceptor: {receptor_path}\nResult: {result_file}")

            if result_file and os.path.exists(result_file) and receptor_path and os.path.exists(receptor_path):
                self._launch_visualization(receptor_path, result_file, viewer)
            else:
                messagebox.showerror("Error", f"Could not find result file or receptor for {result['Ligand']}\nReceptor: {receptor_path}\nResult: {result_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Unexpected error in visualize: {e}")
            import traceback
            traceback.print_exc()
    
    def _show_message(self, message: str):
        """Show a message in the visualization area."""
        label = ctk.CTkLabel(
            self.controls_frame,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        label.pack(expand=True)
        self.controls_frame.pack(fill="both", expand=True)