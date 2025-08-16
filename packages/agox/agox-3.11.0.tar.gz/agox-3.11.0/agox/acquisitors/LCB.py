import numpy as np
from ase.calculators.calculator import all_changes

from agox.acquisitors.ABC_acquisitor import AcquisitonCalculatorBaseClass, AcquisitorBaseClass


class LowerConfidenceBoundAcquisitor(AcquisitorBaseClass):
    """
    Lower Confidence Bound Acquisitor, using predictions and uncertainties from a model.

    The acquisition function is given by

    .. math::

        F(x) = E(x) - \kappa \sigma(x)


    Parameters
    -----------

    model: agox.models.ABC_model.ModelBaseClass
        Model that is used for the acquisition function.
    kappa: float
        Constant that is multiplied with the uncertainty.
    kwargs: dict
        Dictionary of keyword arguments passed to the AcquisitorBaseClass.
    """

    name = "LCBAcquisitor"

    def __init__(self, model, kappa=1, **kwargs):
        super().__init__(**kwargs)
        self.kappa = kappa
        self.model = model

    def calculate_acquisition_function(self, candidates):
        fitness = np.zeros(len(candidates))

        # Attach calculator and get model_energy
        for i, candidate in enumerate(candidates):
            E, sigma = self.model.predict_energy_and_uncertainty(candidate)
            fitness[i] = self.acquisition_function(E, sigma)

            # For printing:
            candidate.add_meta_information("model_energy", E)
            candidate.add_meta_information("uncertainty", sigma)

        return fitness

    def print_information(self, candidates, acquisition_values):

        format_float = lambda f: f"{f:.3f}"

        columns = ['Candidate', 'Energy', 'Uncertainty', 'Fitness', 'Generator']
        rows = []
        if self.model.ready_state:
            for i, candidate in enumerate(candidates):
                fitness = format_float(acquisition_values[i])
                Emodel = format_float(candidate.get_meta_information("model_energy"))
                sigma = format_float(candidate.get_meta_information("uncertainty"))
                generator = candidate.get_meta_information("generator")
                rows.append([str(i), Emodel, sigma, fitness, generator])
        
        self.writer.write_table(columns, rows, show_lines=False, show_edge=False)

    def get_acquisition_calculator(self):
        return LowerConfidenceBoundCalculator(self.model, self.acquisition_function, self.acquisition_force)

    def acquisition_function(self, E, sigma):
        return E - self.kappa * sigma

    def acquisition_force(self, E, F, sigma, sigma_force):
        return F - self.kappa * sigma_force

    def do_check(self, **kwargs):
        return self.model.ready_state


class LowerConfidenceBoundCalculator(AcquisitonCalculatorBaseClass):
    implemented_properties = ["energy", "forces"]

    def __init__(self, model, acquisition_function, acquisition_force, **kwargs):
        super().__init__(model, **kwargs)
        self.acquisition_function = acquisition_function
        self.acquisition_force = acquisition_force

    def calculate(self, atoms=None, properties=["energy"], system_changes=all_changes):
        super().calculate(atoms, properties, system_changes)

        derivatives = "forces" in properties
        model_data = self.model.converter(atoms, derivatives=derivatives)

        E = self.model.predict_energy(atoms, **model_data)
        sigma = self.model.predict_uncertainty(atoms, **model_data)
        self.results["energy"] = self.acquisition_function(E, sigma)

        if derivatives:
            F = self.model.predict_forces(atoms, **model_data)
            sigma_force = self.model.predict_uncertainty_forces(atoms, **model_data)

            self.results["forces"] = self.acquisition_force(E, F, sigma, sigma_force)
