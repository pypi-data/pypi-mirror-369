from typing import Optional

import numpy as np
from ase import Atoms

from agox.models.ABC_model import ModelBaseClass


class CompositionModel(ModelBaseClass):
    name = "CompositionModel"
    implemented_properties = ["energy", "forces"]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.atom_energies = np.zeros(100)
        self.add_dynamic_attribute("atom_energies")

    def predict_energy(self, atoms: Atoms, **kwargs) -> float:
        numbers = atoms.get_atomic_numbers()
        return np.sum(self.atom_energies[numbers])

    def predict_forces(self, atoms: Atoms, **kwargs) -> np.ndarray:
        return np.zeros((len(atoms), 3))
    
    def reset(self) -> None:
        self.atom_energies = np.zeros(100)

    def train(self, data: list[Atoms], energies: Optional[np.ndarray] = None) -> None:
        self.atom_energies = np.zeros(100)
        n = len(self.atom_energies)
        features = np.zeros((len(data), n))

        for i, atoms in enumerate(data):
            numbers = atoms.get_atomic_numbers()
            for number in np.unique(numbers):
                features[i, number] += np.count_nonzero(numbers == number)

        if energies is None:
            energies = np.array([atoms.get_potential_energy() for atoms in data])

        self.atom_energies = np.linalg.pinv(features.T @ features) @ features.T @ energies
