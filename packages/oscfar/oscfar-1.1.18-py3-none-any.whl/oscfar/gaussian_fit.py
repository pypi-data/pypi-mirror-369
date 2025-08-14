import numpy as np
from scipy.optimize import curve_fit
import itertools  # Added for combinations
from scipy.special import erfcx  # For the scattered Gaussian


def sum_of_gaussians(x, *params):
    """
    Calculates the sum of multiple Gaussian functions.

    Each Gaussian is defined by its amplitude, mean, and standard deviation.
    The parameters for the Gaussians are provided in a flat list:
    [amp1, mean1, stddev1, amp2, mean2, stddev2, ..., ampN, meanN, stddevN]

    Args:
        x (np.array):
            The independent variable where the functions are calculated.
        *params (list or np.array):
            A variable number of arguments representing the parameters.
            The total number of parameters must be a multiple of 3.
            - amp: Amplitude of the Gaussian.
            - mean: Mean (center) of the Gaussian.
            - stddev: Standard deviation (width) of the Gaussian.

    Returns:
        y (np.array):
            The sum of the Gaussian functions evaluated at x.

    Raises:
        ValueError: If the number of parameters in `params` is not a multiple of 3.
    """

    if not params or len(params) % 3 != 0:
        raise ValueError(
            "The number of parameters must be a multiple of 3 "
            "(amplitude, mean, stddev for each Gaussian)."
        )

    # Ensure x is a numpy array for vectorized operations and y is float
    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)

    num_gaussians = len(params) // 3

    for i in range(num_gaussians):
        amp = params[i * 3]
        mean = params[i * 3 + 1]
        stddev = params[i * 3 + 2]

        # Standard deviation must be positive.
        # If curve_fit explores a non-positive stddev, return inf to penalize.
        # Using bounds with curve_fit is the preferred way to handle this.
        # if stddev <= 1e-9: # Avoid zero or negative stddev
        #     return np.full_like(x, np.inf)

        gaussian_component = amp * np.exp(-((x - mean) ** 2) / (2 * stddev**2))
        y += gaussian_component

    return y


def sum_of_scattered_gaussians(x, *params):
    """
    Calculates the sum of multiple scattered Gaussian functions.

    Each scattered Gaussian is defined by its amplitude, mean, standard deviation,
    and scattering timescale. The parameters for the scattered Gaussians are
    provided in a flat list:
    [amp1, mean1, sigma1, tau1, amp2, mean2, sigma2, tau2, ..., ampN, meanN, sigmaN, tauN]

    Args:
        x (np.array):
            The independent variable where the functions are calculated.
        *params (list or np.array):
            A variable number of arguments representing the parameters.
            The total number of parameters must be a multiple of 4.
            - amp: Amplitude of the scattered Gaussian.
            - mean: Mean (center) of the scattered Gaussian.
            - sigma: Standard deviation (width) of the Gaussian before scattering.
            - tau: Scattering timescale.

    Returns:
        y (np.array):
            The sum of the scattered Gaussian functions evaluated at x.

    Raises:
        ValueError: If the number of parameters in `params` is not a multiple of 4.
    """

    if not params or len(params) % 4 != 0:
        raise ValueError(
            "The number of parameters must be a multiple of 4 "
            "(amplitude, mean, sigma, tau for each scattered Gaussian)."
        )

    x = np.asarray(x, dtype=float)
    y = np.zeros_like(x)

    # Threshold below which tau is considered zero (use Gaussian)
    # This might need to be adjusted based on typical sigma values.
    tau_threshold = 1e-9  # Made it smaller, was 1e-7
    sigma_min_val = 1e-9  # Smallest allowed sigma to prevent division by zero
    num_components = len(params) // 4

    for i in range(num_components):
        amp = params[i * 4]
        mean = params[i * 4 + 1]
        sigma = params[i * 4 + 2]
        tau = params[i * 4 + 3]

        # Ensure sigma is at least a small positive number for numerical stability
        # curve_fit bounds should ideally enforce sigma_param > 0 and tau >= 0.
        # Ensure tau is also non-negative (bounds should handle this, but good for safety)
        safe_sigma = max(
            np.abs(sigma), sigma_min_val
        )  # Use abs(sigma) in case bounds allow negative
        safe_tau = max(tau, 0.0)  # Ensure tau is non-negative

        t_norm = x - mean
        # If tau is extremely small, or sigma is extremely small relative to tau,
        # it can lead to issues.
        if (
            safe_tau < tau_threshold or (safe_sigma / max(safe_tau, 1e-20)) > 1e8
        ):  # Added a ratio check
            # Scattering is negligible, use a standard Gaussian
            # safe_sigma**2 ensures the variance term is robust
            component = amp * np.exp(-(t_norm**2) / (2 * safe_sigma**2))
        else:
            # Use numerically stable EMG formulation with erfcx
            # B = (1/sqrt(2)) * (sigma/tau - (t - mean)/sigma)
            # Clip B_arg to prevent erfcx from overflowing.
            # erfcx(z) for z > ~26.5 for double precision can overflow exp(z^2) part.
            # erfcx(z) for z < ~-26.5 can also be very large.
            # Let's be a bit conservative with B_ARG_MAX_ABS
            B_ARG_MAX_ABS = 25.0

            # Calculate B_arg carefully
            term1_b_arg = safe_sigma / safe_tau
            term2_b_arg = t_norm / safe_sigma
            B_arg_unclipped = (1.0 / np.sqrt(2.0)) * (term1_b_arg - term2_b_arg)

            B_arg = np.clip(B_arg_unclipped, -B_ARG_MAX_ABS, B_ARG_MAX_ABS)

            # The prefactor (amp / (2.0 * tau)) can also be an issue if tau is tiny.
            # However, the (safe_sigma / max(safe_tau, 1e-20)) > 1e8 check above should help.
            prefactor = amp / (2.0 * safe_tau)  # safe_tau is already max(tau, 0.0)

            exp_term = np.exp(-0.5 * (t_norm / safe_sigma) ** 2)
            component = prefactor * erfcx(B_arg) * exp_term

        y += component

    return y


def find_best_multi_gaussian_fit(
    x_data, y_data, initial_flat_params, max_n_gaussians=None, y_err=None
):
    """
    Finds the best fit to the data using a sum of Gaussian functions.

    This function attempts to fit the data with a varying number of Gaussian
    components, up to a specified maximum. The best fit is determined by
    comparing the Bayesian Information Criterion (BIC) for each fit.

    Args:
        x_data (np.array): The independent variable where the data is measured.
        y_data (np.array): The dependent data to be fitted.
        initial_flat_params (list or np.array): A flat list of initial
                                                 parameters for Gaussian
                                                 components, ordered as
                                                 [amp1, mean1, sigma1, amp2, mean2, sigma2, ...].
                                                 Amplitudes can be positive or negative.
        max_n_gaussians (int, optional): The maximum number of Gaussian
                                         components to try. If None, it defaults
                                         to the number of components implied by
                                         `initial_flat_params`.
        y_err (list or np.array, optional): Error on y_data. If provided, it's used in
                                     `curve_fit` for weighted least squares.

    Returns:
        dict: A dictionary containing the results of the fitting process.
              The dictionary has two keys:
              - 'best_fit': A dictionary containing the results of the best fit
                            found (lowest BIC). It includes:
                            - 'n_components': The number of Gaussian components
                                              in the best fit.
                            - 'popt': The optimized parameters for the best fit.
                            - 'pcov': The estimated covariance of popt.
                            - 'bic': The Bayesian Information Criterion (BIC) for
                                     the best fit.
                            - 'rss': The Residual Sum of Squares for the best fit.
              - 'all_fits': A list of dictionaries, each containing the results
                            for a fit with a specific number of components.
                            Each dictionary in the list has the same structure
                            as 'best_fit', but for a different number of components.

    Raises:
        ValueError: If `initial_flat_params` is invalid (empty or not a multiple of 3), if `x_data` and `y_data` are empty or have different lengths.
    """

    x_data = np.asarray(x_data)
    y_data = np.asarray(y_data)

    if len(x_data) == 0 or len(y_data) == 0:
        raise ValueError("x_data and y_data must not be empty.")
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have the same length.")
    if not initial_flat_params or len(initial_flat_params) % 3 != 0:
        raise ValueError(
            "initial_flat_params must be non-empty and contain groups of 3 (amplitude, mean, sigma)."
        )

    num_initial_components = len(initial_flat_params) // 3
    parsed_initial_peaks = []
    for i in range(num_initial_components):
        amp, mean, sigma = initial_flat_params[i * 3 : (i + 1) * 3]
        parsed_initial_peaks.append(
            {"amp": amp, "mean": mean, "sigma": sigma, "params": [amp, mean, sigma]}
        )

    # Sort initial peaks by amplitude in descending order
    sorted_initial_peaks = sorted(
        parsed_initial_peaks, key=lambda p: p["amp"], reverse=True
    )

    if max_n_gaussians is None:
        max_n_gaussians = num_initial_components
    else:
        max_n_gaussians = min(max_n_gaussians, num_initial_components)

    if (
        max_n_gaussians == 0 and num_initial_components > 0
    ):  # if user sets max_n_gaussians=0 but there are peaks
        max_n_gaussians = num_initial_components
    elif (
        max_n_gaussians == 0 and num_initial_components == 0
    ):  # no peaks, no max_n_gaussians
        # This case should be caught by the initial_flat_params check earlier,
        # but as a safeguard:
        print(
            "Warning: No initial peaks provided and max_n_gaussians is 0. No fits will be attempted."
        )
        return {
            "best_fit": {"bic": np.inf, "popt": None, "n_components": 0, "rss": np.inf},
            "all_fits": [],
        }

    all_fits_results = []
    best_fit_result = {"bic": np.inf}

    # Define sensible bounds
    min_x, max_x = np.min(x_data), np.max(x_data)
    range_x = max_x - min_x
    if range_x == 0:
        range_x = 1.0  # Avoid division by zero if all x are same
    min_sigma = 1e-5  # A very small sigma
    max_sigma = range_x  # Max sigma can be the whole range

    # Amplitude bound: allow positive or negative, scaled by data range
    # Handle all-zero or constant y_data
    y_abs_max = np.max(np.abs(y_data)) if np.any(y_data) else 1.0
    amp_bound_abs = 2.0 * y_abs_max

    for n_gauss in range(1, max_n_gaussians + 1):
        if n_gauss > len(sorted_initial_peaks):
            break

        p0 = []
        current_bounds_lower = []
        current_bounds_upper = []

        for i in range(n_gauss):
            peak_info = sorted_initial_peaks[i]
            p0_amp = peak_info["amp"]
            p0_mean = np.clip(peak_info["mean"], min_x, max_x)
            p0_sigma = np.clip(peak_info["sigma"], min_sigma, max_sigma)

            p0.extend([p0_amp, p0_mean, p0_sigma])
            current_bounds_lower.extend([-amp_bound_abs, min_x, min_sigma])
            current_bounds_upper.extend([amp_bound_abs, max_x, max_sigma])

        bounds = (current_bounds_lower, current_bounds_upper)

        try:
            popt, pcov = curve_fit(
                sum_of_gaussians,
                x_data,
                y_data,
                p0=p0,
                bounds=bounds,
                sigma=y_err,
                absolute_sigma=y_err is not None,
                maxfev=5000 * (n_gauss * 3),
            )
            residuals = y_data - sum_of_gaussians(x_data, *popt)
            rss = np.sum(residuals**2)
            num_params = len(popt)
            n_points = len(x_data)

            bic = (
                n_points * np.log(max(rss, 1e-9) / n_points)
                + num_params * np.log(n_points)
                if n_points > num_params
                else np.inf
            )

            current_fit = {
                "n_components": n_gauss,
                "popt": popt,
                "pcov": pcov,
                "bic": bic,
                "rss": rss,
            }
            all_fits_results.append(current_fit)

            if bic < best_fit_result["bic"]:
                best_fit_result = current_fit
        except RuntimeError:
            # print(
            #     f"Warning: Optimal parameters not found for {n_gauss} Gaussian(s). Skipping."
            # )
            all_fits_results.append(
                {
                    "n_components": n_gauss,
                    "popt": None,
                    "pcov": None,
                    "bic": np.inf,
                    "rss": np.inf,
                }
            )
        except ValueError as e:
            # print(
            #     f"Warning: ValueError during fit for {n_gauss} Gaussian(s): {e}. Skipping."
            # )
            all_fits_results.append(
                {
                    "n_components": n_gauss,
                    "popt": None,
                    "pcov": None,
                    "bic": np.inf,
                    "rss": np.inf,
                }
            )

    if "popt" not in best_fit_result:
        best_fit_result = {
            "bic": np.inf,
            "popt": None,
            "n_components": 0,
            "rss": np.inf,
        }
        if all_fits_results:  # If some attempts were made but all failed
            # print("Warning: No successful fit found. Returning placeholder for best_fit.")
            pass  # No specific best_fit to return, placeholder is fine
        # else: # No attempts made (e.g. max_n_gaussians was 0 or no initial peaks)
        # print("Warning: No fits attempted.")

    return {"best_fit": best_fit_result, "all_fits": all_fits_results}


def _run_combinatorial_fit_for_model(
    x_data,
    y_data,
    initial_flat_params_3_per_peak,
    actual_max_n_components_to_try,
    y_err=None,
    max_initial_components_for_pool=None,
    model_type="gaussian",
    default_initial_tau=1e-4,
    common_bounds_config=None,
):
    """
    Internal helper to perform combinatorial grid search for a specific model type.
    """
    if common_bounds_config is None:
        raise ValueError("common_bounds_config must be provided.")

    min_x = common_bounds_config["min_x"]
    max_x = common_bounds_config["max_x"]
    min_sigma = common_bounds_config["min_sigma"]
    max_sigma_abs = common_bounds_config["max_sigma_abs"]
    abs_amp_bound = common_bounds_config["abs_amp_bound"]
    max_tau_abs = common_bounds_config["max_tau_abs"]

    num_total_initial_components = len(initial_flat_params_3_per_peak) // 3
    parsed_initial_peaks = []
    for i in range(num_total_initial_components):
        amp, mean, sigma = initial_flat_params_3_per_peak[i * 3 : (i + 1) * 3]
        parsed_initial_peaks.append(
            {"amp": amp, "mean": mean, "sigma": sigma}  # Store raw initial guesses
        )

    # Sort initial peaks by absolute amplitude in descending order
    sorted_initial_peaks = sorted(
        parsed_initial_peaks, key=lambda p: np.abs(p["amp"]), reverse=True
    )

    candidate_peaks_pool = sorted_initial_peaks
    if max_initial_components_for_pool is not None:
        candidate_peaks_pool = sorted_initial_peaks[:max_initial_components_for_pool]

    if not candidate_peaks_pool:
        # print(f"Warning: Candidate peak pool is empty for {model_type} model. No fits will be attempted.")
        return {
            "best_fit": {"bic": np.inf, "popt": None, "n_components": 0, "rss": np.inf},
            "all_fits": [],
        }

    num_peaks_in_pool = len(candidate_peaks_pool)
    all_fits_results = []
    overall_best_fit_result = {
        "bic": np.inf,
        "popt": None,
        "n_components": 0,
        "rss": np.inf,
    }

    fit_function = (
        sum_of_gaussians if model_type == "gaussian" else sum_of_scattered_gaussians
    )
    params_per_component = 3 if model_type == "gaussian" else 4

    # Iterate from 1 up to the minimum of allowed components and available unique peaks in the pool
    for n_components_to_fit in range(
        1, min(actual_max_n_components_to_try, num_peaks_in_pool) + 1
    ):
        best_fit_for_this_n_components = {"bic": np.inf, "popt": None, "rss": np.inf}

        for peak_combination in itertools.combinations(
            candidate_peaks_pool, n_components_to_fit
        ):
            p0 = []
            current_bounds_lower = []
            current_bounds_upper = []

            for peak_info in peak_combination:
                # Clip initial guesses to be within bounds
                p0_amp = peak_info["amp"]  # No clip for amp, bounds handle it
                p0_mean = np.clip(peak_info["mean"], min_x, max_x)
                p0_sigma = np.clip(peak_info["sigma"], min_sigma, max_sigma_abs)

                current_p0_component_params = [p0_amp, p0_mean, p0_sigma]
                current_bounds_lower.extend([-abs_amp_bound, min_x, min_sigma])
                current_bounds_upper.extend([abs_amp_bound, max_x, max_sigma_abs])

                if model_type == "scattered":
                    p0_tau = np.clip(
                        default_initial_tau, 0, max_tau_abs
                    )  # Ensure tau is non-negative
                    current_p0_component_params.append(p0_tau)
                    current_bounds_lower.append(0)  # min_tau
                    current_bounds_upper.append(max_tau_abs)  # max_tau

                p0.extend(current_p0_component_params)

            bounds = (current_bounds_lower, current_bounds_upper)

            try:
                popt, pcov = curve_fit(
                    fit_function,
                    x_data,
                    y_data,
                    p0=p0,
                    bounds=bounds,
                    sigma=y_err,
                    absolute_sigma=y_err is not None,
                    maxfev=5000 * (n_components_to_fit * params_per_component),
                )
                residuals = y_data - fit_function(
                    x_data, *popt
                )  # Corrected to use fit_function
                rss = np.sum(residuals**2)
                num_params = len(popt)
                n_points = len(x_data)

                bic = (
                    n_points * np.log(max(rss, 1e-9) / n_points)
                    + num_params * np.log(n_points)
                    if n_points > num_params
                    else np.inf
                )

                if bic < best_fit_for_this_n_components["bic"]:
                    best_fit_for_this_n_components = {
                        "n_components": n_components_to_fit,
                        "popt": popt,
                        "pcov": pcov,
                        "bic": bic,
                        "rss": rss,
                    }
            except (RuntimeError, ValueError):
                pass

        if best_fit_for_this_n_components["popt"] is not None:
            all_fits_results.append(best_fit_for_this_n_components)
            if best_fit_for_this_n_components["bic"] < overall_best_fit_result["bic"]:
                overall_best_fit_result = best_fit_for_this_n_components
        else:
            all_fits_results.append(
                {
                    "n_components": n_components_to_fit,
                    "popt": None,
                    "pcov": None,
                    "bic": np.inf,
                    "rss": np.inf,
                }
            )

    return {"best_fit": overall_best_fit_result, "all_fits": all_fits_results}


def _process_model_fit(args):
    (
        x_data,
        y_data,
        initial_flat_params,
        max_n_gaussians,
        y_err,
        max_initial_components_for_pool,
        model_to_test,
        default_initial_tau,
        max_tau_bound_factor,
    ) = args
    """
    Performs a grid search to find the best multi-component fit by trying
    different numbers of components, different combinations of initial peak
    guesses, and optionally different model types (Gaussian or Scattered Gaussian).

    The function iterates from 1 to `max_n_gaussians`. For each number of
    components `k`, it tries all combinations of `k` peaks chosen from a
    pool of initial guesses. This pool is derived from `initial_flat_params`
    (sorted by absolute amplitude), potentially limited by
    `max_initial_components_for_pool`.

    The best fit is selected based on the Bayesian Information Criterion (BIC).

    Args:
        x_data (np.array):
            The independent variable where the data is measured.
        y_data (np.array):
            The dependent data.
        initial_flat_params (list or np.array): 
            A flat list of initial parameters for Gaussian components, ordered as
            [amp1, mean1, sigma1, amp2, mean2, sigma2, ...]. Amplitudes can be
            positive or negative.
        max_n_gaussians (int, optional):
            The maximum number of components to try in a single model.
            If None, it defaults to the number of components in `initial_flat_params`.
        y_err (list or np.array, optional): 
            Error on y_data. If provided, it's used in `curve_fit` for weighted
            least squares.
        max_initial_components_for_pool (int, optional):
            The maximum number of initial components (selected by highest absolute
            amplitude from `initial_flat_params`) to include in the pool from which
            combinations are drawn. If None, all components from
            `initial_flat_params` are used.
        model_to_test (str, optional): 
            Specifies which model(s) to test:
            - "gaussian": Only fit `sum_of_gaussians`.
            - "scattered": Only fit `sum_of_scattered_gaussians`.
            - "both": Fit both models and choose the overall best.
            Defaults to "gaussian".
        default_initial_tau (float, optional):
            Initial guess for the scattering timescale (tau) if `model_to_test`
            involves "scattered" model. Defaults to 1e-4.
        max_tau_bound_factor (float, optional):
            Factor to multiply by the range of x_data to set the upper bound for tau.
            Defaults to 1.0. If 0, tau will be fixed at 0 for scattered model (effectively Gaussian).

    Returns:
        dict: A dictionary containing the results of the fitting process.
            If `model_to_test` is "gaussian" or "scattered":
            `{'best_fit': {'model_type': ..., ...}, 'all_fits': [...]}`
            If `model_to_test` is "both":
            `{'overall_best_fit': {'model_type': ..., ...},
                'gaussian_results': {'best_fit': ..., 'all_fits': ...},
                'scattered_results': {'best_fit': ..., 'all_fits': ...}}`
            The 'best_fit' dict contains 'n_components', 'popt', 'pcov', 'bic', 'rss'.

    Raises:
        ValueError: If `initial_flat_params` is invalid, data is empty/mismatched, or `model_to_test` is an invalid option.
    """
    x_data = np.asarray(x_data)
    y_data = np.asarray(y_data)

    if len(x_data) == 0 or len(y_data) == 0:
        raise ValueError("x_data and y_data must not be empty.")
    if len(x_data) != len(y_data):
        raise ValueError("x_data and y_data must have the same length.")
    if not initial_flat_params or len(initial_flat_params) % 3 != 0:
        raise ValueError(
            "initial_flat_params must be non-empty and contain groups of 3 (amplitude, mean, sigma)."
        )
    if model_to_test not in ["gaussian", "scattered", "both"]:
        raise ValueError("model_to_test must be 'gaussian', 'scattered', or 'both'.")

    min_x_val, max_x_val = np.min(x_data), np.max(x_data)
    range_x_val = max_x_val - min_x_val if max_x_val > min_x_val else 1.0
    min_sigma_val = 1e-5
    max_sigma_val = range_x_val  # Max sigma can be the whole range

    data_abs_max = np.max(np.abs(y_data)) if np.any(y_data) else 1.0
    abs_amp_bound_val = 2.0 * data_abs_max  # Allow amplitude to be +/- this value

    max_tau_abs_val = max(
        0.0, max_tau_bound_factor * range_x_val
    )  # Ensure tau bound is non-negative

    common_bounds_config = {
        "min_x": min_x_val,
        "max_x": max_x_val,
        "range_x": range_x_val,
        "min_sigma": min_sigma_val,
        "max_sigma_abs": max_sigma_val,
        "abs_amp_bound": abs_amp_bound_val,
        "max_tau_abs": max_tau_abs_val,
    }
    num_initial_components_available = len(initial_flat_params) // 3

    # Determine the maximum number of components to actually try fitting
    if max_n_gaussians is None:
        actual_max_n_components_to_try = num_initial_components_available
    else:
        actual_max_n_components_to_try = min(
            max_n_gaussians, num_initial_components_available
        )

    # If initial_flat_params is empty, num_initial_components_available will be 0.
    # actual_max_n_components_to_try will also be 0.
    # The helper function _run_combinatorial_fit_for_model handles empty candidate_peaks_pool.
    if actual_max_n_components_to_try == 0 and num_initial_components_available > 0:
        # This case implies max_n_gaussians was set to 0 by the user, but there are peaks.
        # We should respect user's max_n_gaussians=0, so actual_max_n_components_to_try remains 0.
        # The loops in _run_combinatorial_fit_for_model will not run.
        pass

    results_gaussian = None
    results_scattered = None

    run_gaussian = model_to_test == "gaussian" or model_to_test == "both"
    run_scattered = model_to_test == "scattered" or model_to_test == "both"

    if run_gaussian:
        results_gaussian = _run_combinatorial_fit_for_model(
            x_data,
            y_data,
            initial_flat_params,
            actual_max_n_components_to_try,
            y_err,
            max_initial_components_for_pool,
            "gaussian",
            default_initial_tau,
            common_bounds_config,
        )

        if results_gaussian and results_gaussian["best_fit"].get("popt") is not None:
            results_gaussian["best_fit"]["model_type"] = "gaussian"

    if run_scattered:
        results_scattered = _run_combinatorial_fit_for_model(
            x_data,
            y_data,
            initial_flat_params,
            actual_max_n_components_to_try,
            y_err,
            max_initial_components_for_pool,
            "scattered",
            default_initial_tau,
            common_bounds_config,
        )

        if results_scattered and results_scattered["best_fit"].get("popt") is not None:
            results_scattered["best_fit"]["model_type"] = "scattered"

    if model_to_test == "gaussian":
        if (
            results_gaussian is None
        ):  # Should not happen if logic is correct, but as safeguard
            return {
                "best_fit": {
                    "bic": np.inf,
                    "popt": None,
                    "n_components": 0,
                    "rss": np.inf,
                    "model_type": "gaussian",
                },
                "all_fits": [],
            }
        return results_gaussian
    elif model_to_test == "scattered":
        if results_scattered is None:
            return {
                "best_fit": {
                    "bic": np.inf,
                    "popt": None,
                    "n_components": 0,
                    "rss": np.inf,
                    "model_type": "scattered",
                },
                "all_fits": [],
            }
        return results_scattered
    elif model_to_test == "both":
        overall_best_fit = {
            "bic": np.inf,
            "popt": None,
            "n_components": 0,
            "rss": np.inf,
            "model_type": "none",
        }

        bic_g = (
            results_gaussian["best_fit"].get("bic", np.inf)
            if results_gaussian and results_gaussian.get("best_fit")
            else np.inf
        )
        popt_g_exists = (
            results_gaussian
            and results_gaussian.get("best_fit")
            and results_gaussian["best_fit"].get("popt") is not None
        )

        bic_s = (
            results_scattered["best_fit"].get("bic", np.inf)
            if results_scattered and results_scattered.get("best_fit")
            else np.inf
        )
        popt_s_exists = (
            results_scattered
            and results_scattered.get("best_fit")
            and results_scattered["best_fit"].get("popt") is not None
        )

        if popt_g_exists and popt_s_exists:
            if bic_g <= bic_s:
                overall_best_fit = results_gaussian["best_fit"]
            else:
                overall_best_fit = results_scattered["best_fit"]
        elif popt_g_exists:
            overall_best_fit = results_gaussian["best_fit"]
        elif popt_s_exists:
            overall_best_fit = results_scattered["best_fit"]
        # If neither popt_g_exists nor popt_s_exists, overall_best_fit remains the default placeholder

        return {
            "overall_best_fit": overall_best_fit,
            "gaussian_results": (
                results_gaussian
                if results_gaussian
                else {"best_fit": {"bic": np.inf, "popt": None}, "all_fits": []}
            ),
            "scattered_results": (
                results_scattered
                if results_scattered
                else {"best_fit": {"bic": np.inf, "popt": None}, "all_fits": []}
            ),
        }


def find_best_multi_gaussian_fit_combinatorial(
    x_data,
    y_data,
    initial_flat_params,
    max_n_gaussians=None,
    y_err=None,
    max_initial_components_for_pool=None,
    model_to_test="gaussian",
    default_initial_tau=1e-4,
    max_tau_bound_factor=1.0,
    use_multiprocessing=True,
    num_processes=None,
):
    """
    Performs a grid search to find the best multi-component fit by trying
    different numbers of components, different combinations of initial peak
    guesses, and optionally different model types (Gaussian or Scattered Gaussian).

    This version supports multiprocessing to speed up the fitting process.

    Args:
        (Same as the single-process version, plus the following:)
        use_multiprocessing (bool, optional):
            Whether to use multiprocessing. Defaults to True.
        num_processes (int, optional):
            The number of processes to use. If None, uses the number of CPU cores.

    Returns:
        (Same as the single-process version)

    Raises:
        (Same as the single-process version)
    """
    if not use_multiprocessing:
        return _process_model_fit(
            (
                x_data,
                y_data,
                initial_flat_params,
                max_n_gaussians,
                y_err,
                max_initial_components_for_pool,
                model_to_test,
                default_initial_tau,
                max_tau_bound_factor,
            )
        )

    import multiprocessing

    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    if num_processes <= 1:
        return _process_model_fit(
            (
                x_data,
                y_data,
                initial_flat_params,
                max_n_gaussians,
                y_err,
                max_initial_components_for_pool,
                model_to_test,
                default_initial_tau,
                max_tau_bound_factor,
            )
        )

    # Prepare arguments for multiprocessing
    args = (
        x_data,
        y_data,
        initial_flat_params,
        max_n_gaussians,
        y_err,
        max_initial_components_for_pool,
        model_to_test,
        default_initial_tau,
        max_tau_bound_factor,
    )

    if model_to_test in ["gaussian", "scattered"]:
        with multiprocessing.Pool(processes=num_processes) as pool:
            result = pool.apply(_process_model_fit, (args,))
        return result

    elif model_to_test == "both":
        # Split the work for Gaussian and Scattered models
        gaussian_args = (
            x_data,
            y_data,
            initial_flat_params,
            max_n_gaussians,
            y_err,
            max_initial_components_for_pool,
            "gaussian",
            default_initial_tau,
            max_tau_bound_factor,
        )
        scattered_args = (
            x_data,
            y_data,
            initial_flat_params,
            max_n_gaussians,
            y_err,
            max_initial_components_for_pool,
            "scattered",
            default_initial_tau,
            max_tau_bound_factor,
        )

        with multiprocessing.Pool(processes=num_processes) as pool:
            results = pool.starmap(
                _process_model_fit,
                [
                    (gaussian_args,),
                    (scattered_args,),
                ],
            )

        results_gaussian, results_scattered = results

        # Determine overall best fit
        overall_best_fit = {
            "bic": np.inf,
            "popt": None,
            "n_components": 0,
            "rss": np.inf,
            "model_type": "none",
        }
        if results_gaussian["best_fit"]["bic"] <= results_scattered["best_fit"]["bic"]:
            overall_best_fit = results_gaussian["best_fit"]
        else:
            overall_best_fit = results_scattered["best_fit"]

        return {
            "overall_best_fit": overall_best_fit,
            "gaussian_results": results_gaussian,
            "scattered_results": results_scattered,
        }

    else:
        raise ValueError("Invalid model_to_test value.")
