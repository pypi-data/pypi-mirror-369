from typing import List, Union

import numpy as np
from matplotlib.axes import Axes

from agox.analysis.criterion import BaseCriterion
from agox.analysis.property import Property
from agox.analysis.search_data import SearchCollection, SearchData


class SuccessPlotter:
    def __init__(
        self, searches: Union[SearchCollection, List[SearchData]], search_property: Property, criterion: BaseCriterion
    ) -> None:
        self.searches = searches
        self.search_property = search_property
        self.criterion = criterion

    def plot(self, ax: Axes) -> None:
        for search in self.searches:
            self.plot_search(ax, search)

        ax.set_xlim(0, None)
        ax.set_ylim(0, 1)
        ax.legend()

    def plot_search(self, ax: Axes, search: SearchData) -> None:
        # Gather stuff:
        prop = self.search_property(search)
        distribution = self.criterion(prop)

        # Plot:
        (l1,) = ax.step(distribution.quantiles(), distribution.cdf(), label=f"{search.get_label()}", where="post")
        ax.fill_between(distribution.quantiles(), distribution.lower(), distribution.upper(), step="post", alpha=0.3)

        # Plot where the searches have gotten to
        points = np.nanmax(prop.axis[1], axis=1)
        y = distribution.ecdf.cdf.evaluate(points)
        ax.plot(points, y, "x", color=l1.get_color())

        ax.set_xlabel(f"{prop.shape[1]}")
        ax.set_ylabel("Success")
