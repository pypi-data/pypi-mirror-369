from abc import ABC, abstractmethod
from typing import Tuple

import numpy as np

from agox.analysis.criterion.base_criterion.discrete_distribution import DiscreteDistribution
from agox.analysis.search_data import SearchData


class BaseCriterion(ABC):
    @abstractmethod
    def compute(self, SearchData) -> Tuple[np.array, np.array]:
        """
        Compute the times and events for the boolean metric.
        """
        pass

    def __call__(self, search_data: SearchData) -> DiscreteDistribution:
        times, events = self.compute(search_data)
        return DiscreteDistribution(times, events)
