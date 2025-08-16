from __future__ import annotations

from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from numpy.typing import NDArray

from agox.utils.metrics import get_metrics


def get_limits(
    arrays: NDArray,
    extra: float = 0.0,
    extra_min: float = None,
    extra_max: float = None,
):
    max_value = -np.inf
    min_value = np.inf

    for arr in arrays:
        max_value = max(max_value, np.max(arr))
        min_value = min(min_value, np.min(arr))

    if extra_min is not None:
        min_value -= extra_min
    if extra_max is not None:
        max_value += extra_max

    max_value += extra
    min_value -= extra

    return [min_value, max_value]


def plot_parity(
    ax: Axes,
    truths: NDArray | Dict[str, NDArray] | List[NDArray],
    predictions: NDArray | Dict[str, NDArray] | List[NDArray],
    labels=None,
    inset: bool = False,
    inset_kwargs: dict = None,
    recursive: bool = False,
    limits=None,
    metrics_used=None,
    scatter_kwargs=None,
    decimal: int = 3,
):
    """
    Plot parity plot for a set of predictions and truths.

    Parameters
    ----------
    ax : Axes
        Matplotlib axes to plot on.
    truths : Dict[str, NDArray] | List[NDArray] | NDArray
        Dictionary with the true values.
    predictions : Dict[str, NDArray] | List[NDArray] | NDArray
        Dictionary with the predicted values.
    labels : List[str], optional
        List of keys to plot, if given only these keys will be plotted. If not,
        all pairs of keys in both truths and predictions will be plotted.
    inset : bool, optional
        Whether to plot an inset with the same data.
    inset_kwargs : dict, optional
        Kwargs to pass to the inset axes.
    metrics_used : List[str], optional
        List of metrics to display in the legend.
    scatter_kwargs : dict, optional
        Kwargs to pass to the scatter plot.
    """

    # Scatter kwargs are created and updated with the given kwargs
    base_scatter_kwargs = {
        "edgecolor": "white",
        "linewidth": 1,
        "alpha": 1.0,
        "s": 50,
    }

    if scatter_kwargs is not None:
        base_scatter_kwargs.update(scatter_kwargs)

    # Limits
    if limits is None:
        limits_extra_min = 0.1
        limits_extra_max = 0.1
    else:
        limits_extra_min = limits[0]
        limits_extra_max = limits[1]

    # Check whether we have a dictionary or a list

    if isinstance(truths, dict) and isinstance(predictions, dict):
        if labels is None:
            labels = set(truths.keys()).intersection(set(predictions.keys()))
        truths = [truths[label] for label in labels]
        predictions = [predictions[label] for label in labels]
    elif isinstance(truths, list) and isinstance(predictions, list):
        if labels is None:
            labels = [f"Pair {i}" for i in range(len(truths))]
    elif isinstance(truths, np.ndarray) and isinstance(predictions, np.ndarray):
        truths = [truths]
        predictions = [predictions]
        if labels is None:
            labels = ["Pair 1"]
    else:
        raise ValueError("Truths and predictions must be both dicts, lists or arrays.")

    for label, true, pred in zip(labels, truths, predictions):
        label_str = f"{label}"

        if metrics_used is not None:
            metrics = get_metrics(true, pred)
            for metric in metrics_used:
                label_str += f"\n{metric.upper()}: {metrics[metric]:.{decimal}f}"

        l1 = ax.scatter(
            true,
            pred,
            **base_scatter_kwargs,
            label=label_str,
        )

    # Prettyness
    calculated_limits = get_limits(truths + predictions, extra_max=limits_extra_max, extra_min=limits_extra_min)
    ax.plot(calculated_limits, calculated_limits, color="black", linestyle="--")

    # Add inset in lower right side:
    if inset:
        # Manage kwargs for the inset
        default_inset_kwargs = {
            "width": "40%",
            "height": "40%",
            "loc": "lower right",
            "bounds": [0, 5],
        }

        default_inset_kwargs.update(inset_kwargs or {})
        inset_kwargs = default_inset_kwargs
        bounds = inset_kwargs.pop("bounds")
        ax_inset = inset_axes(ax, **inset_kwargs)

        inset_min = calculated_limits[0] + bounds[0] + limits_extra_min
        inset_max = inset_min + bounds[0] + bounds[1]
        inset_limits = [inset_min, inset_max]

        print(inset_limits)

        plot_parity(
            ax_inset,
            truths,
            predictions,
            labels=labels,
            inset=False,
            metrics_used=None,
            limits=[limits_extra_min, 0],
            recursive=True,
            scatter_kwargs=scatter_kwargs,
        )

        ax_inset.legend(fontsize=7)
        ax_inset.set_xticklabels([])
        ax_inset.set_yticklabels([])

        ax_inset.set_xlim(inset_limits)
        ax_inset.set_ylim(inset_limits)

        # Plot the area of the inset in the main plot
        ax.add_patch(
            plt.Rectangle(
                (inset_limits[0], inset_limits[0]),
                inset_limits[1] - inset_limits[0],
                inset_limits[1] - inset_limits[0],
                fill=False,
                linestyle="--",
                color="black",
            )
        )

    if not recursive:
        ax.set_xlim(calculated_limits)
        ax.set_ylim(calculated_limits)

    ax.legend(loc="upper left")
