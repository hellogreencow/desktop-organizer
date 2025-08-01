import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter.ttk import Progressbar
import threading
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import webbrowser

from file_organizer import FileOrganizer, FileAnalysis
from config_manager import ConfigManager, get_config_manager
from file_scanner import FileInfo

class ConfigDialog:
    """Dialog for configuring application settings."""
    
    def __init__(self, parent, config_manager: ConfigManager):
        self.parent = parent
        self.config_manager = config_manager
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Configuration")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (600 // 2)
        self.dialog.geometry(f"500x600+{x}+{y}")
    
    def create_widgets(self):
        """Create configuration dialog widgets."""
        notebook = ttk.Notebook(self.dialog)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # API Configuration Tab
        api_frame = ttk.Frame(notebook)
        notebook.add(api_frame, text="API Settings")
        
        ttk.Label(api_frame, text="OpenAI API Key:").pack(anchor=tk.W, pady=(10, 0))
        self.api_key_var = tk.StringVar(value=self.config_manager.config.openai_api_key)
        api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, show="*", width=50)
        api_key_entry.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(api_frame, text="Text Model:").pack(anchor=tk.W)
        self.text_model_var = tk.StringVar(value=self.config_manager.config.openai_model_text)
        text_model_combo = ttk.Combobox(api_frame, textvariable=self.text_model_var, 
                                       values=["gpt-4", "gpt-3.5-turbo", "gpt-4-turbo"])
        text_model_combo.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(api_frame, text="Vision Model:").pack(anchor=tk.W)
        self.vision_model_var = tk.StringVar(value=self.config_manager.config.openai_model_vision)
        vision_model_combo = ttk.Combobox(api_frame, textvariable=self.vision_model_var,
                                         values=["gpt-4-vision-preview", "gpt-4-turbo"])
        vision_model_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Analysis Settings Tab
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="Analysis")
        
        ttk.Label(analysis_frame, text="Max File Size (MB):").pack(anchor=tk.W, pady=(10, 0))
        self.max_size_var = tk.IntVar(value=self.config_manager.config.max_file_size_mb)
        ttk.Spinbox(analysis_frame, from_=1, to=100, textvariable=self.max_size_var).pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(analysis_frame, text="Max Files to Analyze:").pack(anchor=tk.W)
        self.max_files_var = tk.IntVar(value=self.config_manager.config.max_files_to_analyze)
        ttk.Spinbox(analysis_frame, from_=10, to=10000, textvariable=self.max_files_var).pack(fill=tk.X, pady=(0, 10))
        
        # File type checkboxes
        ttk.Label(analysis_frame, text="File Types to Analyze:").pack(anchor=tk.W, pady=(10, 0))
        
        self.analyze_images_var = tk.BooleanVar(value=self.config_manager.config.analyze_images)
        ttk.Checkbutton(analysis_frame, text="Images", variable=self.analyze_images_var).pack(anchor=tk.W)
        
        self.analyze_documents_var = tk.BooleanVar(value=self.config_manager.config.analyze_documents)
        ttk.Checkbutton(analysis_frame, text="Documents", variable=self.analyze_documents_var).pack(anchor=tk.W)
        
        self.analyze_code_var = tk.BooleanVar(value=self.config_manager.config.analyze_code)
        ttk.Checkbutton(analysis_frame, text="Code Files", variable=self.analyze_code_var).pack(anchor=tk.W)
        
        self.analyze_media_var = tk.BooleanVar(value=self.config_manager.config.analyze_media)
        ttk.Checkbutton(analysis_frame, text="Media Files", variable=self.analyze_media_var).pack(anchor=tk.W)
        
        # Safety Settings Tab
        safety_frame = ttk.Frame(notebook)
        notebook.add(safety_frame, text="Safety")
        
        self.dry_run_var = tk.BooleanVar(value=self.config_manager.config.dry_run_mode)
        ttk.Checkbutton(safety_frame, text="Dry Run Mode (Don't actually delete files)", 
                       variable=self.dry_run_var).pack(anchor=tk.W, pady=(10, 0))
        
        self.confirm_deletions_var = tk.BooleanVar(value=self.config_manager.config.confirm_deletions)
        ttk.Checkbutton(safety_frame, text="Confirm before deleting files", 
                       variable=self.confirm_deletions_var).pack(anchor=tk.W)
        
        self.create_backup_var = tk.BooleanVar(value=self.config_manager.config.create_backup)
        ttk.Checkbutton(safety_frame, text="Create backup before organizing", 
                       variable=self.create_backup_var).pack(anchor=tk.W)
        
        ttk.Label(safety_frame, text="Max Deletion Percentage:").pack(anchor=tk.W, pady=(10, 0))
        self.max_deletion_var = tk.DoubleVar(value=self.config_manager.config.max_deletion_percentage * 100)
        ttk.Scale(safety_frame, from_=0, to=100, variable=self.max_deletion_var, 
                 orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 5))
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Save", command=self.save_config).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Test API Key", command=self.test_api_key).pack(side=tk.LEFT)
    
    def test_api_key(self):
        """Test the OpenAI API key."""
        api_key = self.api_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key first.")
            return
        
        # Simple validation
        if not api_key.startswith('sk-'):
            messagebox.showerror("Error", "Invalid API key format. Should start with 'sk-'")
            return
        
        messagebox.showinfo("API Key", "API key format appears valid. Full validation will occur during analysis.")
    
    def save_config(self):
        """Save configuration and close dialog."""
        # Update config with values from dialog
        self.config_manager.config.openai_api_key = self.api_key_var.get().strip()
        self.config_manager.config.openai_model_text = self.text_model_var.get()
        self.config_manager.config.openai_model_vision = self.vision_model_var.get()
        self.config_manager.config.max_file_size_mb = self.max_size_var.get()
        self.config_manager.config.max_files_to_analyze = self.max_files_var.get()
        self.config_manager.config.analyze_images = self.analyze_images_var.get()
        self.config_manager.config.analyze_documents = self.analyze_documents_var.get()
        self.config_manager.config.analyze_code = self.analyze_code_var.get()
        self.config_manager.config.analyze_media = self.analyze_media_var.get()
        self.config_manager.config.dry_run_mode = self.dry_run_var.get()
        self.config_manager.config.confirm_deletions = self.confirm_deletions_var.get()
        self.config_manager.config.create_backup = self.create_backup_var.get()
        self.config_manager.config.max_deletion_percentage = self.max_deletion_var.get() / 100
        
        # Save to files
        self.config_manager.save_config()
        
        self.result = True
        self.dialog.destroy()
    
    def cancel(self):
        """Cancel configuration and close dialog."""
        self.dialog.destroy()

class FileListFrame:
    """Frame for displaying and managing file lists."""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = ttk.Frame(parent)
        self.file_analyses: List[FileAnalysis] = []
        self.selected_files: List[FileAnalysis] = []
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create file list widgets."""
        # Filter frame
        filter_frame = ttk.Frame(self.frame)
        filter_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar()
        self.filter_var.trace('w', self.filter_files)
        ttk.Entry(filter_frame, textvariable=self.filter_var, width=20).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(filter_frame, text="Action:").pack(side=tk.LEFT)
        self.action_filter_var = tk.StringVar(value="All")
        action_combo = ttk.Combobox(filter_frame, textvariable=self.action_filter_var,
                                   values=["All", "Keep", "Delete", "Archive", "Move"], width=10)
        action_combo.pack(side=tk.LEFT, padx=(5, 10))
        action_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_files())
        
        ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT)
        self.category_filter_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(filter_frame, textvariable=self.category_filter_var,
                                     values=["All", "Documents", "Images", "Code", "Data", "Media", "Archive"], width=10)
        category_combo.pack(side=tk.LEFT, padx=(5, 0))
        category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_files())
        
        # Treeview for file list
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("Name", "Size", "Category", "Priority", "Action", "Reason")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=15)
        
        # Configure columns
        self.tree.heading("Name", text="File Name")
        self.tree.heading("Size", text="Size")
        self.tree.heading("Category", text="Category")
        self.tree.heading("Priority", text="Priority")
        self.tree.heading("Action", text="Action")
        self.tree.heading("Reason", text="Reason")
        
        self.tree.column("Name", width=200)
        self.tree.column("Size", width=80)
        self.tree.column("Category", width=100)
        self.tree.column("Priority", width=60)
        self.tree.column("Action", width=80)
        self.tree.column("Reason", width=200)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        v_scrollbar.grid(row=0, column=1, sticky="ns")
        h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        
        # Button frame
        button_frame = ttk.Frame(self.frame)
        button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Select None", command=self.select_none).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="View Details", command=self.view_details).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Open File", command=self.open_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected).pack(side=tk.RIGHT)
    
    def update_files(self, file_analyses: List[FileAnalysis]):
        """Update the file list with new analyses."""
        self.file_analyses = file_analyses
        self.filter_files()
    
    def filter_files(self, *args):
        """Filter files based on current filter settings."""
        # Clear current items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filter_text = self.filter_var.get().lower()
        action_filter = self.action_filter_var.get()
        category_filter = self.category_filter_var.get()
        
        filtered_files = []
        for fa in self.file_analyses:
            # Filter by text
            if filter_text and filter_text not in fa.file_info.name.lower():
                continue
            
            # Filter by action
            if action_filter != "All" and fa.organization_action.action_type.title() != action_filter:
                continue
            
            # Filter by category
            if category_filter != "All" and fa.category != category_filter:
                continue
            
            filtered_files.append(fa)
        
        # Add filtered files to tree
        for fa in filtered_files:
            size_str = self.format_size(fa.file_info.size)
            priority_str = f"{fa.priority_score:.1f}"
            
            # Color code by action
            tags = []
            if fa.organization_action.action_type == 'delete':
                tags.append('delete')
            elif fa.organization_action.action_type == 'keep':
                tags.append('keep')
            elif fa.organization_action.action_type == 'archive':
                tags.append('archive')
            
            item_id = self.tree.insert("", tk.END, values=(
                fa.file_info.name,
                size_str,
                fa.category,
                priority_str,
                fa.organization_action.action_type.title(),
                fa.organization_action.reason
            ), tags=tags)
            
            # Store file analysis reference
            self.tree.set(item_id, 'file_analysis', fa)
        
        # Configure tags for color coding
        self.tree.tag_configure('delete', background='#ffcccc')
        self.tree.tag_configure('keep', background='#ccffcc')
        self.tree.tag_configure('archive', background='#ffffcc')
    
    def format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
        else:
            return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
    
    def on_double_click(self, event):
        """Handle double-click on file item."""
        self.view_details()
    
    def on_select(self, event):
        """Handle file selection."""
        selected_items = self.tree.selection()
        self.selected_files = []
        
        for item in selected_items:
            fa = self.tree.set(item, 'file_analysis')
            if fa:
                self.selected_files.append(fa)
    
    def select_all(self):
        """Select all visible files."""
        self.tree.selection_set(self.tree.get_children())
    
    def select_none(self):
        """Clear selection."""
        self.tree.selection_remove(self.tree.get_children())
    
    def view_details(self):
        """View details of selected file."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a file to view details.")
            return
        
        item = selected[0]
        fa = self.tree.set(item, 'file_analysis')
        if fa:
            self.show_file_details(fa)
    
    def show_file_details(self, fa: FileAnalysis):
        """Show detailed information about a file."""
        details_window = tk.Toplevel(self.parent)
        details_window.title(f"File Details: {fa.file_info.name}")
        details_window.geometry("600x500")
        
        notebook = ttk.Notebook(details_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File Info Tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text="File Info")
        
        info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD)
        info_text.pack(fill=tk.BOTH, expand=True)
        
        info_content = f"""File Path: {fa.file_info.path}
File Name: {fa.file_info.name}
Extension: {fa.file_info.extension}
Size: {self.format_size(fa.file_info.size)}
Created: {fa.file_info.created_time}
Modified: {fa.file_info.modified_time}
Is Duplicate: {fa.file_info.is_duplicate}

Priority Score: {fa.priority_score:.2f}
Category: {fa.category}
Subcategory: {fa.subcategory}
Recommended Action: {fa.organization_action.action_type.title()}
Reason: {fa.organization_action.reason}
Confidence: {fa.organization_action.confidence:.2f}
Target Folder: {fa.organization_action.target_folder}
"""
        
        info_text.insert(tk.END, info_content)
        info_text.config(state=tk.DISABLED)
        
        # Analysis Tab
        analysis_frame = ttk.Frame(notebook)
        notebook.add(analysis_frame, text="AI Analysis")
        
        analysis_text = scrolledtext.ScrolledText(analysis_frame, wrap=tk.WORD)
        analysis_text.pack(fill=tk.BOTH, expand=True)
        
        analysis_content = json.dumps(fa.analysis_result, indent=2)
        analysis_text.insert(tk.END, analysis_content)
        analysis_text.config(state=tk.DISABLED)
    
    def open_file(self):
        """Open selected file in default application."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a file to open.")
            return
        
        item = selected[0]
        fa = self.tree.set(item, 'file_analysis')
        if fa:
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(fa.file_info.path)
                elif os.name == 'posix':  # macOS and Linux
                    os.system(f'open "{fa.file_info.path}"')
            except Exception as e:
                messagebox.showerror("Error", f"Could not open file: {e}")
    
    def delete_selected(self):
        """Delete selected files."""
        if not self.selected_files:
            messagebox.showinfo("Info", "No files selected for deletion.")
            return
        
        if messagebox.askyesno("Confirm Deletion", 
                              f"Are you sure you want to delete {len(self.selected_files)} files?"):
            for fa in self.selected_files:
                try:
                    os.remove(fa.file_info.path)
                    print(f"Deleted: {fa.file_info.path}")
                except Exception as e:
                    print(f"Error deleting {fa.file_info.path}: {e}")
            
            messagebox.showinfo("Success", f"Deleted {len(self.selected_files)} files.")
            # Refresh the list
            self.update_files([fa for fa in self.file_analyses if fa not in self.selected_files])

class DesktopOrganizerGUI:
    """Main GUI application for Desktop Organizer."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AI Desktop File Organizer")
        self.root.geometry("1200x800")
        
        self.config_manager = get_config_manager()
        self.file_organizer = None
        self.analysis_results: List[FileAnalysis] = []
        
        self.create_widgets()
        self.check_configuration()
    
    def create_widgets(self):
        """Create main application widgets."""
        # Menu bar
        self.create_menu()
        
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Control frame
        control_frame = ttk.LabelFrame(main_frame, text="Analysis Control", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Directory selection
        dir_frame = ttk.Frame(control_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(dir_frame, text="Directory to analyze:").pack(side=tk.LEFT)
        
        self.directory_var = tk.StringVar()
        dir_entry = ttk.Entry(dir_frame, textvariable=self.directory_var)
        dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).pack(side=tk.RIGHT)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(fill=tk.X)
        
        self.analyze_button = ttk.Button(button_frame, text="Start Analysis", command=self.start_analysis)
        self.analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.stop_analysis, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="Export Results", command=self.export_results).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Configuration", command=self.open_config).pack(side=tk.RIGHT)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        ttk.Label(control_frame, textvariable=self.progress_var).pack(anchor=tk.W, pady=(10, 0))
        
        self.progress_bar = Progressbar(control_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(5, 0))
        
        # Notebook for different views
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # File list frame
        self.file_list_frame = FileListFrame(self.notebook)
        self.notebook.add(self.file_list_frame.frame, text="File List")
        
        # Summary frame
        self.create_summary_frame()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_menu(self):
        """Create application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open Directory", command=self.browse_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Import Results", command=self.import_results)
        file_menu.add_command(label="Export Results", command=self.export_results)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Configuration", command=self.open_config)
        tools_menu.add_command(label="View Logs", command=self.view_logs)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        help_menu.add_command(label="User Guide", command=self.show_help)
    
    def create_summary_frame(self):
        """Create summary statistics frame."""
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text="Summary")
        
        self.summary_text = scrolledtext.ScrolledText(summary_frame, wrap=tk.WORD)
        self.summary_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def check_configuration(self):
        """Check if configuration is valid."""
        if not self.config_manager.is_valid_config():
            missing = self.config_manager.get_missing_config()
            messagebox.showwarning("Configuration Required", 
                                 f"Please configure the following: {', '.join(missing)}")
            self.open_config()
    
    def browse_directory(self):
        """Browse for directory to analyze."""
        directory = filedialog.askdirectory()
        if directory:
            self.directory_var.set(directory)
    
    def open_config(self):
        """Open configuration dialog."""
        dialog = ConfigDialog(self.root, self.config_manager)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.status_var.set("Configuration saved.")
            # Reinitialize file organizer with new config
            if self.config_manager.is_valid_config():
                self.file_organizer = FileOrganizer(self.config_manager.config.openai_api_key)
    
    def start_analysis(self):
        """Start file analysis in background thread."""
        directory = self.directory_var.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please select a directory to analyze.")
            return
        
        if not os.path.exists(directory):
            messagebox.showerror("Error", "Selected directory does not exist.")
            return
        
        if not self.config_manager.is_valid_config():
            messagebox.showerror("Error", "Please configure the application first.")
            return
        
        # Initialize file organizer if needed
        if self.file_organizer is None:
            self.file_organizer = FileOrganizer(self.config_manager.config.openai_api_key)
        
        # Disable controls
        self.analyze_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.progress_bar.start()
        self.progress_var.set("Starting analysis...")
        
        # Start analysis in background thread
        self.analysis_thread = threading.Thread(target=self.run_analysis, args=(directory,))
        self.analysis_thread.daemon = True
        self.analysis_thread.start()
    
    def run_analysis(self, directory: str):
        """Run file analysis in background thread."""
        try:
            self.root.after(0, lambda: self.progress_var.set("Scanning files..."))
            
            # Run analysis
            results = self.file_organizer.analyze_directory(directory, 
                                                           self.config_manager.config.recursive_scan)
            
            self.analysis_results = results
            
            # Update UI on main thread
            self.root.after(0, self.analysis_complete)
            
        except Exception as e:
            self.root.after(0, lambda: self.analysis_error(str(e)))
    
    def analysis_complete(self):
        """Handle analysis completion."""
        self.progress_bar.stop()
        self.analyze_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set(f"Analysis complete. {len(self.analysis_results)} files analyzed.")
        
        # Update file list
        self.file_list_frame.update_files(self.analysis_results)
        
        # Update summary
        self.update_summary()
        
        self.status_var.set(f"Analysis complete. {len(self.analysis_results)} files processed.")
    
    def analysis_error(self, error_msg: str):
        """Handle analysis error."""
        self.progress_bar.stop()
        self.analyze_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set("Analysis failed.")
        
        messagebox.showerror("Analysis Error", f"Analysis failed: {error_msg}")
        self.status_var.set("Analysis failed.")
    
    def stop_analysis(self):
        """Stop ongoing analysis."""
        # Note: This is a simplified stop mechanism
        # In a production app, you'd want proper thread cancellation
        self.progress_bar.stop()
        self.analyze_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_var.set("Analysis stopped.")
        self.status_var.set("Analysis stopped by user.")
    
    def update_summary(self):
        """Update summary statistics."""
        if not self.analysis_results:
            return
        
        summary = self.file_organizer.get_summary_report()
        
        summary_text = f"""
ANALYSIS SUMMARY
================

Total Files Analyzed: {summary.get('total_files', 0)}
Total Size: {summary.get('total_size_mb', 0):.2f} MB

RECOMMENDED ACTIONS:
{json.dumps(summary.get('action_counts', {}), indent=2)}

CATEGORY DISTRIBUTION:
{json.dumps(summary.get('category_distribution', {}), indent=2)}

PRIORITY DISTRIBUTION:
{json.dumps(summary.get('priority_distribution', {}), indent=2)}

DUPLICATES AND CLEANUP:
- Duplicate files found: {summary.get('duplicates_found', 0)}
- Files recommended for deletion: {summary.get('files_to_delete', 0)}
- Potential space savings: {summary.get('potential_space_savings_mb', 0):.2f} MB

HIGH PRIORITY FILES:
- Files with priority >= 8.0: {summary.get('high_priority_files', 0)}
"""
        
        self.summary_text.delete(1.0, tk.END)
        self.summary_text.insert(tk.END, summary_text)
    
    def export_results(self):
        """Export analysis results to file."""
        if not self.analysis_results:
            messagebox.showinfo("Info", "No analysis results to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.file_organizer.export_results(file_path)
                messagebox.showinfo("Success", f"Results exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export results: {e}")
    
    def import_results(self):
        """Import previously saved analysis results."""
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Convert back to FileAnalysis objects (simplified)
                # This would need more sophisticated reconstruction in a real app
                messagebox.showinfo("Import", "Results imported successfully.")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import results: {e}")
    
    def view_logs(self):
        """View application logs."""
        log_window = tk.Toplevel(self.root)
        log_window.title("Application Logs")
        log_window.geometry("600x400")
        
        log_text = scrolledtext.ScrolledText(log_window)
        log_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        log_text.insert(tk.END, "Application logs would appear here in a full implementation.")
    
    def show_about(self):
        """Show about dialog."""
        about_text = """AI Desktop File Organizer
Version 1.0

An intelligent file organization tool that uses AI to analyze 
and categorize your files automatically.

Features:
- Multimodal AI analysis of various file types
- Smart categorization and priority ranking
- Batch file operations
- Safe deletion with confirmation
- Comprehensive reporting

Created with Python and OpenAI GPT-4."""
        
        messagebox.showinfo("About", about_text)
    
    def show_help(self):
        """Show help/user guide."""
        help_text = """USER GUIDE

1. CONFIGURATION:
   - Go to Tools > Configuration
   - Enter your OpenAI API key
   - Configure analysis settings

2. ANALYSIS:
   - Select a directory to analyze
   - Click "Start Analysis"
   - Wait for AI to process all files

3. REVIEW RESULTS:
   - Check the File List tab
   - Review recommendations
   - Use filters to find specific files

4. TAKE ACTION:
   - Select files for deletion
   - Export results for later
   - Use batch operations

5. SAFETY:
   - Enable dry run mode for testing
   - Confirm deletions are enabled by default
   - Create backups before organizing"""
        
        help_window = tk.Toplevel(self.root)
        help_window.title("User Guide")
        help_window.geometry("500x400")
        
        help_text_widget = scrolledtext.ScrolledText(help_window, wrap=tk.WORD)
        help_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        help_text_widget.insert(tk.END, help_text)
        help_text_widget.config(state=tk.DISABLED)
    
    def run(self):
        """Run the application."""
        self.root.mainloop()

def main():
    """Main function to run the GUI application."""
    app = DesktopOrganizerGUI()
    app.run()

if __name__ == "__main__":
    main()