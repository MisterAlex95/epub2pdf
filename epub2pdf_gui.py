#!/usr/bin/env python3
"""
epub2pdf GUI - Graphical User Interface for epub2pdf
A simple and intuitive interface for converting EPUB files to PDF
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import threading
import os
import sys
from pathlib import Path

class Epub2PdfGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("epub2pdf - EPUB to PDF Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.recursive = tk.BooleanVar()
        self.force = tk.BooleanVar()
        self.grayscale = tk.BooleanVar()
        self.resize_var = tk.StringVar()
        self.zip_output = tk.BooleanVar()
        self.clean_tmp = tk.BooleanVar(value=True)
        self.open_output = tk.BooleanVar()
        self.verbose = tk.BooleanVar()
        
        # Create main frame
        self.create_widgets()
        
        # Set default output directory
        self.output_dir.set("./pdfs")
        
    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="📘 epub2pdf - EPUB to PDF Converter", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Input directory
        ttk.Label(main_frame, text="Input Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        input_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(input_frame, textvariable=self.input_dir, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(input_frame, text="Browse", command=self.browse_input).grid(row=0, column=1, padx=(5, 0))
        
        # Output directory
        ttk.Label(main_frame, text="Output Directory:").grid(row=2, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(output_frame, textvariable=self.output_dir, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Button(output_frame, text="Browse", command=self.browse_output).grid(row=0, column=1, padx=(5, 0))
        
        # Options frame
        options_frame = ttk.LabelFrame(main_frame, text="Options", padding="10")
        options_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        options_frame.columnconfigure(1, weight=1)
        
        # Left column
        ttk.Checkbutton(options_frame, text="Search subdirectories", variable=self.recursive).grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Overwrite existing files", variable=self.force).grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Grayscale conversion", variable=self.grayscale).grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Create ZIP archive", variable=self.zip_output).grid(row=3, column=0, sticky=tk.W, pady=2)
        
        # Right column
        ttk.Checkbutton(options_frame, text="Clean temporary files", variable=self.clean_tmp).grid(row=0, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Open output directory", variable=self.open_output).grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Checkbutton(options_frame, text="Verbose mode", variable=self.verbose).grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Resize option
        ttk.Label(options_frame, text="Resize images:").grid(row=3, column=1, sticky=tk.W, pady=2)
        resize_combo = ttk.Combobox(options_frame, textvariable=self.resize_var, 
                                   values=["", "A4", "A3", "A5", "HD", "FHD", "Custom"],
                                   state="readonly", width=15)
        resize_combo.grid(row=4, column=1, sticky=tk.W, pady=2)
        resize_combo.bind("<<ComboboxSelected>>", self.on_resize_change)
        
        # Custom resize entry
        self.custom_resize_var = tk.StringVar()
        self.custom_resize_entry = ttk.Entry(options_frame, textvariable=self.custom_resize_var, width=15)
        self.custom_resize_entry.grid(row=5, column=1, sticky=tk.W, pady=2)
        self.custom_resize_entry.grid_remove()  # Hidden by default
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=4, column=0, columnspan=3, pady=20)
        
        ttk.Button(buttons_frame, text="Convert", command=self.start_conversion, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Dry Run", command=self.dry_run).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Clear Log", command=self.clear_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(buttons_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
    def browse_input(self):
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_dir.set(directory)
            
    def browse_output(self):
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir.set(directory)
            
    def on_resize_change(self, event):
        if self.resize_var.get() == "Custom":
            self.custom_resize_entry.grid()
        else:
            self.custom_resize_entry.grid_remove()
            
    def get_resize_option(self):
        resize = self.resize_var.get()
        if resize == "Custom":
            return self.custom_resize_var.get()
        elif resize:
            return resize
        return ""
        
    def build_command(self, dry_run=False):
        cmd = ["./epub2pdf.sh"]
        
        if self.input_dir.get():
            cmd.extend(["--input-dir", self.input_dir.get()])
            
        if self.output_dir.get():
            cmd.extend(["--output-dir", self.output_dir.get()])
            
        if self.recursive.get():
            cmd.append("--recursive")
            
        if self.force.get():
            cmd.append("--force")
            
        if self.grayscale.get():
            cmd.append("--grayscale")
            
        resize = self.get_resize_option()
        if resize:
            cmd.extend(["--resize", resize])
            
        if self.zip_output.get():
            cmd.append("--zip-output")
            
        if self.clean_tmp.get():
            cmd.append("--clean-tmp")
            
        if self.open_output.get():
            cmd.append("--open-output-dir")
            
        if self.verbose.get():
            cmd.append("--verbose")
            
        if dry_run:
            cmd.append("--dry-run")
            
        return cmd
        
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def clear_log(self):
        self.log_text.delete(1.0, tk.END)
        
    def dry_run(self):
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory")
            return
            
        cmd = self.build_command(dry_run=True)
        self.log_message(f"Running dry run: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=os.getcwd())
            if result.stdout:
                self.log_message(result.stdout)
            if result.stderr:
                self.log_message("STDERR: " + result.stderr)
        except Exception as e:
            self.log_message(f"Error: {e}")
            
    def start_conversion(self):
        if not self.input_dir.get():
            messagebox.showerror("Error", "Please select an input directory")
            return
            
        if not self.output_dir.get():
            messagebox.showerror("Error", "Please select an output directory")
            return
            
        # Start conversion in a separate thread
        self.progress.start()
        self.status_var.set("Converting...")
        
        thread = threading.Thread(target=self.run_conversion)
        thread.daemon = True
        thread.start()
        
    def run_conversion(self):
        cmd = self.build_command()
        self.log_message(f"Starting conversion: {' '.join(cmd)}")
        
        try:
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                     text=True, bufsize=1, universal_newlines=True, cwd=os.getcwd())
            
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log_message(line.rstrip())
                    
            process.stdout.close()
            return_code = process.wait()
            
            if return_code == 0:
                self.log_message("✅ Conversion completed successfully!")
                self.status_var.set("Conversion completed")
                messagebox.showinfo("Success", "Conversion completed successfully!")
            else:
                self.log_message(f"❌ Conversion failed with return code: {return_code}")
                self.status_var.set("Conversion failed")
                messagebox.showerror("Error", "Conversion failed. Check the log for details.")
                
        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {e}")
            
        finally:
            self.progress.stop()
            self.status_var.set("Ready")

def main():
    # Check if epub2pdf.sh exists
    if not os.path.exists("epub2pdf.sh"):
        messagebox.showerror("Error", "epub2pdf.sh not found in current directory")
        return
        
    # Create and run GUI
    root = tk.Tk()
    app = Epub2PdfGUI(root)
    
    # Configure style
    style = ttk.Style()
    style.theme_use('clam')
    
    # Make the window appear in front
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)
    
    root.mainloop()

if __name__ == "__main__":
    main() 