
import numpy as np

from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.utils.thermodynamics import ThermodynamicsData, gibbs_free_energy


class GibbsFreeEnergyAquisitor(LowerConfidenceBoundAcquisitor):
    name = "GFEacquisitor"

    def __init__(
        self,
        thermo_data: ThermodynamicsData,
        model: object,
        kappa: float = 1,
        **kwargs,
    ):
        super().__init__(model, kappa, **kwargs)
        self.thermo_data = thermo_data

    def calculate_acquisition_function(
        self, candidates: list
    ) -> np.array:
        fitness = np.zeros(len(candidates))

        # Attach calculator and get model_energy
        for i, candidate in enumerate(candidates):
            E, sigma = self.model.predict_energy_and_uncertainty(candidate)

            fitness[i] = gibbs_free_energy(candidate=candidate, total_energy=self.acquisition_function(E, sigma), 
                                           thermo_data=self.thermo_data)

            # For printing:
            comp = candidate.get_search_formula()

            ##------------------------------
            candidate.add_meta_information("model_energy", E)
            candidate.add_meta_information("uncertainty", sigma)
            candidate.add_meta_information("model_gfe", fitness[i])
            candidate.add_meta_information("gfe_composition", comp)

        return fitness

    def print_information(self, candidates, acquisition_values):
        if self.model.ready_state:
            for i, candidate in enumerate(candidates):
                fitness = acquisition_values[i]

                GFEmodel = candidate.get_meta_information("model_gfe")
                composition = candidate.get_meta_information("gfe_composition")
                Emodel = candidate.get_meta_information("model_energy")
                sigma = candidate.get_meta_information("uncertainty")
                description = candidate.get_meta_information("description")
                self.writer(
                    "Candidate "
                    + composition
                    + ": GFE={:8.3f}, E={:8.3f}, s={:8.3f}, F={:8.3f}, {}".format(
                        GFEmodel, Emodel, sigma, fitness, description
                    )
                )
