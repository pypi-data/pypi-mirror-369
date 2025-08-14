import numpy as np
import pandas as pd

from scipy.signal import butter, filtfilt, medfilt
from scipy.stats import median_abs_deviation
from statsmodels.nonparametric.smoothers_lowess import lowess


def remove_baseline_peaks(
    data, detection_indices, noise_estimates, secondary_threshold_factor=2.0
):
    """
    Removes detected peaks that are too close to the baseline using a secondary amplitude threshold.

    Args:
        data (np.ndarray): The original signal data.
        detection_indices (np.ndarray): Indices of peaks detected by OS-CFAR.
        noise_estimates (np.ndarray): Array of noise estimates corresponding to each detection.
        secondary_threshold_factor (float): Factor multiplied by the noise estimate
                                           to set the secondary threshold.

    Returns:
        np.ndarray: Indices of the filtered detections.
    """
    filtered_detections = []
    for idx, noise_est in zip(detection_indices, noise_estimates):
        peak_amplitude = data[idx]
        secondary_threshold = secondary_threshold_factor * noise_est
        if peak_amplitude > secondary_threshold:
            filtered_detections.append(idx)
    return np.array(filtered_detections, dtype=int)


def median_filter(data, kernel_size):
    """
    Applies a median filter to the 1D data.

    Args:
        data (np.ndarray): 1D array of input data.
        kernel_size (int): The size of the median filter kernel. Must be a
                           positive integer. If even, it will be incremented
                           by 1 to ensure an odd size.

    Returns:
        np.ndarray: The median-filtered data array, same shape as input.

    Raises:
        ValueError: If input data is not a 1D numpy array, or if kernel_size
                    is not a positive integer.
    """

    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")
    if not isinstance(kernel_size, int) or kernel_size <= 0:
        raise ValueError("kernel_size must be a positive integer.")
    if kernel_size % 2 == 0:
        print(
            "Warning: Median filter kernel size should ideally be odd. Incrementing by 1."
        )
        kernel_size += 1

    filtered_data = medfilt(data, kernel_size=kernel_size)
    return filtered_data


def lowpass_filter(data, cutoff_freq, sampling_rate, order=5):
    """
    Applies a low-pass Butterworth filter to the 1D data.

    This uses a zero-phase filter ('filtfilt') to avoid introducing phase shifts in the filtered signal.

    Args:
        data (np.ndarray): 1D array of input data (e.g., time series).
        cutoff_freq (float): The desired cutoff frequency in Hz. Frequencies
                             above this value will be attenuated.
        sampling_rate (float): The sampling rate of the input data in Hz.
                               This is crucial for digital filter design.
        order (int, optional): The order of the Butterworth filter. Higher
                               orders provide a steeper rolloff but can be
                               less stable. Defaults to 5.

    Returns:
        np.ndarray: The low-pass filtered data array, same shape as input.

    Raises:
        ValueError: If input data is not a 1D numpy array, or if
                    cutoff_freq or sampling_rate are invalid.
    """

    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")
    if cutoff_freq <= 0:
        raise ValueError("cutoff_freq must be positive.")
    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be positive.")

    nyquist_freq = 0.5 * sampling_rate
    if cutoff_freq >= nyquist_freq:
        # For lowpass, cutoff >= nyquist means filtering everything, which is usually not intended.
        # Consider warning or adjusting behavior.
        print(
            f"Warning: cutoff_freq ({cutoff_freq} Hz) is >= Nyquist frequency ({nyquist_freq} Hz). "
            "Result might be heavily smoothed or zero."
        )
        # Or raise ValueError("cutoff_freq must be less than the Nyquist frequency.")

    normal_cutoff = cutoff_freq / nyquist_freq
    b, a = butter(order, normal_cutoff, btype="low", analog=False)
    filtered_data = filtfilt(b, a, data)
    return filtered_data


def highpass_filter(data, cutoff_freq, sampling_rate, order=5):
    """
    Applies a high-pass Butterworth filter to the 1D data.

    This uses a zero-phase filter ('filtfilt') to avoid introducing
    phase shifts in the filtered signal.

    Args:
        data (np.ndarray): 1D array of input data (e.g., time series).
        cutoff_freq (float): The desired cutoff frequency in Hz. Frequencies
                             below this value will be attenuated.
        sampling_rate (float): The sampling rate of the input data in Hz.
                               This is crucial for digital filter design.
        order (int, optional): The order of the Butterworth filter. Higher
                               orders provide a steeper rolloff but can be
                               less stable. Defaults to 5.

    Returns:
        np.ndarray: The high-pass filtered data array, same shape as input.

    Raises:
        ValueError: If input data is not a 1D numpy array, or if
                    cutoff_freq or sampling_rate are invalid.
    """
    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")
    if cutoff_freq <= 0:
        raise ValueError("cutoff_freq must be positive.")
    if sampling_rate <= 0:
        raise ValueError("sampling_rate must be positive.")

    # Nyquist frequency is half the sampling rate
    nyquist_freq = 0.5 * sampling_rate

    # Check if the cutoff frequency is valid (must be less than Nyquist)
    if cutoff_freq >= nyquist_freq:
        # You might want to handle this differently, e.g., return data unmodified
        # or issue a warning. Raising an error is safest for filter design.
        raise ValueError(
            f"cutoff_freq ({cutoff_freq} Hz) must be less than "
            f"the Nyquist frequency ({nyquist_freq} Hz)."
        )

    # Normalize the cutoff frequency to the Nyquist frequency
    normal_cutoff = cutoff_freq / nyquist_freq

    # Design the Butterworth filter
    # b, a are the numerator and denominator polynomials of the IIR filter
    b, a = butter(order, normal_cutoff, btype="high", analog=False)

    # Apply the filter using filtfilt for zero phase distortion
    # filtfilt applies the filter forward and then backward
    filtered_data = filtfilt(b, a, data)

    return filtered_data


def group_close_peaks(peak_indices, min_distance):
    """
    Groups peak indices that are close to each other.

    Iterates through sorted peak indices and groups any peaks that are
    separated by less than or equal to 'min_distance' samples.

    Args:
        peak_indices (list or np.ndarray): A list or array of peak indices,
                                           assumed to be sorted or will be sorted.
        min_distance (int): The maximum distance (in samples) between two
                            consecutive peaks for them to be considered
                            part of the same group.

    Returns:
        list[list[int]]: A list where each element is a list representing a
                         group of close peak indices. Returns an empty list
                         if no peaks are provided.
    """
    if not peak_indices:
        return []

    # Ensure indices are sorted
    sorted_indices = np.sort(peak_indices)

    groups = []
    current_group = [sorted_indices[0]]

    for i in range(1, len(sorted_indices)):
        # Check distance to the *last* peak added to the current group
        if sorted_indices[i] - current_group[-1] <= min_distance:
            # If close enough, add to the current group
            current_group.append(sorted_indices[i])
        else:
            # If too far, the current group is finished
            groups.append(current_group)
            # Start a new group with the current peak
            current_group = [sorted_indices[i]]

    # Add the last group after the loop finishes
    groups.append(current_group)

    return groups


def find_representative_peaks(data, peak_indices, min_distance):
    """
    Groups close peaks and returns the index of the maximum peak from each group.

    First, groups peaks that are within 'min_distance' of each other using
    group_close_peaks. Then, for each group, identifies the index
    corresponding to the highest value in the 'data' array.

    Args:
        data (np.ndarray): The 1D data array (e.g., time series) where
                           peak values are found. Used to determine the max peak.
        peak_indices (list or np.ndarray): A list or array of peak indices
                                           to be grouped and processed.
        min_distance (int): The maximum distance (in samples) between two
                            consecutive peaks for them to be considered
                            part of the same group.

    Returns:
        list[int]: A list containing the index of the maximum peak from
                   each identified group. Returns an empty list if no
                   peaks are provided.
    """
    if not peak_indices:
        return []
    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")

    # Step 1: Group the peaks
    peak_groups = group_close_peaks(peak_indices, min_distance)

    representative_peaks = []
    if not peak_groups:
        return []  # Should not happen if peak_indices is not empty, but safe check

    # Step 2: Find the maximum peak in each group
    for group in peak_groups:
        if not group:  # Skip empty groups if they somehow occur
            continue

        # Get the values of the peaks in the current group
        peak_values_in_group = data[group]

        # Find the index within the *group* list that corresponds to the max value
        max_value_index_in_group = np.argmax(peak_values_in_group)

        # Get the original index from the 'group' list using this relative index
        strongest_peak_original_index = group[max_value_index_in_group]

        representative_peaks.append(strongest_peak_original_index)

    # Return the sorted list of representative peaks for consistency
    return sorted(representative_peaks)


def verify_peaks_snr(data, peak_indices, noise_window_factor=3, min_snr=3.0):
    """
    Verifies peaks based on their local Signal-to-Noise Ratio (SNR).

    Calculates SNR for each peak relative to the noise estimated in
    adjacent windows.

    Args:
        data (np.ndarray): The 1D data array (e.g., time series) where
                           peaks were detected.
        peak_indices (list or np.ndarray): Indices of the detected peaks.
        noise_window_factor (int, optional): Determines the size and offset
                                             of the noise estimation windows
                                             relative to a conceptual 'peak width'.
                                             A simple proxy for peak width (e.g., 5 samples)
                                             is used internally. The noise windows will
                                             be roughly this size and offset by
                                             this amount from the peak center.
                                             Defaults to 3.
        min_snr (float, optional): The minimum acceptable local SNR for a
                                   peak to be considered verified. Defaults to 3.0.

    Returns:
        list: A list of indices corresponding to the verified peaks.

    Raises:
        ValueError: If input data is not a 1D numpy array.
    """
    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")
    if not peak_indices:
        return []  # Return empty list if no peaks to check

    verified_peaks = []
    n_samples = len(data)

    # Use a small, fixed window size proxy for basic peak region/noise offset
    # A more sophisticated approach might estimate width dynamically.
    approx_peak_half_width = 5  # Heuristic: assume peak affects +/- 5 samples
    noise_offset = noise_window_factor * approx_peak_half_width
    noise_window_size = noise_window_factor * approx_peak_half_width

    for peak_idx in peak_indices:
        peak_value = data[peak_idx]

        # Define noise estimation windows (careful with boundaries)
        noise_win1_start = max(0, peak_idx - noise_offset - noise_window_size)
        noise_win1_end = max(0, peak_idx - noise_offset)

        noise_win2_start = min(n_samples, peak_idx + noise_offset + 1)
        noise_win2_end = min(n_samples, peak_idx + noise_offset + noise_window_size + 1)

        # Collect noise samples, excluding the immediate peak vicinity
        noise_samples = []
        if noise_win1_end > noise_win1_start:
            noise_samples.extend(data[noise_win1_start:noise_win1_end])
        if noise_win2_end > noise_win2_start:
            noise_samples.extend(data[noise_win2_start:noise_win2_end])

        if not noise_samples:
            # Cannot estimate noise if windows are empty (e.g., peak at edge)
            # Decide how to handle: skip, keep, or use global noise? Let's skip for now.
            # print(f"Warning: Could not estimate local noise for peak at index {peak_idx}. Skipping verification.")
            continue

        # Estimate local baseline (median) and noise level (MAD)
        local_baseline = np.median(noise_samples)
        # Use MAD for robustness to outliers in noise windows. Scale to estimate std dev.
        # scale=1.4826 converts MAD to std dev for Gaussian noise
        local_noise_std = median_abs_deviation(
            noise_samples, scale=1.4826, nan_policy="omit"
        )

        # Handle cases where noise estimate is zero or very small
        if local_noise_std < 1e-9:
            # If noise is essentially zero, any positive peak amplitude gives huge SNR.
            # Check if peak is significantly above baseline. If baseline is also zero,
            # it's ambiguous. Let's keep it if peak > baseline, otherwise discard.
            if peak_value > local_baseline:
                snr = np.inf  # Assign infinite SNR
            else:
                snr = 0.0
        else:
            # Calculate SNR
            signal_amplitude = peak_value - local_baseline
            snr = signal_amplitude / local_noise_std

        # Verify peak
        if snr >= min_snr:
            verified_peaks.append(peak_idx)

    return verified_peaks


def enforce_min_distance(raw_peak_indices, data_values, min_distance):
    """
    Refines CFAR detections to enforce a minimum distance between peaks.

    Args:
        raw_peak_indices: List of indices where CFAR detected a peak.
        data_values: The original data array (or SNR array) used for sorting.
        min_distance: The minimum allowed separation between final peaks (in indices).

    Returns:
        List of indices of the final, refined peaks.
    """

    if not raw_peak_indices:
        return []

    # Get peak values and sort peaks by value (descending)
    peak_info = []
    for idx in raw_peak_indices:
        # Handle potential index errors if raw_peak_indices are not guaranteed to be valid
        if 0 <= idx < len(data_values):
            peak_info.append({"index": idx, "value": data_values[idx]})
        # else: handle error or skip invalid index

    # Sort by value, strongest first
    sorted_peaks = sorted(peak_info, key=lambda p: p["value"], reverse=True)

    final_peaks_indices = []
    suppressed = [False] * len(data_values)  # Or use a set for sparse indices

    for peak in sorted_peaks:
        idx = peak["index"]

        # Check if this peak or its location has already been suppressed by a stronger neighbor
        if suppressed[idx]:
            continue

        # Keep this peak
        final_peaks_indices.append(idx)
        suppressed[idx] = True  # Mark as kept/processed

        # Suppress neighbors within min_distance
        # Careful with boundary conditions
        start_suppress = max(0, idx - min_distance)
        end_suppress = min(len(data_values) - 1, idx + min_distance)

        for i in range(start_suppress, end_suppress + 1):
            suppressed[i] = True  # Suppress the whole region

        # More precise alternative: Only suppress other *detected* raw peaks within the distance
        # This requires iterating through 'sorted_peaks' again or having an efficient lookup
        # for other_peak in sorted_peaks:
        #    if not suppressed[other_peak['index']] and abs(other_peak['index'] - idx) <= min_distance:
        #        suppressed[other_peak['index']] = True

    # Optional: Sort final peaks by index if needed
    final_peaks_indices.sort()

    return final_peaks_indices


def filter_peaks_by_extent_1d(peak_indices, min_extent, max_extent):
    """
    Filters a list of 1D peak indices, removing peaks that belong to consecutive groups larger than max_extent.

    Args:
        peak_indices (list or np.ndarray): A list or array of integer indices
                                           where peaks were detected by CFAR.
                                           Assumed to be along a single dimension.
        max_extent (int): The maximum allowed number of consecutive indices
                          for a valid peak group. Groups larger than this
                          are considered extended clutter/scattering and removed.

    Returns:
        list: A list of filtered peak indices, keeping only those belonging
              to groups with extent <= max_extent.
    """
    if not isinstance(peak_indices, (list, np.ndarray)):
        raise TypeError("peak_indices must be a list or numpy array")
    if len(peak_indices) == 0:
        return []
    if max_extent < 1:
        raise ValueError("max_extent must be at least 1")

    # Ensure indices are sorted and unique for grouping
    sorted_indices = np.unique(np.sort(np.asarray(peak_indices)))

    if len(sorted_indices) == 0:
        return []

    filtered_peaks = []
    current_group_start_index = 0

    for i in range(1, len(sorted_indices)):
        # Check if the current index breaks the consecutive sequence
        if sorted_indices[i] != sorted_indices[i - 1] + 1:
            # End of the previous group (or a single-element group)
            group_end_index = i - 1
            group_extent = group_end_index - current_group_start_index + 1

            # Check if the completed group's extent is acceptable
            if group_extent <= max_extent and group_extent >= min_extent:
                # Add all indices from this valid group
                filtered_peaks.extend(
                    sorted_indices[current_group_start_index : group_end_index + 1]
                )

            # Start a new group
            current_group_start_index = i

    # Handle the very last group after the loop finishes
    group_end_index = len(sorted_indices) - 1
    group_extent = group_end_index - current_group_start_index + 1
    if group_extent <= max_extent and group_extent >= min_extent:
        filtered_peaks.extend(
            sorted_indices[current_group_start_index : group_end_index + 1]
        )

    return filtered_peaks  # Return as a list, or np.array(filtered_peaks) if preferred


def moving_average_filter(data, window_size):
    """
    Applies a simple moving average filter to the 1D data.

    Each point in the output is the average of the 'window_size' neighboring
    points in the input data (including the point itself). Uses 'same' mode
    for convolution, meaning the output array has the same size as the input,
    but edge effects might be present where the window doesn't fully overlap.

    Args:
        data (np.ndarray): 1D array of input data.
        window_size (int): The number of points to include in the averaging
                           window. Should be an odd number for a centered average,
                           but works with even numbers too. Must be positive.

    Returns:
        np.ndarray: The smoothed data array, same shape as input.

    Raises:
        ValueError: If input data is not a 1D numpy array or if window_size
                    is not a positive integer.
    """
    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")
    if not isinstance(window_size, int) or window_size <= 0:
        raise ValueError("window_size must be a positive integer.")
    if window_size > len(data):
        raise ValueError("window_size cannot be larger than the data length.")

    kernel = np.ones(window_size) / window_size
    filtered_data = np.convolve(data, kernel, mode="same")

    return filtered_data


def lowess_filter(xdata, ydata, smoothing_factor):
    """
    Applies a Locally Weighted Scatterplot Smoothing (LOWESS) filter to the data.

    LOWESS is a non-parametric regression method that fits simple models to
    localized subsets of the data to build up a function that describes the
    deterministic part of the variation in the data, point by point.

    Args:
        xdata (np.ndarray): 1D array of independent variable values (e.g., time).
        ydata (np.ndarray): 1D array of dependent variable values (e.g., signal).
                            Must have the same length as xdata.
        smoothing_factor (float): The fraction of the data to use when
                                  estimating the local regression. Should be
                                  between 0 and 1. Larger values result in
                                  smoother curves.

    Returns:
        np.ndarray: The smoothed y-values, corresponding to the xdata points.

    Raises:
        ValueError: If xdata or ydata are not 1D numpy arrays, if they have
                    different lengths, or if smoothing_factor is not between 0 and 1.
    """
    if not isinstance(xdata, np.ndarray) or xdata.ndim != 1:
        raise ValueError("Input 'xdata' must be a 1D NumPy array.")
    if not isinstance(ydata, np.ndarray) or ydata.ndim != 1:
        raise ValueError("Input 'ydata' must be a 1D NumPy array.")
    if len(xdata) != len(ydata):
        raise ValueError("xdata and ydata must have the same length.")
    if not (0 <= smoothing_factor <= 1):
        raise ValueError("smoothing_factor must be between 0 and 1.")

    # The lowess function returns a 2D array where the first column is x and the second is the smoothed y

    smooth = lowess(ydata, xdata, frac=smoothing_factor)
    x, y_smooth = smooth[..., 0], smooth[..., 1]
    return y_smooth
