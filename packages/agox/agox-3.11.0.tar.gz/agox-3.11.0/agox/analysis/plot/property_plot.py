from typing import List, Union

import numpy as np
from matplotlib.axes import Axes

from agox.analysis.property import Property
from agox.analysis.search_data import SearchCollection, SearchData


class PropertyPlotter:
    def __init__(self, searches: Union[SearchCollection, List[SearchData]], search_property: Property, window: int = 5) -> None:
        """
        Plot an analysis property versus time for a list of searches. The property
        should be a scalar property, e.g. one number pr. iteration/time-step of a search.
        """
        self.searches = searches
        self.search_property = search_property
        self.window = window

    def plot(self, ax: Axes) -> None:
        for search in self.searches:
            self.plot_search(ax, search)

        ax.set_xlim(0, None)
        ax.legend()

    def plot_search(self, ax: Axes, search: SearchData) -> None:
        # Gather stuff
        prop = self.search_property(search)
        values = prop.data
        time = prop.axis[1]
        min_energies = np.minimum.accumulate(values, axis=1)

        time_mean = np.nanmean(time, axis=0)
        prop_mean = np.nanmean(values, axis=0)
        prop_min = np.nanmin(min_energies, axis=0)

        prop_min_avg = np.nanmean(min_energies, axis=0)

        roll_kernel = np.ones(self.window) / self.window
        roll_avg = np.convolve(prop_mean, roll_kernel, mode="valid")

        values_max = np.nanmax(values, axis=0)
        values_min = np.nanmin(values, axis=0)
        values_min_roll = np.convolve(values_min, roll_kernel, mode="valid")
        values_max_roll = np.convolve(values_max, roll_kernel, mode="valid")

        # Plot - mean
        (l1,) = ax.plot(time_mean, prop_min, zorder=1) # Minimum energy among all restarts
        ax.plot(time_mean, prop_min_avg, '--', color=l1.get_color(), zorder=1) # Average minimum energy among all restarts
        l2, = ax.plot(time_mean[:len(roll_avg)], roll_avg, label=f"{search.get_label()}", color=l1.get_color(), zorder=0, alpha=0.75) # Rolling average
        ax.fill_between(time_mean[:len(values_max_roll)], values_max_roll, values_min_roll, alpha=0.2, color=l1.get_color(), zorder=0.5) # Rolling average spread

        ax.set_xlabel(f"{prop.shape[1]}")
        ax.set_ylabel(f"{prop.name}")
