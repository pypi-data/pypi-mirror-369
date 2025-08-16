from typing import Literal

import numpy as np

from agox.analysis.search_data import SearchData

from .property import ArrayPropertyData, Property


class EnergyProperty(Property):
                    
    def compute(self, search_data: SearchData) -> np.array:
        """
        Get the energy of the system as a np.array of shape [restarts, iterations].
        """

        axis_name, indices = self.get_time_axis(search_data)

        energy = ArrayPropertyData(
            data=search_data.get_all("energies", fill=np.inf),
            name="Energy",
            shape=("Restarts", axis_name),
            array_axis=(search_data.get_all_identifiers(), indices),
        )
        return energy
