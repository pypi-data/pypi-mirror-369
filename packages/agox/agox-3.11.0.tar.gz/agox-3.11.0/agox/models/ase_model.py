from typing import Optional

import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator

from agox.models import CompositionModel, ModelBaseClass
from agox.utils import candidate_list_comprehension


class CalculatorModel(ModelBaseClass):
    """
    A model that turns an ASE calculator into a model that can be used with AGOX.
    """

    name = "CalculatorModel"
    implemented_properties = ["energy", "forces"]

    def __init__(self, calculator: Calculator, composition_model: bool = True, **kwargs) -> None:
        super().__init__(**kwargs)
        self.calculator = calculator
        if composition_model:
            self.composition_model = CompositionModel()
        else:
            self.composition_model = None
            
        self.name = f"{calculator.__class__.__name__}Model"

    @candidate_list_comprehension
    def predict_energy(self, atoms: Atoms, **kwargs) -> float:
        energy = self.calculator.get_potential_energy(atoms)
        if self.composition_model is not None:
            energy += self.composition_model.predict_energy(atoms)
        return energy

    @candidate_list_comprehension
    def predict_forces(self, atoms: Atoms, **kwargs) -> np.ndarray:
        return self.calculator.get_forces(atoms)

    def train(
        self, data: list[Atoms], self_labels: Optional[np.ndarray] = None, truth_labels: Optional[np.ndarray] = None
    ) -> None:
        if self_labels is None:
            self.composition_model.reset()
            self_labels = np.array([self.predict_energy(atoms) for atoms in data])
        if truth_labels is None:
            truth_labels = np.array([atoms.get_potential_energy() for atoms in data])

        self.writer(f'Training composition model on {len(data)} configurations.')
        self.composition_model.train(data, energies = truth_labels - self_labels)

        indices = np.argwhere(self.composition_model.atom_energies != 0).flatten()
        self.writer("Composition model atom energies:")
        for i in indices:
            self.writer(f"Z={i}: {self.composition_model.atom_energies[i]:0.3f}")



