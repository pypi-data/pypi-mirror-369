import numpy as np
from scipy.stats import median_abs_deviation


def os_cfar_1d(data, guard_cells, train_cells, rank_k, threshold_factor):
    """
    Performs 1D Ordered Statistic Constant False Alarm Rate (OS-CFAR) detection.

    Args:
        data (np.ndarray): 1D array of input data (must be in linear power,
                           not dB).
        guard_cells (int): Number of guard cells on EACH side of the CUT.
        train_cells (int): Number of training cells on EACH side of the CUT.
        rank_k (int): The rank (1-based index) of the sorted training cell
                      values to use for noise estimation (1 <= rank_k <= N).
                      N = 2 * train_cells is the total number of training cells.
                      A common choice is around 0.75 * N.
        threshold_factor (float): The scaling factor (alpha) to multiply the
                                  noise estimate by to get the threshold.

    Returns:
        tuple: A tuple containing:
            - detected_peaks_indices (np.ndarray): Indices where peaks were detected.
            - threshold (np.ndarray): The calculated threshold for each cell.
                                      (Same size as input data, padded with NaNs
                                       at edges where CFAR wasn't computed).
    """
    if not isinstance(data, np.ndarray) or data.ndim != 1:
        raise ValueError("Input 'data' must be a 1D NumPy array.")
    if guard_cells < 0 or train_cells <= 0 or rank_k <= 0:
        raise ValueError("guard_cells, train_cells, and rank_k must be positive.")

    num_cells = len(data)
    # Total number of training cells in the window
    N = 2 * train_cells
    if rank_k > N:
        raise ValueError(
            f"rank_k ({rank_k}) cannot be greater than the total "
            f"number of training cells N ({N})."
        )

    # Calculate half window size (excluding CUT)
    window_half_size = guard_cells + train_cells

    # Initialize threshold array and detections list
    threshold = np.full(num_cells, np.nan)  # Use NaN for edges
    detected_peaks_indices = []

    # Slide the window across the data
    # Skip edges where the full window doesn't fit
    for i in range(window_half_size, num_cells - window_half_size):
        # Define indices for the window components
        cut_index = i

        # Indices for leading training cells
        lead_train_start = i - window_half_size
        lead_train_end = i - guard_cells - 1  # Inclusive index

        # Indices for lagging training cells
        lag_train_start = i + guard_cells + 1
        lag_train_end = i + window_half_size  # Inclusive index

        # Extract values from training cells
        leading_train_values = data[lead_train_start : lead_train_end + 1]
        lagging_train_values = data[lag_train_start : lag_train_end + 1]

        # Combine training cell values
        all_train_values = np.concatenate((leading_train_values, lagging_train_values))

        # --- OS-CFAR Core Logic ---
        # Sort the training cell values
        sorted_train_values = np.sort(all_train_values)

        # Select the k-th ordered statistic as the noise estimate (Z)
        # Use rank_k - 1 because of 0-based indexing
        noise_estimate = sorted_train_values[rank_k - 1]
        # --- End OS-CFAR Core Logic ---

        # Calculate the threshold (T = alpha * Z)
        current_threshold = threshold_factor * noise_estimate
        threshold[cut_index] = current_threshold

        # Compare Cell Under Test (CUT) value to the threshold
        cut_value = data[cut_index]
        if cut_value > current_threshold:
            detected_peaks_indices.append(cut_index)

    return np.array(detected_peaks_indices), threshold


def variable_window_cfar(
    data, guard_cells, min_window, max_window, homogeneity_threshold
):
    """
    A basic implementation of a Variable Window CFAR detector using a split-window approach.

    Args:
        data (np.ndarray): The input signal data (1D).
        guard_cells (int): The number of guard cells on each side of the CUT.
        min_window (int): The minimum number of reference cells on each side.
        max_window (int): The maximum number of reference cells on each side.
        homogeneity_threshold (float): A threshold to determine if the reference
                                       windows are considered homogeneous.

    Returns:
        np.ndarray: A boolean array indicating detections (True) and non-detections (False).
    """
    n = len(data)
    detections = np.zeros(n, dtype=bool)

    for i in range(n):
        # Determine the possible range for the reference window
        start = max(0, i - guard_cells - max_window)
        end = min(n, i + guard_cells + max_window + 1)

        # Split the reference window into leading and lagging parts
        leading_start = start
        leading_end = max(start, i - guard_cells)
        lagging_start = min(end, i + guard_cells + 1)
        lagging_end = end

        # Extract the leading and lagging reference cells
        leading_ref = data[leading_start:leading_end]
        lagging_ref = data[lagging_start:lagging_end]

        # Calculate a homogeneity measure (e.g., ratio of standard deviations or MAD)
        if len(leading_ref) > 0 and len(lagging_ref) > 0:
            mad_leading = (
                median_abs_deviation(leading_ref)
                if len(leading_ref) > 1
                else np.std(leading_ref)
            )
            mad_lagging = (
                median_abs_deviation(lagging_ref)
                if len(lagging_ref) > 1
                else np.std(lagging_ref)
            )

            if mad_leading > 0:
                homogeneity_metric = mad_lagging / mad_leading
            elif mad_lagging > 0:
                homogeneity_metric = mad_leading / mad_lagging
            else:
                homogeneity_metric = 1.0  # Both are constant

            # Adjust the window size based on homogeneity
            if (
                homogeneity_metric > homogeneity_threshold
                or homogeneity_metric < 1 / homogeneity_threshold
            ):
                # Non-homogeneous: Use a smaller window
                num_ref_cells = min_window
            else:
                # Homogeneous: Use a larger window
                num_ref_cells = max_window

            # Redefine the reference window with the adjusted size
            ref_start = max(0, i - guard_cells - num_ref_cells)
            ref_end = min(n, i + guard_cells + num_ref_cells + 1)

            leading_ref_adjusted = data[
                max(0, i - guard_cells - num_ref_cells) : max(0, i - guard_cells)
            ]
            lagging_ref_adjusted = data[
                min(n, i + guard_cells + 1) : min(
                    n, i + guard_cells + num_ref_cells + 1
                )
            ]
            reference_cells = np.concatenate(
                (leading_ref_adjusted, lagging_ref_adjusted)
            )

            if len(reference_cells) >= 2 * min_window:
                # Estimate the noise level (e.g., using the mean or ordered statistic)
                noise_estimate = np.mean(reference_cells)  # Simple mean estimation

                # Apply the CFAR detection
                threshold_factor = 3  # Adjust as needed
                threshold = threshold_factor * noise_estimate
                if data[i] > threshold:
                    detections[i] = True
        else:
            # Handle edge cases where not enough reference cells are available
            detections[i] = False

    return detections


def variable_window_os_cfar_indices(
    data,
    guard_cells,
    min_window,
    max_window,
    k_rank,
    homogeneity_threshold,
    threshold_factor,
):
    """
    A basic implementation of a Variable Window OS-CFAR detector returning detection indices.

    Args:
        data (np.ndarray): The input signal data (1D).
        guard_cells (int): The number of guard cells on each side of the CUT.
        min_window (int): The minimum number of reference cells on each side.
        max_window (int): The maximum number of reference cells on each side.
        k_rank (int): The rank of the order statistic to use for noise estimation.
        homogeneity_threshold (float): A threshold to determine if the reference
                                       windows are considered homogeneous.
        threshold_factor (float): Factor multiplied by the noise estimate for the threshold.

    Returns:
        np.ndarray: An array of indices where detections occurred.
    """
    n = len(data)
    detection_indices = []

    for i in range(n):
        current_window_size = min_window

        # Determine the possible range for the reference window
        start = max(0, i - guard_cells - max_window)
        end = min(n, i + guard_cells + max_window + 1)

        while current_window_size <= max_window:
            leading_start = max(start, i - guard_cells - current_window_size)
            leading_end = max(start, i - guard_cells)
            lagging_start = min(end, i + guard_cells + 1)
            lagging_end = min(end, i + guard_cells + 1 + current_window_size)

            leading_ref = data[leading_start:leading_end]
            lagging_ref = data[lagging_start:lagging_end]

            if len(leading_ref) >= min_window and len(lagging_ref) >= min_window:
                mad_leading = (
                    median_abs_deviation(leading_ref)
                    if len(leading_ref) > 1
                    else np.std(leading_ref)
                )
                mad_lagging = (
                    median_abs_deviation(lagging_ref)
                    if len(lagging_ref) > 1
                    else np.std(lagging_ref)
                )

                if mad_leading > 0:
                    homogeneity_metric = mad_lagging / mad_leading
                elif mad_lagging > 0:
                    homogeneity_metric = mad_leading / mad_lagging
                else:
                    homogeneity_metric = 1.0

                if (
                    homogeneity_metric > homogeneity_threshold
                    or homogeneity_metric < 1 / homogeneity_threshold
                ):
                    # Non-homogeneous, use the current (smaller) window
                    num_ref_cells = current_window_size
                    break  # Exit the window expansion loop
                else:
                    # Homogeneous, try a larger window
                    current_window_size += 1
            else:
                current_window_size += 1  # Not enough cells for homogeneity check

        # Apply OS-CFAR with the determined window size
        leading_start_final = max(0, i - guard_cells - current_window_size)
        leading_end_final = max(0, i - guard_cells)
        lagging_start_final = min(n, i + guard_cells + 1)
        lagging_end_final = min(n, i + guard_cells + 1 + current_window_size)

        reference_cells = np.concatenate(
            (
                data[leading_start_final:leading_end_final],
                data[lagging_start_final:lagging_end_final],
            )
        )

        if len(reference_cells) >= 2 * min_window:
            sorted_ref = np.sort(reference_cells)
            noise_estimate = (
                sorted_ref[k_rank - 1]
                if k_rank <= len(sorted_ref)
                else np.mean(sorted_ref)
            )  # Handle edge case
            threshold = threshold_factor * noise_estimate
            if data[i] > threshold:
                detection_indices.append(i)

    return np.array(detection_indices, dtype=int)


# def do_oscfar_1d(
#     data: DataReader, show=False, gc=1, tc=10, rank_k=0.75, thres=1.05, min_e=2, max_e=10, min_dist=6, cut_f=0.1, rate=1, f_order=5, filter_type='high'
# ):
#     guard_cells_os = gc  # Number of guard cells on each side
#     train_cells_os = tc  # Number of training cells on each side
#     N_total = 2 * train_cells_os
#     rank_k_os = int(
#         rank_k * N_total
#     )  # Choose rank (e.g., 75th percentile) - must be >= 1
#     threshold_factor_os = thres  # Alpha value (adjust based on desired Pfa)
#     time_series = np.sum(data.data_full, 0)

#     if filter_type == 'high':
#         filtered_ts = highpass_filter(time_series, cut_f, rate, order=f_order)
#     elif filter_type == 'low':
#         filtered_ts = lowpass_filter(time_series, cut_f, rate, order=f_order)

#     detected_indices_os, threshold_os = os_cfar_1d(
#         filtered_ts,
#         guard_cells=guard_cells_os,
#         train_cells=train_cells_os,
#         rank_k=rank_k_os,
#         threshold_factor=threshold_factor_os,
#     )

#     final_peaks = detected_indices_os
#     final_peaks = filter_peaks_by_extent_1d(final_peaks, min_e, max_e)
#     final_peaks = enforce_min_distance(list(final_peaks), time_series, min_dist)

#     if show:
#         plt.plot(data.times, time_series)
#         plt.plot(data.times, threshold_os, c="grey", linestyle="--")
#         plt.scatter(
#             data.times[final_peaks], time_series[final_peaks], marker="x", c="r"
#         )
#         plt.xlabel("Time (s)")
#         plt.ylabel("Summed Intensity")

#         plt.show()
#     return final_peaks, threshold_os
