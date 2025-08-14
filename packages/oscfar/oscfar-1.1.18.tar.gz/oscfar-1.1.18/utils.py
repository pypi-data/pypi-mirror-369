from fitburst.analysis.fitter import LSFitter
from fitburst.backend.generic import DataReader
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import logging, json

from uncertainties import ufloat


logger = logging.getLogger(__name__)
# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def plot_colormaps(gradient, cmap_category, category_name):
    """
    Plots a list of colormaps.
    """
    if not cmap_category:
        print(f"No colormaps in category: {category_name}")
        return

    # Calculate rows and columns for subplot grid
    n_colormaps = len(cmap_category)
    n_cols = 3  # You can adjust this for more/fewer columns
    n_rows = int(np.ceil(n_colormaps / n_cols))

    fig, axes = plt.subplots(
        n_rows,
        n_cols,
        figsize=(n_cols * 3.5, n_rows * 0.8),
        layout="constrained",
        squeeze=False,
    )
    fig.suptitle(f"Matplotlib Colormaps: {category_name}", fontsize=16, y=1.02)

    for i, cmap_name in enumerate(cmap_category):
        row = i // n_cols
        col = i % n_cols
        ax = axes[row, col]

        # Use the colormap
        try:
            cmap = mpl.colormaps[cmap_name]
            ax.imshow(gradient, aspect="auto", cmap=cmap)
        except KeyError:
            print(f"Cannot plot cmap: {cmap_name}")
            # continue

        ax.text(
            0.01,
            0.5,
            cmap_name,
            va="center",
            ha="left",
            fontsize=10,
            color="white",
            transform=ax.transAxes,
            bbox=dict(
                facecolor="black", alpha=0.5, edgecolor="none", boxstyle="round,pad=0.2"
            ),
        )

        ax.set_axis_off()

    # Hide any unused subplots
    for i in range(n_colormaps, n_rows * n_cols):
        row = i // n_cols
        col = i % n_cols
        axes[row, col].set_visible(False)

    plt.show()


def get_colormaps():
    """
    Retrieves and categorizes available matplotlib colormaps, then plots them
    by category for visual inspection.

    This function fetches all registered colormaps in matplotlib, categorizes
    them based on common usage (perceptually uniform, sequential, diverging,
    qualitative, miscellaneous), and then uses `plot_colormaps` to display
    each category in separate figure windows.

    Returns:
        list[str]: A sorted list of all available colormap names.
    """
    # Create a simple gradient to display the colormaps

    gradient = np.linspace(0, 1, 256)
    gradient = np.vstack((gradient, gradient))

    # Get all available colormaps
    all_cmaps = sorted(mpl.colormaps)

    # Categorize colormaps (as per Matplotlib documentation)
    perceptually_uniform_cmaps = [
        "viridis",
        "plasma",
        "inferno",
        "magma",
        "cividis",
        "rocket",
        "mako",
        "turbo",
    ]
    sequential_cmaps = [
        cm
        for cm in all_cmaps
        if cm.startswith(
            (
                "Blues",
                "BuGn",
                "BuPu",
                "GnBu",
                "Greens",
                "Greys",
                "Oranges",
                "OrRd",
                "PuBu",
                "PuBuGn",
                "PuRd",
                "Purples",
                "RdPu",
                "Reds",
                "YlGn",
                "YlGnBu",
                "YlOrBr",
                "YlOrRd",
            )
        )
        and cm not in perceptually_uniform_cmaps
    ]
    sequential_2_cmaps = [
        "autumn",
        "bone",
        "cool",
        "copper",
        "cubehelix",
        "flag",
        "gist_earth",
        "gist_gray",
        "gist_heat",
        "gist_ncar",
        "gist_rainbow",
        "gist_stern",
        "gray",
        "hot",
        "hsv",
        "jet",
        "nipy_spectral",
        "ocean",
        "pink",
        "rainbow",
        "spectral",
        "spring",
        "summer",
        "winter",
    ]
    diverging_cmaps = [
        "BrBG",
        "bwr",
        "coolwarm",
        "RdBu",
        "RdGy",
        "PuOr",
        "PRGn",
        "PiYG",
        "RdYlBu",
        "RdYlGn",
        "seismic",
        "twilight",
        "twilight_shifted",
    ]
    qualitative_cmaps = [
        "Accent",
        "Dark2",
        "Paired",
        "Pastel1",
        "Pastel2",
        "Set1",
        "Set2",
        "Set3",
        "tab10",
        "tab20",
        "tab20b",
        "tab20c",
    ]
    miscellaneous_cmaps = [
        cm
        for cm in all_cmaps
        if cm
        not in (
            perceptually_uniform_cmaps
            + sequential_cmaps
            + sequential_2_cmaps
            + diverging_cmaps
            + qualitative_cmaps
        )
    ]

    # Sort the lists to ensure consistent order
    perceptually_uniform_cmaps.sort()
    sequential_cmaps.sort()
    sequential_2_cmaps.sort()
    diverging_cmaps.sort()
    qualitative_cmaps.sort()
    miscellaneous_cmaps.sort()

    # Plot each category
    plot_colormaps(gradient, perceptually_uniform_cmaps, "Perceptually Uniform")
    plot_colormaps(gradient, sequential_cmaps, "Sequential (Part 1 - ColorBrewer)")
    plot_colormaps(gradient, sequential_2_cmaps, "Sequential (Part 2 - Other)")
    plot_colormaps(gradient, diverging_cmaps, "Diverging")
    plot_colormaps(gradient, qualitative_cmaps, "Qualitative")
    plot_colormaps(gradient, miscellaneous_cmaps, "Miscellaneous/Legacy")

    print("\nColormaps are displayed in separate windows based on their category.")
    return all_cmaps

class NpzReader(DataReader):
    """
    Class for reading .npz files containing spectrogram data.

    Inherits from fitburst.backend.generic.DataReader.

    Attributes:
        metadata (dict): Metadata associated with the data.
    """

    def __init__(self, fname):
        """
        Initializes the NpzReader with the given file and downsampling factor.

        Args:
            fname (str): Path to the .npz file.
        """

        self.fname = fname

        temp = np.load(fname, allow_pickle=True)
        self.metadata = temp["metadata"].tolist()
        temp.close()

        super().__init__(fname)
        self.load_data()

    def __repr__(self):
        """
        Returns a string representation of the NpzReader object.
        """

        return f"{self.__class__.__name__}(fname='{self.fname}')"

    def __str__(self):
        """
        Returns a string representation of the NpzReader object.
        """

        return f"(fname='{self.fname}')"


class NpzWriter(NpzReader):
    """
    Class for writing and manipulating .npz files containing spectrogram data.

    Inherits from NpzReader.

    Attributes:
        burst_parameters (dict): Parameters of the burst, such as amplitude,
                                 dispersion measure, scattering timescale, etc.
        metadata (dict): Metadata associated with the data.
        dm_index (int): Index for the dispersion measure parameter.
        scattering_index (int): Index for the scattering index parameter.
        spectral_index (int): Index for the spectral index parameter.
        ref_freq (float): Reference frequency for spectral index calculations.
    """

    def_amplitude = 1
    def_arrival_time = 0
    def_burst_width = 0.0001
    def_dm = 0
    def_dm_index = -2
    def_ref_freq = 400
    def_scattering_index = -4
    def_scattering_timescale = 0.0001
    def_spectral_index = 0
    def_spectral_running = 0

    def __init__(self, file_or_reader=None):
        """
        Initializes the NpzWriter with the given .npz file.

        Args:
            file_or_reader (str or NpzReader): Path to the .npz file or NpzReader made for file
        """
        if file_or_reader is None:
            self._making_new_file = True
            self.metadata = {
                "bad_chans": [],
                "freqs_bin0": 0,
                "times_bin0": 0,
                "is_dedispersed": True,
                "num_freq": 0,
                "num_time": 0,
                "res_freq": 0,
                "res_time": 0,
            }

            self.burst_parameters = {
                "amplitude": [self.def_amplitude],
                "arrival_time": [self.def_arrival_time],
                "burst_width": [self.def_burst_width],
                "dm": [self.def_dm],
                "dm_index": [self.def_dm_index],
                "ref_freq": [self.def_ref_freq],
                "scattering_index": [self.def_scattering_index],
                "scattering_timescale": [self.def_scattering_timescale],
                "spectral_index": [self.def_spectral_index],
                "spectral_running": [self.def_spectral_running],
            }
            logger.warning(f"Please use function .set_data to setup the data.")
        else:
            self._making_new_file = False

        if type(file_or_reader) == str:
            self.fname = file_or_reader

            temp = np.load(file_or_reader, allow_pickle=True)
            self.metadata = temp["metadata"].tolist()
            temp.close()

            super().__init__(file_or_reader)
            self.load_data()

        if type(file_or_reader) == NpzReader:
            self.fname = file_or_reader.fname

            temp = np.load(self.fname, allow_pickle=True)
            self.metadata = temp["metadata"].tolist()
            temp.close()

            super().__init__(file_or_reader.fname)
            self.load_data()

    def set_data(self, data, times, freqs, time_res, freq_res, bad_chans=[]):
        """
        Sets the data and metadata for a new .npz file.

        Args:
            data (np.ndarray): The spectrogram data (frequency x time).
            times (np.ndarray): Array of time values for each time sample.
            freqs (np.ndarray): Array of frequency values for each channel.
            time_res (float): Time resolution of the data.
            freq_res (float): Frequency resolution of the data.
            bad_chans (list, optional): List of indices of bad frequency channels.
                                       Defaults to [].
        """
        if not self._making_new_file:
            raise RuntimeError(
                "This function can only be used when creating a new file."
            )

        if type(data) != np.ndarray:
            data = np.array(data)
        self.data_full = data
        self.metadata["num_freq"] = self.data_full.shape[0]
        self.metadata["num_time"] = self.data_full.shape[1]
        if len(times) != self.metadata["num_time"]:
            raise AssertionError(
                f"Data shape does not match metadata. {len(times)} != {self.metadata['num_time']}"
            )

        if len(freqs) != self.metadata["num_freq"]:
            raise AssertionError(
                f"Data shape does not match metadata. {len(freqs)} != {self.metadata['num_freq']}"
            )

        self.metadata["bad_chans"] = bad_chans
        self.metadata["freqs_bin0"] = freqs[0]
        self.metadata["times_bin0"] = times[0]
        self.metadata["res_freq"] = freq_res
        self.metadata["res_time"] = time_res

        self.times = times
        self.freqs = freqs
        self.res_time = time_res
        self.res_freq = freq_res

        self.num_freq = self.data_full.shape[0]
        self.num_time = self.data_full.shape[1]

        self.data_weights = np.ones((self.num_freq, self.num_time), dtype=float)
        self.data_weights[bad_chans, :] = 0

        self.data_loaded = True

    def remove_baseline(self, percent, step=0.05, verbose=False, cutoff=0.3):
        """
        Removes baseline from the start and end of the data based on SNR.

        Iteratively reduces the percentage of data considered from the start
        and end until the SNR in those regions falls below a cutoff threshold.
        The arrival time parameter in burst_parameters is adjusted accordingly.

        Args:
            percent (float): Initial percentage of data from the start and end
                             to consider for baseline removal (between 0 and 1).
            step (float, optional): The step size by which the percentage is
                                    reduced in each iteration. Defaults to 0.05.
            verbose (bool, optional): If True, prints intermediate SNR values
                                      and percentages during the process.
                                      Defaults to False.
            cutoff (float, optional): The SNR threshold below which a region
                                      is considered baseline and removed.
                                      Defaults to 0.3.

        Raises:
            RuntimeError: If the NpzWriter is set to create a new file but
                          data has not been loaded using .set_data().
        """

        if self._making_new_file and not self.data_loaded:
            raise RuntimeError("Please use function .set_data to setup the data.")

        data_start = self.data_full[:, 0 : int(percent * len(self.times))]
        data_end = self.data_full[:, -int(percent * len(self.times)) :]

        ts_start = np.sum(data_start, 0)
        ts_end = np.sum(data_end, 0)

        snr_start = self.__calculate_snr(ts_start)
        snr_end = self.__calculate_snr(ts_end)

        if verbose:
            print(f"Cutoff: {cutoff}")
            print("Current SNRs:")
            print(snr_start, snr_end)
            print("Current percent: ", percent)
            print("")

        start_done = False
        end_done = False

        while True:
            percent -= np.abs(step)
            if percent < 0:
                break

            if not start_done:
                data_start = self.data_full[:, 0 : int(percent * len(self.times))]
                ts_start = np.sum(data_start, 0)
                snr_start = self.__calculate_snr(ts_start)
            if not end_done:
                data_end = self.data_full[:, -int(percent * len(self.times)) :]
                ts_end = np.sum(data_end, 0)
                snr_end = self.__calculate_snr(ts_end)

            if verbose:
                print("Current SNRs:")
                print(snr_start, snr_end)
                print("Current percent: ", percent)
                print("")

            if start_done and end_done:
                break
            if snr_start > cutoff and snr_end > cutoff:
                continue
            elif snr_end <= cutoff and not end_done:  # Cutting the end of the data
                final_end_percent = percent
                end_done = True
            elif (
                snr_start <= cutoff and not start_done
            ):  # Cutting the start of the data
                final_start_percent = percent
                start_done = True
            else:
                continue

        if not start_done:
            final_start_percent = 0

        # Move the arrival time:
        toa = np.array(self.burst_parameters["arrival_time"], dtype=float)
        toa -= (final_start_percent * len(self.times)) * self.res_time
        self.burst_parameters["arrival_time"] = toa.tolist()

        if end_done:
            self.data_full = self.data_full[
                :,
                int(final_start_percent * len(self.times)) : -int(
                    final_end_percent * len(self.times)
                ),
            ]
        else:
            self.data_full = self.data_full[
                :, int(final_start_percent * len(self.times)) :
            ]

        self.times = np.arange(self.data_full.shape[1]) * self.res_time

        self.metadata["num_time"] = self.data_full.shape[1]
        self.num_time = self.data_full.shape[1]

    def __calculate_snr(self, array):
        return np.mean(array) / np.std(array)

    def update_burst_parameters(self, **kwargs):
        """
        Updates the burst parameters with the provided keyword arguments.

        Args:
            **kwargs: Keyword arguments representing burst parameters to update.
                      Possible keys include:
                      - 'amplitude': Amplitude of the burst.
                      - 'dm': Dispersion measure of the burst.
                      - 'scattering_timescale': Scattering timescale of the burst.
                      - 'arrival_time': Arrival time of the burst.
                      - 'burst_width': Intrinsic width of the burst.
                      - 'spectral_running': Spectral index of the burst.
        """
        if self._making_new_file and not self.data_loaded:
            raise RuntimeError("Please use function .set_data to setup the data.")

        if "arrival_time" not in kwargs:
            raise KeyError(
                f"Cannot update parameters if number of ToAs is not provided. Please use the key 'arrival_time'."
            )

        number_of_components = len(kwargs["arrival_time"])

        for param in self.burst_parameters:
            if param in kwargs:
                if type(kwargs[param]) == np.ndarray:
                    kwargs[param] = kwargs[param].tolist()
                if len(kwargs[param]) != number_of_components:
                    raise ValueError(
                        f"Unexpected length of {len(kwargs[param])} for parameter {param} when {number_of_components} expected."
                    )

                self.burst_parameters[param] = kwargs[
                    param
                ]  # Safely put the kwargs' data into the burst parameters
            else:
                if type(self.burst_parameters[param]) != list:
                    self.burst_parameters[param] = [
                        self.burst_parameters[param]
                    ] * number_of_components
                else:
                    if len(self.burst_parameters[param]) != number_of_components:
                        temp = set(self.burst_parameters[param])
                        if len(temp) == 1:  # One parameter repeated
                            self.burst_parameters[param] = [
                                self.burst_parameters[param][-1]
                            ] * number_of_components

                        if (
                            len(temp) > number_of_components
                        ):  # More parameters than components -> clip results
                            self.burst_parameters[param] = self.burst_parameters[param][
                                :number_of_components
                            ]

                        if len(temp) < number_of_components:
                            logger.warning(
                                f"Using default value {getattr(self, f'def_{param}',0)} for parameter {param} to increase to {number_of_components} components."
                            )
                            self.burst_parameters[param] += [
                                getattr(self, f"def_{param}")
                            ] * (
                                number_of_components - len(self.burst_parameters[param])
                            )

    def save(self, new_filepath: str):
        """
        Saves the processed data and burst parameters to a new .npz file.

        Args:
            new_filepath (str): Path to the new .npz file where the data
                                will be saved.
        """
        if self._making_new_file and not self.data_loaded:
            raise RuntimeError("Please use function .set_data to setup the data.")

        print(f"Saving file at {new_filepath}...")

        with open(new_filepath, "wb") as f:
            np.savez(
                f,
                data_full=self.data_full,
                burst_parameters=self.burst_parameters,
                metadata=self.metadata,
            )
        print(f"Saved file at {new_filepath} successfully.")


class Peaks:
    """
    Class to hold results from OS-CFAR.

    Attributes:
        peaks (np.array): First half of the OS-CFAR results containing the peaks resulting from the algorithm.
        threshold (np.array): Second half of the OS-CFAR results containing the threshold used by the algorithm.
    """

    def __init__(self, oscfar_result):
        """
        Initializes the Peaks object with the result from OS-CFAR.

        Args:
            oscfar_result (tuple): A tuple containing the detected peak indices
                                   and the threshold array.
        """

        self.peaks = np.array(oscfar_result[0])
        self.threshold = np.array(oscfar_result[1])


class WaterFallImage:
    """
    Base class for creating matplotlib figures and axes for waterfall plots.

    Provides basic functionality for changing figure size, showing, and saving plots.
    Intended to be inherited by classes that create specific plot layouts.

    Attributes:
        cmap (str): The default colormap to use for the spectrogram image.
                    Defaults to 'gist_yarg'.
    """

    cmap = "gist_yarg"

    def __init__(self):
        pass

    def change_size(self, width, height):
        """
        Changes the size of the figure containing the axes.

        Args:
            width (float): The new width of the figure in inches.
            height (float): The new height of the figure in inches.
        """

        plt.gcf().set_size_inches(width, height)

    def show(self, block=None):
        """
        Displays the plot.

        Args:
            block (bool, optional): Whether to block the execution until the
                                    plot window is closed. Defaults to None,
                                    which uses the matplotlib default.
        """

        plt.show(block)

    def save(self, fname):
        """
        Saves the current plot to a file.

        Args:
            fname (str): The filename (including path and extension) to save the plot to.
        """

        plt.savefig(fname)
        print("Image saved successfully.")


class WaterFallAxes(WaterFallImage):
    """
    Class to create matplotlib axes for a single waterfall plot, including
    optional time series and spectrum plots.

    Inherits from WaterFallImage.

    Attributes:
        im (matplotlib.axes.Axes): Axes object for the main spectrogram image.
        ts (matplotlib.axes.Axes or None): Axes object for the time series plot,
                                           or None if show_ts is False.
        spec (matplotlib.axes.Axes or None): Axes object for the spectrum plot,
                                            or None if show_spec is False.
        show_ts (bool): Whether the time series plot is included.
        show_spec (bool): Whether the spectrum plot is included.
        _data (NpzReader or None): Stores the data reader object after plotting.
        _time_series (np.ndarray or None): Stores the summed time series after plotting.
        _freq_series (np.ndarray or None): Stores the summed frequency series after plotting.
    """

    def __init__(
        self,
        width: float = 0.75,
        height: float = 0.75,
        bottom: float = 0.1,
        left: float = None,
        hratio: float = 1,
        vratio: float = 1,
        show_ts=True,
        show_spec=True,
        labels_on=[True, True],
    ):
        """
        Initializes the WaterFallAxes object.

        Args:
            width (float): Width of the main spectrogram plot. Defaults to 0.75.
            height (float): Height of the main spectrogram plot. Defaults to 0.75.
            bottom (float): Bottom position of the main spectrogram plot.
            left (float, optional): Left position of the main spectrogram plot.
                                    Defaults to the value of 'bottom'.
            hratio (float, optional): Horizontal ratio for plot dimensions. Defaults to 1.
            vratio (float, optional): Vertical ratio for plot dimensions. Defaults to 1.
            show_ts (bool, optional): Whether to show the time series plot. Defaults to True.
            show_spec (bool, optional): Whether to show the spectrum plot. Defaults to True.
            labels_on (list, optional): List of two booleans indicating whether to
                                        show labels on the x and y axes, respectively.
                                        Defaults to [True, True].
        """
        super().__init__()

        self.show_ts = show_ts
        self.show_spec = show_spec

        if labels_on[0] or labels_on[1]:
            width = 0.6
            height = 0.6

        bot = bottom
        if left is None:
            left = bot

        im_w = width / hratio
        im_h = height / vratio

        self.im = plt.axes((left, bot, im_w, im_h))
        if self.show_ts:
            self.ts = plt.axes((left, im_h + bot, im_w, 0.2 / vratio), sharex=self.im)

        if self.show_spec:
            self.spec = plt.axes((im_w + left, bot, 0.2 / hratio, im_h), sharey=self.im)

        if labels_on[0] or labels_on[1]:
            if labels_on[0]:
                self.im.set_xlabel("Time (s)")
            if labels_on[1]:
                self.im.set_ylabel("Observing frequency (MHz)")
        else:
            plt.setp(self.im.get_xticklabels(), visible=False)
            plt.setp(self.im.get_xticklines(), visible=False)
            plt.setp(self.im.get_yticklabels(), visible=False)
            plt.setp(self.im.get_yticklines(), visible=False)

        if self.show_ts:
            plt.setp(self.ts.get_xticklabels(), visible=False)
            plt.setp(self.ts.get_xticklines(), visible=False)
            plt.setp(self.ts.get_yticklabels(), visible=False)
            plt.setp(self.ts.get_yticklines(), visible=False)
        if self.show_spec:
            plt.setp(self.spec.get_xticklabels(), visible=False)
            plt.setp(self.spec.get_xticklines(), visible=False)
            plt.setp(self.spec.get_yticklabels(), visible=False)
            plt.setp(self.spec.get_yticklines(), visible=False)

    def plot(self, data: NpzReader, title="", readjust_title=0, vmin=None, vmax=None):
        """
        Plots the spectrogram, time series, and spectrum on the created axes.

        Args:
            data (NpzReader): DataReader object containing the spectrogram data.
            title (str, optional): Title of the plot. Defaults to "".
            readjust_title (int, optional): Vertical adjustment for the title position. Defaults to 0.
            vmin (int, optional): Minimum value for the colormap
            max (int, optional): Maximum value for the colormap
        """
        self._data = data  # Store data for later use (e.g., in plot_time_peaks)

        self._time_series = np.sum(data.data_full, 0)
        self._freq_series = np.sum(data.data_full, 1)

        if vmin is None:
            vmin = np.median(data.data_full) - np.std(data.data_full) * 4
        if vmax is None:
            vmax = np.median(data.data_full) + np.std(data.data_full) * 4

        self.im.imshow(
            data.data_full,
            cmap=self.cmap,
            aspect="auto",
            origin="lower",
            extent=[
                data.times[0],
                data.times[-1],
                data.freqs[0],
                data.freqs[-1],
            ],
            vmin=vmin,
            vmax=vmax
        )
        if self.show_ts:
            self.ts.plot(data.times, self._time_series)
            plt.text(
                1,  # - len(title) * 0.025,
                0.85 - readjust_title,
                title,
                transform=self.ts.transAxes,
                ha="right",
                va="bottom",
            )

        if self.show_spec:
            self.spec.plot(self._freq_series, data.freqs)

    def plot_time_peaks(self, peaks: Peaks, color, show_thres=False):
        """
        Plots vertical lines on the spectrogram at the time indices of the detected peaks.
        Also plots the peaks on the time series plot if it is shown.

        Args:
            peaks (Peaks): An object containing the peak indices and threshold.
            color (str): Color for the vertical lines and scatter points.
            show_thres (bool): Whether to show the threshold on the time series plot.
        """
        if getattr(self, "_data", None) is None:
            raise Exception(
                "Cannot plot the time series' peaks without the data. Please use '.plot(data) first."
            )

        if peaks is None:
            return

        if type(peaks) == Peaks:
            if peaks.peaks is None or len(peaks.peaks) == 0:
                return

        for x in peaks.peaks:
            self.im.axvline(self._data.times[x], color=color, linestyle="--", alpha=0.5)

        if self.show_ts:
            self.ts.scatter(
                self._data.times[peaks.peaks],
                self._time_series[peaks.peaks],
                marker="o",
                color=color,
                zorder=10,
            )

        if show_thres:
            self.ts.plot(self._data.times, peaks.threshold, c="grey", linestyle="--")


class WaterFallGrid(WaterFallImage):
    """
    Class to create a grid of waterfall plots (spectrograms) with associated time series and spectra.

    Inherits from WaterFallImage.

    Attributes:
        nrows (int): Number of rows in the grid.
        ncols (int): Number of columns in the grid.
        axes (np.ndarray): A 2D array of WaterFallAxes objects, representing
                           each subplot in the grid.
        vs (float): Vertical spacing between plots.
        hs (float): Horizontal spacing between plots.
    """

    def __init__(self, nrows: int, ncols: int, vspacing=0.1, hspacing=0.1):
        """
        Initializes the WaterFallGrid object.

        Args:
            nrows (int): Number of rows in the grid.
            ncols (int): Number of columns in the grid.
            vspacing (float, optional): Vertical spacing between plots. Defaults to 0.1.
            hspacing (float, optional): Horizontal spacing between plots. Defaults to 0.1.
        """

        super().__init__()

        self.nrows = nrows
        self.ncols = ncols
        self.axes = np.zeros((nrows, ncols), dtype=object)
        self.vs = vspacing
        self.hs = hspacing

    def plot(
        self,
        data: list,
        peaks: list,
        titles: list,
        color,
        labels=[True, False],
        adjust_t=0,
        show_thres=False,
    ):
        """
        Plots the waterfall grid with the provided data, peaks, and titles.

        Args:
            data (list): List of DataReader objects, one for each subplot.
            peaks (list): List of Peaks objects, one for each subplot.
            titles (list): List of titles for each subplot.
            color (str): Color for the peak markers.
            labels (list, optional): List of two booleans indicating whether to
                                     show labels on the x and y axes, respectively.
                                     Defaults to [True, False].
            adjust_t (int, optional): Vertical adjustment for the title position. Defaults to 0.
            show_thres (bool): Whether to show the threshold on the time series plot.
        """

        if type(data) == list or type(peaks) == list or type(titles) == list:
            data = np.array(data).reshape((self.nrows, self.ncols))
            peaks = np.array(peaks).reshape((self.nrows, self.ncols))
            titles = np.array(titles).reshape((self.nrows, self.ncols))

        lefts = np.arange(0, 1, 1 / (self.ncols)) + self.hs
        bottoms = np.arange(0, 1, 1 / (self.nrows)) + self.vs
        for i in range(self.nrows):
            for j in range(self.ncols):
                ax = WaterFallAxes(
                    0.75,
                    0.75,
                    bottoms[i],
                    left=lefts[j],
                    hratio=self.ncols,
                    vratio=self.nrows,
                    show_ts=True,
                    show_spec=True,
                    labels_on=labels,
                )
                ax.plot(
                    data[i, j],
                    title=titles[i, j],
                    readjust_title=adjust_t,
                )
                ax.plot_time_peaks(peaks[i, j], color, show_thres)
                self.axes[i, j] = ax

    def add_info(self, info: pd.DataFrame):
        """
        Adds a table with additional information below the grid.

        Args:
            info (pd.DataFrame): DataFrame containing the information to be displayed.
        """

        ax = plt.axes((0, 0, 1, self.vs - 0.1))
        plt.setp(ax.get_xticklabels(), visible=False)
        plt.setp(ax.get_yticklabels(), visible=False)
        plt.setp(ax.get_xticklines(), visible=False)
        plt.setp(ax.get_yticklines(), visible=False)

        table = ax.table(
            info.values,
            colLabels=info.columns,
            rowLabels=info.index,
            loc="bottom",
            cellLoc="center",
            rowLoc="center",
            bbox=[0, 0, 1, 1],
        )


class FitburstResultsReader:
    """
    Class to read and access results from a fitburst JSON output file.

    Attributes:
        filepath (str): Path to the fitburst JSON results file.
        results (dict): Dictionary containing the loaded JSON data.
        initial_dm (float): Initial DM used in the fit.
        initial_time (float): Initial time used in the fit.
        (various attributes): Attributes corresponding to keys in the
                              'fit_statistics' section of the JSON,
                              including best-fit parameters and their
                              uncertainties as `uncertainties.ufloat` objects.
    """

    def __init__(self, filepath: str):
        """
        Initializes the FitburstResultsReader with the path to the JSON results file.

        Args:
            filepath (str): Path to the JSON file containing fitburst results.
        """

        self.filepath = filepath

        with open(self.filepath, "r") as f:
            self.results = json.load(f)

        self.initial_dm = self.results["initial_dm"]
        self.initial_time = self.results["initial_time"]

        fit_statistics = self.results["fit_statistics"]

        for key, data in fit_statistics.items():
            if key in ["bestfit_parameters", "bestfit_uncertainties"]:
                continue
            setattr(self, key, data)

        for param in fit_statistics["bestfit_parameters"]:
            if len(fit_statistics["bestfit_parameters"][param]) == 1:
                setattr(
                    self,
                    param,
                    ufloat(
                        fit_statistics["bestfit_parameters"][param][0],
                        fit_statistics["bestfit_uncertainties"][param][0],
                    ),
                )

            else:
                ufloats = [
                    ufloat(value, uncertainty)
                    for value, uncertainty in zip(
                        fit_statistics["bestfit_parameters"][param],
                        fit_statistics["bestfit_uncertainties"][param],
                    )
                ]
                setattr(self, param, ufloats)

    def get_fit_statistics(self):
        """
        Returns the 'fit_statistics' section of the fitburst results.

        Returns:
            dict: A dictionary containing fit statistics.
        """

        return self.results["fit_statistics"]

    def get_model_parameters(self):
        """
        Returns the 'model_parameters' section of the fitburst results.

        Returns:
            dict: A dictionary containing model parameters.
        """

        return self.results["model_parameters"]

    def get_fit_logistics(self):
        """
        Returns the 'fit_logistics' section of the fitburst results.

        Returns:
            dict: A dictionary containing fit logistics.
        """

        return self.results["fit_logistics"]


class FitburstResultsWriter:
    """
    Class to write and save results from a fitburst LSFitter object to a JSON file.

    Attributes:
        info (LSFitter): The LSFitter object containing the fit results.
    """

    def __init__(self, info: LSFitter):
        """
        Initializes the FitburstResultsWriter with an LSFitter object.

        Args:
            info (LSFitter): An instance of the LSFitter class containing the
                             results of a fitburst analysis.
        """

        self.info = info

    def get_fit_statistics(self):
        """
        Returns the 'fit_statistics' section from the LSFitter object.

        Returns:
            dict: A dictionary containing fit statistics.
        """

        return self.info.fit_statistics

    def get_model_parameters(self):
        """
        Returns the 'model_parameters' section from the LSFitter object's model.

        Returns:
            dict: A dictionary containing model parameters.
        """

        return self.info.model.get_parameters_dict()

    def get_fit_logistics(self):
        """
        Returns the 'fit_logistics' section from the LSFitter object.

        Returns:
            dict: A dictionary containing fit logistics.
        """

        return {"weight_range": self.info.weight_range}

    def save(self, filepath: str):
        """
        Saves the fitburst results to a JSON file.

        Args:
            filepath (str): The path to the JSON file where the results will be saved.
        """

        with open(filepath, "w") as f:
            json.dump(
                make_json_serializable(
                    {
                        "initial_dm": self.info.model.dm_incoherent,
                        "initial_time": self.info.model.times[0],
                        "fit_statistics": self.get_fit_statistics(),
                        "model_parameters": self.get_model_parameters(),
                        "fit_logistics": self.get_fit_logistics(),
                    }
                ),
                f,
                indent=4,
            )


def make_json_serializable(obj):
    """
    Recursively converts non-JSON serializable objects (primarily NumPy arrays)
    within a data structure to their JSON serializable equivalents.

    Args:
        obj: The object to convert. This can be a NumPy array,
             a dictionary, a list, or any other JSON serializable type.

    Returns:
        A new object with NumPy arrays converted to lists,
        suitable for JSON serialization.
    """
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: make_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [make_json_serializable(item) for item in obj]
    elif isinstance(
        obj,
        (
            np.bool_,
            np.int_,
            np.intc,
            np.intp,
            np.int8,
            np.int16,
            np.int32,
            np.int64,
            np.uint8,
            np.uint16,
            np.uint32,
            np.uint64,
            np.float16,
            np.float32,
            np.float64,
        ),
    ):
        return obj.item()  # Convert numpy scalar types to native python types
    else:
        return obj
