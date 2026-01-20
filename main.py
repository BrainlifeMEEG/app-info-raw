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
    add_raw_info_to_product
)

# Set up matplotlib for headless execution
setup_matplotlib_backend()

# Ensure output directories exist
ensure_output_dirs('out_dir')

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

# Add channel positions information
positions = raw._get_channel_positions()
if positions is not None and np.any(~np.isnan(positions)):
    channel_positions_msg = "Channel positions:\n" + "\n".join(
        [f"{ch_name}: {pos.tolist()}" for ch_name, pos in zip(raw.ch_names, positions)]
    )
    add_info_to_product(product_items, channel_positions_msg)
else:
    msg = 'Full list of channels (no positions available): ' + ', '.join(raw.ch_names)
    add_info_to_product(product_items, msg)

# Create the product.json file
create_product_json(product_items)