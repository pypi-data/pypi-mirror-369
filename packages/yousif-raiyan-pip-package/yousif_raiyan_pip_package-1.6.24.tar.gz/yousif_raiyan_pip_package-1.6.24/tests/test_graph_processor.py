#!/usr/bin/env python3
"""
Test script for EEGGraphProcessor class
Streams a large EDF file window-by-window and checks that
a single graph-features pickle is written.
"""

import sys
import os
import matplotlib.pyplot as plt
import pickle
from pathlib import Path


# make sure our package is on PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.yousif_raiyan_pip_package import EDFLoader, EEGGraphProcessor

def save_correlation_matrices_as_images(pickle_path: str, output_folder: str):
        """
        Load a pickle file containing one or more correlation matrices and
        save each matrix as its own PNG in the specified output folder.

        :param pickle_path: Path to the pickle file. Supported formats:
                            - dict with keys "corr_matrices" (list of 2D arrays)
                            and optional "starts" (list of start indices).
                            - list or tuple of 2D correlation arrays.
                            - a single 2D array.
        :param output_folder: Directory where PNGs will be saved.
        """
        os.makedirs(output_folder, exist_ok=True)

        # 1) Load the pickle
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)

        # 2) Determine how to extract matrices and labels
        if isinstance(data, dict) and "corr_matrices" in data:
            matrices = data["corr_matrices"]
            starts = data.get("starts", list(range(len(matrices))))
        elif isinstance(data, (list, tuple)):
            matrices = data
            starts = list(range(len(matrices)))
        else:
            matrices = [data]
            starts = [0]

        # 3) Plot each matrix
        for idx, mat in enumerate(matrices):
            fig, ax = plt.subplots()
            cax = ax.imshow(mat, aspect='auto')
            ax.set_title(f"Correlation Matrix (start idx: {starts[idx]})")
            plt.colorbar(cax, ax=ax)
            plt.tight_layout()

            # 4) Save to file
            fname = f"corr_{idx:04d}.png"
            path = os.path.join(output_folder, fname)
            fig.savefig(path)
            plt.close(fig)

        print(f"✔ Plotted {len(matrices)} correlation matrices to '{output_folder}'")

def test_graph_processor():
    loader = EDFLoader(folder_path="data", name="Sebastian")
    proc   = EEGGraphProcessor(edf_loader=loader, window_size=1000)
    #proc.generate_graphs_from_edf()

    # path = proc.compute_time_varying_segment_correlation(
    # start_time=100.0,
    # stop_time=140.0,
    # interval_seconds=1.0
    # )

    image_files = save_correlation_matrices_as_images("graph_representation/Sebastian_100-140_corr.pickle", "graph_representation/corr_frames")

if __name__ == "__main__":
    test_graph_processor()
