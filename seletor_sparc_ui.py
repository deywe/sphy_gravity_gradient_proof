#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SPHY Framework - Visual Ingestion Interface
Script: SPARC Dataset Graphical Selector and Converter
Author: Deywe Okabe
Organization: Black Swan Research / Harpia Quantum
Environment: Local Windows (Native UI)
"""

import os
import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import pandas as pd

def process_and_save(file_path):
    """
    Executes the SPARC parsing engine and exports the flat SPHY payload.
    """
    try:
        file_name = os.path.basename(file_path)
        # Extracts the galaxy name by isolating the _rotmod.dat suffix
        galaxy_name = file_name.replace("_rotmod.dat", "").replace(".dat", "")
        
        col_radius, col_vobs, col_vgas, col_vdisk, col_vbulge = [], [], [], [], []
        
        with open(file_path, 'r') as f:
            for line in f:
                clean_line = line.strip()
                if clean_line.startswith('#') or not clean_line:
                    continue
                
                parts = clean_line.split()
                if len(parts) >= 5:
                    col_radius.append(float(parts[0]))
                    col_vobs.append(float(parts[1]))
                    col_vgas.append(float(parts[3]))
                    col_vdisk.append(float(parts[4]))
                    
                    if len(parts) >= 6:
                        col_vbulge.append(float(parts[5]))
                    else:
                        col_vbulge.append(0.0)

        # Phase space arrays
        r = np.array(col_radius)
        v_obs = np.array(col_vobs)
        v_gas = np.array(col_vgas)
        v_disk = np.array(col_vdisk)
        v_bulge = np.array(col_vbulge)

        # Classical negative noise filter
        v_gas[v_gas < 0] = 0.0
        v_disk[v_disk < 0] = 0.0
        v_bulge[v_bulge < 0] = 0.0

        # Composition of the visible baryonic tensor
        v_baryonic = np.sqrt(v_gas**2 + v_disk**2 + v_bulge**2)

        # Creation of the standard SPHY DataFrame
        df_csv = pd.DataFrame({
            'raio': r,
            'v_barionica': v_baryonic,
            'v_observada': v_obs
        })

        # Sets the output directory to match the source folder
        output_dir = os.path.dirname(file_path)
        output_path = os.path.join(output_dir, f"{galaxy_name}_ready_sphy.csv")
        
        df_csv.to_csv(output_path, index=False)
        
        messagebox.showinfo(
            "Cosmological Success", 
            f"Galaxy: {galaxy_name}\n\n"
            f"✓ CSV generated with {len(df_csv)} data points!\n"
            f"Saved at: {output_path}\n\n"
            f"Ready to be uploaded to the Streamlit API."
        )
        
    except Exception as e:
        messagebox.showerror("Tensor Error", f"Critical failure while processing the file:\n{str(e)}")

def open_file_selector():
    """
    Instantiates the hidden Tkinter graphical interface and opens the Windows file picker.
    """
    root = tk.Tk()
    root.withdraw() # Hides the empty main Tkinter window
    
    # Configures file extension filters for the selection dialog
    file_types = [
        ("SPARC Dat Files", "*_rotmod.dat"), 
        ("All Dat Files", "*.dat"), 
        ("Text Files", "*.txt")
    ]
    
    selected_path = filedialog.askopenfilename(
        title="SPHY Core - Select Galaxy from SPARC Catalog",
        filetypes=file_types
    )
    
    if selected_path:
        process_and_save(selected_path)
    else:
        print("[*] Operation canceled by user.")

if __name__ == "__main__":
    open_file_selector()