#!/usr/bin/env python3
"""
File Search Tkinter Application

A simple, modern-looking Tkinter desktop app to browse files returned by an 
external script based on a query, view file contents, and search within content using regex.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import subprocess
import threading
import os
import re
import shutil
from pathlib import Path
from typing import Optional, List, Tuple
from enum import Enum

# Configuration
DEBUG = False  # Set to True to see debug logs (DEBUG, INFO, ERROR). False shows INFO and ERROR only.


class LogLevel(Enum):
    """Log levels for the application."""
    DEBUG = 0
    INFO = 1
    ERROR = 2


class FileSearchApp:
    """Main application class for the File Search Tkinter app."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Log Search")
        self.root.geometry("1200x800")
        
        # Application state
        default_folder = Path.home() / '.help_log_search'
        self.current_folder: Optional[Path] = default_folder if default_folder.exists() else None
        self.current_file: Optional[Path] = None
        self.current_query: str = ""
        self.file_count: int = 0
        self.quick_query: bool = False  # Quick query mode (-m flag)
        self.filename_aliases: dict = {}  # Maps alias -> actual filename
        self.alias_to_path: dict = {}  # Maps alias -> full path
        self.search_matches: List[Tuple[str, str]] = []  # (start, end) indices
        self.current_match_index: int = -1
        self.find_overridden: bool = False  # True if user changed the Find input after a fetch
        self._programmatic_search_set: bool = False  # Internal flag to ignore programmatic Find updates
        
        # Configure dark theme
        self._configure_theme()
        
        # Create UI components
        self._create_widgets()
        
        # Configure layout
        self._configure_layout()
        
        # Bind events
        self._bind_events()
        
        # Initialize default folder display if it exists
        if self.current_folder and self.current_folder.exists():
            self._load_default_folder()
        
        # Initialize application
        print("[INFO] Log Search application started")

    def _configure_theme(self):
        """Configure the dark theme for the application."""
        # Define color scheme
        self.colors = {
            'bg_dark': '#1e1e1e',           # Main background
            'bg_light': '#1e1e1e',          # Panel backgrounds
            'fg_primary': '#e0e0e0',        # Primary text
            'fg_secondary': '#b0b0b0',      # Secondary text
            'accent': '#0d7377',            # Accent color
            'accent_hover': '#14a4aa',      # Accent hover color
            'button_bg': '#3c3c3c',         # Button background
            'button_fg': '#e0e0e0',         # Button text
            'entry_bg': '#3c3c3c',          # Entry background
            'entry_fg': '#e0e0e0',          # Entry text
            'highlight_all': '#4fc3f7',     # All matches highlight (light blue)
            'highlight_current': '#ff8a65', # Current match highlight (vivid orange)
            'scrollbar_thumb': '#505050',   # Scrollbar thumb - more visible
            'scrollbar_track': '#2a2a2a',   # Scrollbar track - darker
            'footer': '#555555'             # Footer text
        }
        
        self.root.configure(bg=self.colors['bg_dark'])
        self._configure_ttk_styles()

    def _configure_ttk_styles(self):
        """Configure TTK widget styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Frame styles
        self.style.configure('Dark.TFrame', background=self.colors['bg_dark'])
        self.style.configure('Panel.TFrame', background=self.colors['bg_light'])
        
        # Label styles
        self.style.configure('Dark.TLabel', 
                           background=self.colors['bg_dark'], 
                           foreground=self.colors['fg_primary'])
        self.style.configure('Footer.TLabel',
                           background=self.colors['bg_dark'],
                           foreground=self.colors['footer'],
                           font=('Liberation Mono', 9))
        
        # Button styles
        self.style.configure('Dark.TButton',
                           background=self.colors['button_bg'],
                           foreground=self.colors['button_fg'],
                           borderwidth=1,
                           relief='flat',
                           padding=(12, 8))
        self.style.map('Dark.TButton',
                      background=[('active', self.colors['accent_hover']),
                                ('pressed', self.colors['accent'])],
                      foreground=[('active', 'white')])
        
        # PanedWindow styles
        self.style.configure('Dark.TPanedwindow', background=self.colors['bg_dark'])
        self.style.configure('Dark.TPanedwindow.Sash', 
                           background=self.colors['bg_light'],
                           sashthickness=6)

    def _create_scrollbar(self, parent, orient=tk.VERTICAL):
        """Create a styled scrollbar."""
        return tk.Scrollbar(parent,
                          orient=orient,
                          bg=self.colors['scrollbar_track'],
                          troughcolor=self.colors['scrollbar_track'],
                          activebackground=self.colors['accent'],
                          highlightbackground=self.colors['scrollbar_track'],
                          width=16,
                          relief='flat',
                          borderwidth=1,
                          elementborderwidth=1)

    def _create_text_entry(self, parent, textvariable=None):
        """Create a styled text entry."""
        return tk.Entry(parent,
                       textvariable=textvariable,
                       bg=self.colors['entry_bg'],
                       fg=self.colors['entry_fg'],
                       insertbackground=self.colors['fg_primary'],
                       relief='solid',
                       borderwidth=1,
                       font=('Liberation Mono', 11),
                       highlightthickness=1,
                       highlightcolor=self.colors['accent'])

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        self.main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        
        # Top frame for query input
        self.top_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        
        # Query entry with placeholder
        self.query_var = tk.StringVar()
        self.query_entry = self._create_text_entry(self.top_frame, self.query_var)
        self.query_entry.config(font=('Liberation Mono', 11))
        # Set placeholder text
        self._set_placeholder(self.query_entry, "Enter search term for logs...")
        
        # Quick query checkbox
        self.quick_query_var = tk.BooleanVar(value=True)  # Checked by default
        self.quick_query_checkbox = tk.Checkbutton(self.top_frame,
                                               text="Quick",
                                               variable=self.quick_query_var,
                                               bg=self.colors['bg_dark'],
                                               fg=self.colors['fg_primary'],
                                               selectcolor=self.colors['entry_bg'],
                                               activebackground=self.colors['bg_dark'],
                                               activeforeground=self.colors['fg_primary'],
                                               font=('Liberation Mono', 10))
        
        # Fetch button
        self.fetch_button = ttk.Button(self.top_frame, 
                                     text="Fetch", 
                                     command=self._on_fetch_click,
                                     style='Dark.TButton')
        
        # Middle frame with resizable panels
        self.middle_frame = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL, style='Dark.TPanedwindow')
        
        # Left panel for files list
        self.left_panel = ttk.Frame(self.middle_frame, style='Panel.TFrame')
        
        # Files listbox with scrollbar
        self.files_frame = tk.Frame(self.left_panel, bg=self.colors['bg_light'], relief='sunken', bd=1)
        self.files_listbox = tk.Listbox(self.files_frame,
                                       bg=self.colors['bg_light'],
                                       fg=self.colors['fg_primary'],
                                       selectbackground=self.colors['accent'],
                                       selectforeground='white',
                                       relief='flat',
                                       borderwidth=0,
                                       activestyle='none',
                                       font=('Liberation Mono', 10))
        
        self.files_scrollbar = self._create_scrollbar(self.files_frame)
        
        # Right panel for content
        self.right_panel = ttk.Frame(self.middle_frame, style='Panel.TFrame')
        
        # Search frame
        self.search_frame = ttk.Frame(self.right_panel, style='Dark.TFrame')
        #self.search_label = ttk.Label(self.search_frame, text="Find:", style='Dark.TLabel')
        self.search_var = tk.StringVar()
        self.search_entry = self._create_text_entry(self.search_frame, self.search_var)
        
        self.prev_button = ttk.Button(self.search_frame,
                                    text="Prev",
                                    command=self._on_prev_match,
                                    style='Dark.TButton')
        
        self.next_button = ttk.Button(self.search_frame,
                                    text="Next", 
                                    command=self._on_next_match,
                                    style='Dark.TButton')
        
        # Content text widget
        self.content_frame = tk.Frame(self.right_panel, bg=self.colors['bg_light'], relief='sunken', bd=1)
        self.content_text = tk.Text(self.content_frame,
                                  bg=self.colors['bg_light'],
                                  fg=self.colors['fg_primary'],
                                  insertbackground=self.colors['fg_primary'],
                                  relief='flat',
                                  borderwidth=0,
                                  wrap=tk.WORD,
                                  state=tk.DISABLED,
                                  font=('Liberation Mono', 10, 'bold'),
                                  spacing1=2,
                                  spacing3=2)
        
        self.content_scrollbar_v = self._create_scrollbar(self.content_frame)
        self.content_scrollbar_h = self._create_scrollbar(self.content_frame, tk.HORIZONTAL)
        

        
        # Footer
        self.footer_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        self.footer_info_label = ttk.Label(self.footer_frame, 
                                         text="", 
                                         style='Footer.TLabel')
        self.footer_label = ttk.Label(self.footer_frame, 
                                    text="by Mateo Velez", 
                                    style='Footer.TLabel')
        
        # Configure text tags for highlighting
        self.content_text.tag_configure('highlight_all', background=self.colors['highlight_all'], foreground='black')
        self.content_text.tag_configure('highlight_current', background=self.colors['highlight_current'], foreground='black')

    def _configure_layout(self):
        """Configure the layout of all widgets."""
        # Main layout with better padding
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Top frame layout with improved spacing
        self.top_frame.pack(fill=tk.X, pady=(0, 15))
        self.query_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=4)
        self.quick_query_checkbox.pack(side=tk.LEFT, padx=(0, 10))
        self.fetch_button.pack(side=tk.LEFT)
        
        # Middle frame layout - using PanedWindow with better spacing
        self.middle_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Add panels to PanedWindow (using basic add without minsize for compatibility)
        self.middle_frame.add(self.left_panel)
        self.middle_frame.add(self.right_panel)
        

        self.files_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Files listbox and scrollbar
        self.files_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.files_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.files_listbox.config(yscrollcommand=self.files_scrollbar.set)
        self.files_scrollbar.config(command=self.files_listbox.yview)
        
        # Configure left panel size
        self.left_panel.configure(width=300)
        self.left_panel.pack_propagate(False)
        
        # Search frame layout with better spacing
        self.search_frame.pack(fill=tk.X, pady=(0, 8), padx=5)
        #self.search_label.pack(side=tk.LEFT, padx=(0, 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), ipady=4)
        self.prev_button.pack(side=tk.LEFT, padx=(0, 5))
        self.next_button.pack(side=tk.LEFT)
        
        # Content frame layout with padding
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5)
        self.content_text.grid(row=0, column=0, sticky='nsew')
        self.content_scrollbar_v.grid(row=0, column=1, sticky='ns')
        self.content_scrollbar_h.grid(row=1, column=0, sticky='ew')
        
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)
        
        # Configure scrollbars
        self.content_text.config(yscrollcommand=self.content_scrollbar_v.set,
                               xscrollcommand=self.content_scrollbar_h.set)
        self.content_scrollbar_v.config(command=self.content_text.yview)
        self.content_scrollbar_h.config(command=self.content_text.xview)
        

        
        # Footer layout
        self.footer_frame.pack(fill=tk.X)
        self.footer_info_label.pack(side=tk.LEFT, anchor=tk.W)
        self.footer_label.pack(anchor=tk.E)

    def _bind_events(self):
        """Bind event handlers."""
        # Enter key in query entry triggers fetch
        self.query_entry.bind('<Return>', lambda e: self._on_fetch_click())
        
        # Files listbox selection
        self.files_listbox.bind('<<ListboxSelect>>', self._on_file_select)
        
        # Search entry changes trigger search
        self.search_var.trace('w', self._on_search_change)
        
        # Enter key in search entry goes to next match
        self.search_entry.bind('<Return>', lambda e: self._on_next_match())

    def _log_message(self, message: str, level: LogLevel = LogLevel.INFO):
        """Print log messages to stdout based on level and DEBUG setting."""
        # Determine if we should show this log message
        should_show = False
        
        if DEBUG:
            # Show all levels when DEBUG is True
            should_show = True
        else:
            # Show only INFO and ERROR when DEBUG is False
            should_show = level in (LogLevel.INFO, LogLevel.ERROR)
        
        if should_show:
            # Add level prefix for clarity
            level_prefix = {
                LogLevel.DEBUG: "[DEBUG]",
                LogLevel.INFO: "[INFO]",
                LogLevel.ERROR: "[ERROR]"
            }
            
            formatted_message = f"{level_prefix[level]} {message}"
            print(formatted_message)

    def _on_fetch_click(self):
        """Handle fetch button click."""
        query = self.query_var.get().strip()
        
        # Check if query is empty or placeholder text
        if not query or query == "Enter search term for logs...":
            self.query_entry.focus()
            return
            
        if len(query) < 2:
            self.query_entry.focus()
            return
        
        self.current_query = query
        self.quick_query = self.quick_query_var.get()
        
        mode_text = " (quick mode)" if self.quick_query else ""
        self._log_message(f"Starting search for files containing: '{query}'{mode_text}", LogLevel.INFO)
        
        # Show progress feedback
        self.root.config(cursor="watch")
        self.fetch_button.config(state=tk.DISABLED, text="Searching...")
        
        # Clear previous results
        self.files_listbox.delete(0, tk.END)
        self.filename_aliases.clear()
        self.alias_to_path.clear()
        self.content_text.config(state=tk.NORMAL)
        self.content_text.delete(1.0, tk.END)
        self.content_text.config(state=tk.DISABLED)
        self.file_count = 0
        self._update_footer_info()
        
        # Run fetch in background thread
        thread = threading.Thread(target=self._fetch_files_thread, args=(query,))
        thread.daemon = True
        thread.start()

    def _fetch_files_thread(self, query: str):
        """Fetch files in background thread."""
        try:
            # Find fetch_logs command in PATH
            fetch_logs_cmd = shutil.which('fetch_logs')
            if not fetch_logs_cmd:
                self.root.after(0, self._fetch_error, "fetch_logs command not found in PATH")
                return
            
            self._log_message(f"Using fetch_logs command: {fetch_logs_cmd}", LogLevel.DEBUG)
            
            # Build command with optional -m flag for quick query
            cmd = [fetch_logs_cmd]
            if self.quick_query:
                cmd.append('-m')
            cmd.append(query)
            
            # Call the external fetch_logs script
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=30)
            
            if result.returncode != 0:
                error_msg = f"fetch_logs failed with exit code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr.strip()}"
                self._log_message(f"Command stderr: {result.stderr.strip()}", LogLevel.DEBUG)
                self.root.after(0, self._fetch_error, error_msg)
                return
            
            folder_path = result.stdout.strip()
            self._log_message(f"fetch_logs returned path: {folder_path}", LogLevel.DEBUG)
            
            if not folder_path:
                self.root.after(0, self._fetch_error, "fetch_logs returned empty output")
                return
            
            folder = Path(folder_path)
            if not folder.exists():
                self.root.after(0, self._fetch_error, f"Folder does not exist: {folder_path}")
                return
            
            if not folder.is_dir():
                self.root.after(0, self._fetch_error, f"Path is not a directory: {folder_path}")
                return
            
            # Get list of regular files
            try:
                files = [f for f in folder.iterdir() if f.is_file()]
                # Sort by modification time (most recent first)
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                self._log_message(f"Found {len(files)} files in {folder}", LogLevel.DEBUG)
                self.root.after(0, self._fetch_success, folder, files)
                
            except Exception as e:
                self.root.after(0, self._fetch_error, f"Error reading folder: {str(e)}")
                
        except subprocess.TimeoutExpired:
            self.root.after(0, self._fetch_error, "fetch_logs timed out")
        except Exception as e:
            self.root.after(0, self._fetch_error, f"Error running fetch_logs: {str(e)}")

    def _fetch_success(self, folder: Path, files: List[Path]):
        """Handle successful fetch."""
        self.current_folder = folder
        
        # Clear previous mappings
        self.filename_aliases.clear()
        self.alias_to_path.clear()
        
        # Update files list with aliases
        self.files_listbox.delete(0, tk.END)
        for file in files:
            alias = self.alias_filename(file.name)
            self.filename_aliases[alias] = file.name
            self.alias_to_path[alias] = file
            self.files_listbox.insert(tk.END, alias)
        
        # Update file count
        self.file_count = len(files)
        self._update_footer_info()
        
        # Update search to current query and reset override for a new fetch
        self.find_overridden = False
        self._programmatic_search_set = True
        self.search_var.set(self.current_query)
        
        # If there's already content loaded, trigger search with new query
        if self.current_file and self.content_text.get(1.0, tk.END).strip():
            self._perform_search()
        
        # Reset UI state
        self.root.config(cursor="")
        self.fetch_button.config(state=tk.NORMAL, text="Fetch")
        
        # Provide user feedback in logs only
        if files:
            self._log_message(f"Found {len(files)} files containing '{self.current_query}'", LogLevel.INFO)
        else:
            self._log_message(f"No files found containing '{self.current_query}'", LogLevel.INFO)

    def _fetch_error(self, error_msg: str):
        """Handle fetch error."""
        self._log_message(f"Search failed: {error_msg}", LogLevel.ERROR)
        
        # Show user-friendly error message
        if "not found in PATH" in error_msg:
            messagebox.showerror("Configuration Error", 
                               "The fetch_logs command was not found.\n"
                               "Please ensure it's installed and available in your PATH.")
        elif "timed out" in error_msg:
            messagebox.showerror("Search Timeout", 
                               "The search operation timed out.\n"
                               "Try a more specific search term or check your system load.")
        else:
            messagebox.showerror("Search Error", 
                               f"An error occurred while searching for files:\n\n{error_msg}")
        
        # Reset UI state
        self.root.config(cursor="")
        self.fetch_button.config(state=tk.NORMAL, text="Fetch")

    def _on_file_select(self, event):
        """Handle file selection in the listbox."""
        selection = self.files_listbox.curselection()
        if not selection or not self.current_folder:
            return
        
        alias = self.files_listbox.get(selection[0])
        
        # Get the actual file path from the alias
        if alias in self.alias_to_path:
            file_path = self.alias_to_path[alias]
            actual_filename = self.filename_aliases[alias]
        else:
            # Fallback: treat as actual filename (for backward compatibility)
            actual_filename = alias
            file_path = self.current_folder / alias
        
        self._log_message(f"Opening {actual_filename}", LogLevel.INFO)
        
        try:
            # Check file size before reading
            file_size = file_path.stat().st_size
            if file_size > 10 * 1024 * 1024:  # 10MB limit
                if not messagebox.askyesno("Large File Warning", 
                                         f"The file '{filename}' is {file_size // 1024 // 1024}MB.\n"
                                         f"This may take a while to load. Continue?"):
                    return
            
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            
            content = content.replace('\x00', '')
            self.current_file = file_path
            
            # Update content display
            self.content_text.config(state=tk.NORMAL)
            self.content_text.delete(1.0, tk.END)
            self.content_text.insert(1.0, content)
            self.content_text.config(state=tk.DISABLED)
            
            # Keep user's Find query if they modified it; otherwise default to current query
            if not self.find_overridden:
                self._programmatic_search_set = True
                self.search_var.set(self.current_query)
            
            # Trigger search to highlight matches
            self._perform_search()
            
            self._log_message(f"Successfully loaded {actual_filename} ({len(content)} characters)", LogLevel.INFO)
            
        except PermissionError:
            error_msg = f"Permission denied reading {actual_filename}"
            self._log_message(error_msg, LogLevel.ERROR)
            messagebox.showerror("Permission Error", 
                               f"Cannot read file '{actual_filename}'.\n"
                               f"You don't have permission to access this file.")
        except UnicodeDecodeError:
            error_msg = f"File '{actual_filename}' contains binary data or unsupported encoding"
            self._log_message(error_msg, LogLevel.ERROR)
            messagebox.showerror("File Format Error", 
                               f"Cannot display file '{actual_filename}'.\n"
                               f"This appears to be a binary file or uses an unsupported text encoding.")
        except Exception as e:
            error_msg = f"Error reading file {actual_filename}: {str(e)}"
            self._log_message(error_msg, LogLevel.ERROR)
            messagebox.showerror("File Error", 
                               f"An unexpected error occurred while reading '{actual_filename}':\n\n{str(e)}")

    def _on_search_change(self, *args):
        """Handle search text change."""
        # If change was programmatic, do not mark as user override
        if self._programmatic_search_set:
            self._programmatic_search_set = False
        else:
            self.find_overridden = True
        self._perform_search()

    def _perform_search(self):
        """Perform search and highlight matches."""
        search_text = self.search_var.get()
        if not search_text:
            # Clear all highlights
            self.content_text.tag_remove('highlight_all', 1.0, tk.END)
            self.content_text.tag_remove('highlight_current', 1.0, tk.END)
            self.search_matches = []
            self.current_match_index = -1
            return
        
        try:
            # Compile regex pattern (case-insensitive)
            pattern = re.compile(search_text, re.IGNORECASE)
        except re.error as e:
            self._log_message(f"Invalid regex pattern: {str(e)}", LogLevel.ERROR)
            return
        
        # Get content from text widget
        content = self.content_text.get(1.0, tk.END)
        
        # Clear previous highlights
        self.content_text.tag_remove('highlight_all', 1.0, tk.END)
        self.content_text.tag_remove('highlight_current', 1.0, tk.END)
        
        # Find all matches
        self.search_matches = []
        for match in pattern.finditer(content):
            start_idx = f"1.0+{match.start()}c"
            end_idx = f"1.0+{match.end()}c"
            self.search_matches.append((start_idx, end_idx))
            
            # Highlight all matches
            self.content_text.tag_add('highlight_all', start_idx, end_idx)
        
        # Reset current match index
        self.current_match_index = -1
        
        # Go to first match if any
        if self.search_matches:
            self._log_message(f"Found {len(self.search_matches)} matches for pattern: {search_text}", LogLevel.DEBUG)
            self._highlight_current_match(0)
        else:
            self._log_message(f"No matches found for pattern: {search_text}", LogLevel.DEBUG)

    def _highlight_current_match(self, index: int):
        """Highlight the current match and scroll to it."""
        if not self.search_matches or index < 0 or index >= len(self.search_matches):
            return
        
        # Remove previous current highlight
        self.content_text.tag_remove('highlight_current', 1.0, tk.END)
        
        # Add current highlight
        start_idx, end_idx = self.search_matches[index]
        self.content_text.tag_add('highlight_current', start_idx, end_idx)
        
        # Scroll to match
        self.content_text.see(start_idx)
        
        self.current_match_index = index

    def _on_prev_match(self):
        """Navigate to previous search match."""
        if not self.search_matches:
            return
        
        if self.current_match_index <= 0:
            # Wrap to last match
            new_index = len(self.search_matches) - 1
        else:
            new_index = self.current_match_index - 1
        
        self._highlight_current_match(new_index)

    def _on_next_match(self):
        """Navigate to next search match."""
        if not self.search_matches:
            return
        
        if self.current_match_index >= len(self.search_matches) - 1:
            # Wrap to first match
            new_index = 0
        else:
            new_index = self.current_match_index + 1
        
        self._highlight_current_match(new_index)
    
    def _update_footer_info(self):
        """Update the footer info display with folder and count info."""
        if self.current_folder and self.file_count > 0:
            # Get first 12 characters of folder name
            folder_name = self.current_folder.name
            folder_display = folder_name[:12] + "..." if len(folder_name) > 12 else folder_name
            info_text = f"Found {self.file_count}, At {folder_display}"
            self.footer_info_label.config(text=info_text)
        else:
            self.footer_info_label.config(text="")
    
    def alias_filename(self, filename: str) -> str:
        """Create an alias for a filename. Override this function to customize aliasing."""
        # Default implementation: use first 30 chars + extension
        name, ext = os.path.splitext(filename)
        if len(name) > 30:
            return f"{name[:30]}...{ext}"
        return filename
    
    def _set_placeholder(self, entry_widget, placeholder_text):
        """Set placeholder text for an entry widget."""
        entry_widget.placeholder = placeholder_text
        entry_widget.placeholder_color = self.colors['fg_secondary']
        entry_widget.default_color = self.colors['entry_fg']
        
        def on_focus_in(event):
            if entry_widget.get() == placeholder_text:
                entry_widget.delete(0, tk.END)
                entry_widget.config(fg=entry_widget.default_color)
        
        def on_focus_out(event):
            if not entry_widget.get():
                entry_widget.insert(0, placeholder_text)
                entry_widget.config(fg=entry_widget.placeholder_color)
        
        # Set initial placeholder
        entry_widget.insert(0, placeholder_text)
        entry_widget.config(fg=entry_widget.placeholder_color)
        
        # Bind events
        entry_widget.bind('<FocusIn>', on_focus_in)
        entry_widget.bind('<FocusOut>', on_focus_out)
    
    def clear_cached_logs(self):
        """Clear cached logs function - placeholder for external calls."""
        # This function exists for external compatibility but does nothing
        # since we removed the clear cache button functionality
        pass
    
    def _load_default_folder(self):
        """Load files from the default folder."""
        try:
            if self.current_folder and self.current_folder.is_dir():
                files = [f for f in self.current_folder.iterdir() if f.is_file()]
                files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                self.file_count = len(files)
                
                # Clear previous mappings
                self.filename_aliases.clear()
                self.alias_to_path.clear()
                
                # Update files list with aliases
                self.files_listbox.delete(0, tk.END)
                for file in files:
                    alias = self.alias_filename(file.name)
                    self.filename_aliases[alias] = file.name
                    self.alias_to_path[alias] = file
                    self.files_listbox.insert(tk.END, alias)
                
                self._update_footer_info()
                
                if files:
                    self._log_message(f"Loaded {len(files)} files from default folder: {self.current_folder.name}", LogLevel.INFO)
        except Exception as e:
            self._log_message(f"Error loading default folder: {str(e)}", LogLevel.ERROR)


def main():
    """Main entry point for the application."""
    # To enable debug logging, change DEBUG = True at the top of this file
    root = tk.Tk()
    app = FileSearchApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()