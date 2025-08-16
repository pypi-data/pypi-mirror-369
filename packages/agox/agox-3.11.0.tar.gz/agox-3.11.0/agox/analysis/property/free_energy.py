import numpy as np

from agox.utils.thermodynamics import ThermodynamicsData, gibbs_free_energy

from .property import ArrayPropertyData, Property, SearchData


class FreeEnergyProperty(Property):
    def __init__(self, thermo_data: ThermodynamicsData, time_axis=None):
        """
        Get the energy of the system as a np.array of shape [restarts, iterations].
        """
        if time_axis is None:
            time_axis = "indices"

        if time_axis not in ["indices", "iterations"]:
            raise ValueError("time_axis must be one of ['indices', 'iterations']")
        self.thermo_data = thermo_data
        self.time_axis = time_axis

    def get_time_axis(self, search_data: SearchData) -> str:
        axis_name = self.time_axis.capitalize()

        if self.time_axis == "indices":
            indices = search_data.get_all("indices", fill=np.nan)
        elif self.time_axis == "iterations":
            indices = search_data.get_all("iterations", fill=np.nan)
        else:
            indices = search_data.get_all("times", fill=np.nan) / self.unit * self.cost_factor
            if self.cost_factor == 1:
                axis_name = axis_name + f" [{self.time_unit_symbol}]"
            else:
                axis_name = f"CPU cost [{self.time_unit_symbol}]"

        if self.time_axis in ["indices", "iterations"]:
            axis_name = f"{axis_name} [#]"

        return axis_name, indices

    def compute(self, search_data) -> np.array:
        """
        Get the energy of the system as a np.array of shape [restarts, iterations].
        """

        axis_name, indices = self.get_time_axis(search_data)

        candidates = search_data.get_all_candidates()
        energy = search_data.get_all("energies", fill=np.inf)
        free_energy = np.ones_like(energy) * np.inf

        N_restarts = search_data.get_number_of_restarts()

        for restart in range(N_restarts):
            for observation in range(len(candidates[restart])):
                candidate = candidates[restart][observation]
                free_energy[restart, observation] = gibbs_free_energy(candidate=candidate, thermo_data=self.thermo_data)

        free_energy_property = ArrayPropertyData(
            data=free_energy,
            name='Free Energy',
            shape=("Restarts", axis_name),
            array_axis=(search_data.get_all_identifiers(), indices),
        )

        return free_energy_property
