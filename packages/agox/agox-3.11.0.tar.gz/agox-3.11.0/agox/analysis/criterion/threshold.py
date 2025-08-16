from typing import Tuple

import numpy as np

from agox.analysis.criterion.base_criterion import BaseCriterion
from agox.analysis.property.property import PropertyData


class ThresholdCriterion(BaseCriterion):
    def __init__(self, threshold: float):
        """
        Find the time at which the property first crosses below a threshold.

        Parameters
        ----------
        threshold : float

        """
        self.threshold = threshold

    def compute(self, property_data: PropertyData) -> Tuple[np.array, np.array]:
        """
        Parameters
        ----------
        property_arr : np.array
            The property array to compute the metric on, shape (n_restarts, n_observations).
        """
        property_arr = property_data.data
        property_time = property_data.axis[1]

        # Rolling minimum of the property array
        min_energies = np.minimum.accumulate(property_arr, axis=1)

        # Check if the minimum energy is below the threshold
        success = min_energies <= self.threshold

        # Find the time of the first success
        events = np.max(success, axis=1).astype(int)
        times_indices = np.argmax(success, axis=1)

        times = np.array([property_data.axis[1][i, time_index] for i, time_index in enumerate(times_indices)])
        times[events == 0] = np.nanmax(property_time)

        return times, events
