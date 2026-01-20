"""
Display raw MNE data information and metadata.

This app loads MNE raw data files and displays detailed information about the
data including channel types, sampling rate, duration, and channel positions.

Input:
    - raw: Path to MNE raw data file (.fif format)

Output:
    - out_dir/info.txt: Text file with complete raw data information
    - product.json: Metadata for Brainlife.io visualization
"""

# Copyright (c) 2020 brainlife.io
#
# This app displays MNE raw data information.
#
# Author: Kami Salibayeva
# Indiana University

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'brainlife_utils'))

# Standard imports
import mne
import numpy as np

# Import shared utilities
from brainlife_utils import (
    load_config,
    setup_matplotlib_backend,
    ensure_output_dirs,
    create_product_json,
    add_info_to_product,
    add_raw_info_to_product,
    add_image_to_product,
    save_figure_with_base64
)
import matplotlib.pyplot as plt

# Set up matplotlib for headless execution
setup_matplotlib_backend()

# Ensure output directories exist
ensure_output_dirs('out_dir', 'out_figs')

# Load configuration
config = load_config()

# == LOAD DATA ==
fname = config['raw']

# Read the raw data
raw = mne.io.read_raw_fif(fname)
info = raw.info

# == SAVE INFO TO FILE ==
# Save the info into an info.txt file
with open(os.path.join('out_dir', 'info.txt'), 'w') as f:
    print(info, file=f)

# == CREATE PRODUCT JSON ==
product_items = []

# Add structured raw info messages
add_raw_info_to_product(product_items, raw)

# Add channel positions visualization if available
positions = raw._get_channel_positions()
if positions is not None and np.any(~np.isnan(positions)):
    # Try to plot the montage
    try:
        # Create montage plot (2D topographic view)
        fig = plt.figure(figsize=(10, 8))
        mne.viz.plot_montage(raw.get_montage(), kind='topomap', show=False)
        montage_img = save_figure_with_base64(fig, 
                                              os.path.join('out_figs', 'montage_2d.png'))
        add_image_to_product(product_items, 'Channel Montage (2D)', 
                           base64_data=montage_img)
    except Exception as e:
        add_info_to_product(product_items, f"Could not plot montage: {str(e)}", 'warning')
    
    # Try to plot 3D electrode positions
    try:
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], s=50, alpha=0.6)
        
        # Add channel names to points
        for i, (pos, ch_name) in enumerate(zip(positions, raw.ch_names)):
            ax.text(pos[0], pos[1], pos[2], ch_name, fontsize=8, alpha=0.7)
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title('3D Electrode Positions')
        fig.tight_layout()
        
        electrode_img = save_figure_with_base64(fig, 
                                                os.path.join('out_figs', 'electrodes_3d.png'))
        add_image_to_product(product_items, 'Electrode Positions (3D)', 
                           base64_data=electrode_img)
    except Exception as e:
        add_info_to_product(product_items, f"Could not plot 3D positions: {str(e)}", 'warning')
else:
    msg = 'Full list of channels (no positions available): ' + ', '.join(raw.ch_names)
    add_info_to_product(product_items, msg)

# Create the product.json file
create_product_json(product_items)