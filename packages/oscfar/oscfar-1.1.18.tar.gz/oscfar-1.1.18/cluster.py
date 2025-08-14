from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
import numpy as np


def cluster_peaks_p(peak_positions, peak_heights, n, max_e=0.7, verbose=False):
    """
     Cluster peak positions using DBSCAN and select the most prominent peak from each cluster.
     Parameters

    Args:
         peak_positions : array-like, shape (n_samples, n_features)
             The positions of the detected peaks to be clustered.
         peak_heights : array-like, shape (n_samples,)
             The heights (or intensities) of the detected peaks, used to select the most prominent peak in each cluster.
         n : int
             The minimum number of samples in a neighborhood for a point to be considered as a core point in DBSCAN.
         max_e : float, optional (default=0.7)
             The maximum distance between two samples for one to be considered as in the neighborhood of the other (epsilon parameter for DBSCAN).
         verbose : bool, optional (default=False)
             If True, prints the number of clusters found by DBSCAN.
    Returns
        clustered_peaks : list
            A list of peak positions, each representing the most prominent peak (highest peak height) from each cluster found by DBSCAN.
    Notes
        Peaks labeled as noise by DBSCAN (label -1) are ignored.
        The function uses StandardScaler to normalize peak positions before clustering.
    """

    scaler = StandardScaler()
    scaled_peak_data = scaler.fit_transform(np.array(peak_positions).reshape(-1, 1))

    dbscan = DBSCAN(max_e, min_samples=n)
    dbscan_cluster_labels = dbscan.fit_predict(scaled_peak_data)

    num_dbscan_clusters = len(set(dbscan_cluster_labels)) - (
        1 if -1 in dbscan_cluster_labels else 0
    )
    if verbose:
        print(f"Number of clusters found by DBSCAN: {num_dbscan_clusters}")

    clustered_groups = {}
    for ind, label in enumerate(dbscan_cluster_labels):
        if label == -1:
            continue

        if clustered_groups.get(label) is None:
            clustered_groups[label] = [(peak_positions[ind], ind)]
        else:
            clustered_groups[label].append((peak_positions[ind], ind))

    clustered_peaks = []
    for group_label in clustered_groups:
        pos = []
        h = []
        for pk in clustered_groups[group_label]:
            pos.append(pk[0])
            h.append(peak_heights[pk[1]])

        clustered_peaks.append(pos[np.argmax(h)])

    return clustered_peaks


def cluster_peaks_ph(peak_positions, peak_heights, n, max_e=0.7, verbose=False):
    """
    Clusters peaks based on their positions and heights using DBSCAN.

    Args:
        peak_positions (list or np.ndarray): Positions of the peaks.
        peak_heights (list or np.ndarray): Heights of the peaks.
        n (int): Minimum number of samples in a cluster.
        max_e (float, optional): The maximum distance between two samples for
                                 one to be considered as in the neighborhood
                                 of the other. Defaults to 0.7.
        verbose (bool, optional): If True, print the number of clusters found. Defaults to False.

    Returns:
        list: A list of representative peak positions, one from each cluster.
    """

    peak_data = np.array((peak_positions, peak_heights)).T

    scaler = StandardScaler()
    scaled_peak_data = scaler.fit_transform(peak_data)

    dbscan = DBSCAN(max_e, min_samples=n)
    dbscan_cluster_labels = dbscan.fit_predict(scaled_peak_data)

    num_dbscan_clusters = len(set(dbscan_cluster_labels)) - (
        1 if -1 in dbscan_cluster_labels else 0
    )
    if verbose:
        print(f"Number of clusters found by DBSCAN: {num_dbscan_clusters}")

    clustered_groups = {}
    for ind, label in enumerate(dbscan_cluster_labels):
        if label == -1:
            continue

        if clustered_groups.get(label) is None:
            clustered_groups[label] = [(peak_positions[ind], ind)]
        else:
            clustered_groups[label].append((peak_positions[ind], ind))

    clustered_peaks = []
    for group_label in clustered_groups:
        pos = []
        h = []
        for pk in clustered_groups[group_label]:
            pos.append(pk[0])
            h.append(peak_heights[pk[1]])

        clustered_peaks.append(pos[np.argmax(h)])

    return clustered_peaks
