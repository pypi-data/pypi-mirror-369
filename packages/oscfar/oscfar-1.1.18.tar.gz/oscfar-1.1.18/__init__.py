import numpy as np

# Package to do OS-CFAR + Useful filters
__version__ = "1.1.18"

from . import cfar
from . import filters
from . import utils
from . import gaussian_fit
from . import cluster

# OS-CFAR versions
os_cfar = cfar.os_cfar_1d
vwindow_os_cfar = cfar.variable_window_os_cfar_indices

# Filters
baseline_filter = filters.remove_baseline_peaks
lowpass_filter = filters.lowpass_filter
highpass_filter = filters.highpass_filter

median_smoothing = filters.median_filter
mean_smoothing = filters.moving_average_filter
lowess_smoothing = filters.lowess_filter

group_peaks = filters.find_representative_peaks
force_min_dist = filters.enforce_min_distance
check_snr = filters.verify_peaks_snr
force_max_extent = filters.filter_peaks_by_extent_1d

# Utilities
peaks = utils.Peaks
waterfall_axes = utils.WaterFallAxes
waterfall_grid = utils.WaterFallGrid
npz_reader = utils.NpzReader
npz_writer = utils.NpzWriter

# Gaussian functions
multi_gaussian = gaussian_fit.sum_of_gaussians
multi_scattered_gaussian = gaussian_fit.sum_of_scattered_gaussians
grid_search_gaussian = gaussian_fit.find_best_multi_gaussian_fit

# Other utilities
best_params = {
    "guard_cells": 1,
    "train_cells": 8,
    "rank_k": 0.75,
    "threshold_factor": 0.9,
    "averaging": 2,
    "min_snr": 2,
    "baseline": 0.15,
    "smoothing": "lowess",
}


def do_os_cfar(
    data: np.ndarray,
    guard_cells,
    train_cells,
    rank_k,
    threshold_factor,
    averaging,
    min_dist,
    min_snr,
    baseline,
    smoothing="mean",
    lowess_frac=0.01,
    clustering=False,
    clustering_cutoff=0.7,
):
    """
    Perform OS-CFAR detection and post-processing on 2D array data.

    This function applies Ordered Statistics CFAR (OS-CFAR) detection to a 2D input array
    (e.g., a spectrogram), typically by summing along one axis to produce a 1D time series.
    It then applies smoothing, peak detection, SNR filtering, baseline removal, and optional clustering.

    Args:
        data (np.ndarray): 2D input array (e.g., frequency x time), assumed to be linear power.
        guard_cells (int): Number of guard cells on each side of the cell under test (CUT).
        train_cells (int): Number of training cells on each side of the CUT.
        rank_k (float): Fraction (0-1) of training cells to use for the OS-CFAR rank (e.g., 0.75 for 75th percentile).
        threshold_factor (float): Scaling factor (alpha) for the OS-CFAR threshold.
        averaging (int): Window size for initial smoothing (mean or median).
        min_dist (int): Minimum distance (in samples) between detected peaks.
        min_snr (float): Minimum SNR required for a peak to be kept.
        baseline (float): Threshold factor for removing peaks close to the baseline.
        smoothing (str, optional): Smoothing method for the time series ('mean', 'median', 'lowess', or None). Default is 'mean'.
        lowess_frac (float, optional): Fraction of data for LOWESS smoothing if used. Default is 0.01.
        clustering (int or bool, optional): If int > 0, applies DBSCAN clustering to peaks with this as min_samples. Default is False.
        clustering_cutoff (float, optional): Cutoff value for clustering. Default is 0.7.

    Returns:
        Peaks: Peaks object containing detected peak indices and the OS-CFAR threshold array.

    Raises:
        TypeError: If input data is not a 2D NumPy array.
    """

    if len(data.shape) != 2:
        raise TypeError(
            f"Data should be two dimensional only! Received {len(data.shape)} dimensions."
        )

    x = np.arange(data.shape[1])
    ts = np.sum(data, 0)
    stdev = np.std(data, 0)
    mts = np.mean(data, 0)

    if smoothing == "mean":
        filtered = mean_smoothing(ts, averaging)
    elif smoothing == "median":
        filtered = median_smoothing(ts, averaging)
    elif smoothing == "lowess":
        filtered = lowess_smoothing(x, ts, lowess_frac)
    else:
        filtered = ts

    res = os_cfar(
        filtered,
        guard_cells,
        train_cells,
        int(rank_k * 2 * train_cells),
        threshold_factor,
    )

    pk = res[0]
    pk = force_min_dist(list(pk), filtered, min_dist)
    pk = check_snr(filtered, list(pk), min_dist, min_snr)
    pk = group_peaks(filtered, list(pk), min_dist)
    pk = baseline_filter(mts, pk, stdev, baseline)

    if type(clustering) == int and clustering != 0:
        pk = cluster.cluster_peaks_ph(pk, filtered[pk], clustering, clustering_cutoff)

    return peaks((pk, res[1]))
