from statistics import NormalDist
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from scipy.stats import linregress


def calculate_density(norm: stats.norm, stdevs: np.ndarray, residuals: np.ndarray, percentile: float) -> float:
    """
    Calculate the fraction of the residuals that fall within the lower
    `percentile` of their respective Gaussian distributions, which are
    defined by their respective uncertainty estimates.

    Parameters
    ----------
    norm : scipy.stats.norm
        The normal distribution to use for the calculation.
    stdevs : np.ndarray
        The standard deviations of the residuals.
    residuals : np.ndarray
        The residuals to calculate the density of.
    percentile : float
        The percentile to calculate the density of.
    """
    # Find the normalized bounds of this percentile
    upper_bound = norm.ppf(percentile)

    # Normalize the residuals so they all should fall on the normal bell curve
    normalized_residuals = residuals.reshape(-1) / stdevs.reshape(-1)

    # Count how many residuals fall inside here
    num_within_quantile = 0
    for resid in normalized_residuals:
        if resid <= upper_bound:
            num_within_quantile += 1

    # Return the fraction of residuals that fall within the bounds
    density = num_within_quantile / len(residuals)
    return density


def calibration_curve(true, pred, stdevs, bins=100) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate the calibration curve of a set of predictions.

    Parameters
    ----------
    true : np.ndarray
        The true values.
    pred : np.ndarray
        The predicted values.
    stdevs : np.ndarray
        The standard deviations of the predictions.
    bins : int
        The number of bins to use for the calibration curve.
    """

    residuals = true - pred
    norm = stats.norm(0, 1)
    predicted_pi = np.linspace(0, 1, bins)
    observed_pi = [calculate_density(norm, stdevs, residuals, percentile) for percentile in predicted_pi]

    return predicted_pi, observed_pi


def miscalibration_area(predicted_pi: np.ndarray, observed_pi: np.ndarray) -> float:
    """
    Calculate the area between the calibration curve and the line of perfect calibration.

    Parameters
    ----------
    predicted_pi : np.ndarray
        The predicted probabilities.
    observed_pi : np.ndarray
        The observed probabilities.
    """
    return np.trapz(np.abs(predicted_pi - observed_pi), predicted_pi)


def calibration_error(predicted_pi: np.ndarray, observed_pi: np.ndarray) -> float:
    """
    Calculate the calibration error of a calibration curve.

    Parameters
    ----------
    predicted_pi : np.ndarray
        The predicted probabilities.
    observed_pi : np.ndarray
        The observed probabilities.
    """
    return ((predicted_pi - observed_pi) ** 2).sum()


def sharpness(stdevs: np.ndarray):
    """
    Calculate the sharpness of the uncertainty estimates.
    Here we calculate it as the square-root of the mean of the squared to have
    it in the same units as the predictions.
    """
    return np.sqrt((stdevs**2).mean())


def dispersion(stdevs: np.ndarray):
    """
    Calculate the dispersion of the uncertainty estimates.
    """
    return np.sqrt(((stdevs - stdevs.mean()) ** 2).sum() / (len(stdevs) - 1)) / stdevs.mean()


def error_based_calibration(
    truth: np.ndarray,
    pred: np.ndarray,
    sigma: np.ndarray,
    bins: int = 10,
    sigma_max: float = None,
    sigma_min: float = None,
):
    """
    Calculate the error-based calibration of a set of predictions.

    Parameters
    ----------
    truth : np.ndarray
        The true values.
    pred : np.ndarray
        The predicted values.
    sigma : np.ndarray
        The standard deviations of the predictions.
    bins : int
        The number of bins to use.
    sigma_max : float
        The maximum standard deviation to consider.
    sigma_min : float
        The minimum standard deviation.
    """

    eps = truth - pred
    if sigma_max is None:
        sigma_max = sigma.max()
    if sigma_min is None:
        sigma_min = sigma.min()

    bin_edges = np.linspace(sigma_min, sigma_max, bins)

    rmse = []
    rmv = []

    for i in range(bins - 1):
        mask = (sigma > bin_edges[i]) * (sigma <= bin_edges[i + 1])
        count = np.sum(mask)

        if count == 0:
            continue

        rmse.append(np.sqrt(1 / count * np.sum(eps[mask] ** 2)))
        rmv.append(np.sqrt(1 / count * np.sum(sigma[mask] ** 2)))

    rmse = np.array(rmse)
    rmv = np.array(rmv)

    return rmse, rmv


def calibration_plot(true, pred, stdevs, ax=None, **kwargs):
    predicted_pi, observed_pi = calibration_curve(true, pred, stdevs)

    if ax is None:
        fig, ax = plt.subplots()

    (l1,) = ax.plot(predicted_pi, observed_pi, **kwargs)
    ax.plot([0, 1], [0, 1], "k--", alpha=0.5)

    # Fill between:
    ax.fill_between(predicted_pi, predicted_pi, observed_pi, alpha=0.99, color=l1.get_color())

    mis_area = miscalibration_area(predicted_pi, observed_pi)
    cal_error = calibration_error(predicted_pi, observed_pi)

    # text = f'Miscalibration area: {mis_area:.3f}\nCalibration error: {cal_error:.3f}'
    # ax.text(0.05, 0.95, text, transform=ax.transAxes, va='top', ha='left')

    ax.set_xlabel("Predicted probability")
    ax.set_ylabel("Observed probability")
    ax.set_xlim([0, 1])

    return ax


def plot_residuals(ax, true, pred, sigmas, sigma_bin=1, steps=10):
    residuals = pred - true

    l1 = ax.scatter(residuals, sigmas)
    s = np.linspace(0, 20)
    ax.set_xlim([-20, 20])
    ax.set_ylim([0, 20])

    for conf in [1.96]:
        for sign in [1, -1]:
            ax.plot(
                sign * conf * s,
                s,
                color="black",
                linestyle="--",
                label="95% confidence interval",
            )
    ax.set_xlabel("Residual")
    ax.set_ylabel("Sigma")

    for i in range(1, steps):
        indices = (sigmas < sigma_bin * i) & (sigmas > sigma_bin * (i - 1))
        res = residuals[indices]

        norm = NormalDist.from_samples(res)

        weights, bins = np.histogram(res, bins=50)
        weights = weights / np.max(weights) * sigma_bin
        ax.bar(
            bins[:-1],
            weights,
            width=bins[1] - bins[0],
            alpha=0.9,
            bottom=sigma_bin * (i - 1),
            color="red",
            edgecolor="black",
        )
        x = np.linspace(-norm.stdev * 1.96, norm.stdev * 1.96, 100)
        y = sigma_bin * np.exp(-(x**2) / (2 * norm.stdev**2)) + sigma_bin * (i - 1)
        ax.plot(x, y, color="red", linestyle="--")


def plot_error_based_calibration(ax, truth, prediction, sigma, bins=10, sigma_min=None, sigma_max=None):
    rmse, rmv = error_based_calibration(truth, prediction, sigma, bins=bins, sigma_min=sigma_min, sigma_max=sigma_max)

    ax.plot(rmv, rmse, "-o")

    lin_fit = linregress(rmv, rmse)

    ax.plot(
        rmv,
        lin_fit.intercept + lin_fit.slope * rmv,
        "--",
        color="black",
        label=f"a = {lin_fit.slope:.2f}, b = {lin_fit.intercept:.2f}",
    )
    ax.plot(rmv, 0 + 1 * rmv, "r--", label="Ideal")

    ax.legend()
    ax.set_xlabel("RMV [eV]")
    ax.set_ylabel("RMSE [eV]")


def sharpness_plot(stdevs, bins=25, ax=None):
    if ax is None:
        fig, ax = plt.subplots()

    ax.hist(stdevs, bins=bins, density=True, edgecolor="k")

    ax.set_xlabel(r"$\sigma$")
    ax.set_ylabel("Density")

    sharpness_val = sharpness(stdevs)
    ax.axvline(sharpness_val, color="k", linestyle="--")

    dispersion_val = dispersion(stdevs)

    text = f"Sharpness: {sharpness_val:.3f}\nDispersion: {dispersion_val:.3f}"
    ax.text(0.95, 0.95, text, transform=ax.transAxes, va="top", ha="right")
    return ax
