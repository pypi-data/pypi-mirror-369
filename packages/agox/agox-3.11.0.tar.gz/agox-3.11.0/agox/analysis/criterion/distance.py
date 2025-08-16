from typing import Any, Tuple

import numpy as np
from scipy.spatial.distance import cdist

from agox.analysis.criterion.base_criterion import BaseCriterion
from agox.analysis.property.property import ListPropertyData


class DistanceCriterion(BaseCriterion):
    def __init__(self, threshold: float, comparate: Any) -> None:
        """
        Find the time at which the property first crosses below a threshold.

        Parameters
        ----------
        threshold : float
            Distance threshold to compare against the property data
        comparate : Any
            Data to compare against the property data, of the same type as the objects in property_data.data
        """
        self.threshold = threshold
        self.comparate = comparate

    def compute(self, property_data: ListPropertyData) -> Tuple[np.array, np.array]:
        """
        Parameters
        ----------
        property_data : ListPropertyData
            Property data to be analyzed
        """
        time_indices = []
        events = []

        for data in property_data.data:
            property_arr = np.array(data).squeeze().reshape(-1, self.comparate.shape[1])
            distances = cdist(property_arr, self.comparate)
            below_threshold = distances <= self.threshold
            if below_threshold.any():
                indices = np.argwhere(below_threshold).flatten()
                time = indices[0]
                event = 1
            else:
                time = len(property_arr)-1
                event = 0

            time_indices.append(time)
            events.append(event)

        events = np.array(events)
        times = self._get_times(property_data, time_indices, events)

        # times = np.array([property_data.axis[1][i, time_index] for i, time_index in enumerate(time_indices)])
        # times[events == 0] = np.nanmax(property_data.axis[1])

        print(f"Distance criterion: {np.sum(events)} events found")
        print(events)

        return times, events
    
    def _get_times(self, property_data, time_indices, events):
        times = np.array([property_data.axis[1][i, time_index] for i, time_index in enumerate(time_indices)])
        times[events == 0] = np.nanmax(property_data.axis[1])
        return times
