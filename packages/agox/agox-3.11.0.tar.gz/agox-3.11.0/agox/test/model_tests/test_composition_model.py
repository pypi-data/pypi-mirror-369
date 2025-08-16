import numpy as np
import pytest
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator

from agox.models import CompositionModel


@pytest.fixture
def dataset() -> list[Atoms]:
    data = []
    test_atom_energies = np.zeros(100)
    test_atom_energies[8] = 10
    test_atom_energies[6] = 5

    for _ in range(10):
        numbers = np.random.choice([6, 8], 10, replace=True)
        energy = np.sum(test_atom_energies[numbers])
        atoms = Atoms(numbers)
        atoms.calc = SinglePointCalculator(atoms, energy=energy, forces=np.zeros((len(atoms), 3)))
        data.append(atoms)

    return data

@pytest.fixture
def model(dataset: list[Atoms]) -> CompositionModel:
    model = CompositionModel()
    model.train(dataset)
    return model

def test_train(model: CompositionModel) -> None:
    assert model.atom_energies[8] == pytest.approx(10, abs=1e-3)
    assert model.atom_energies[6] == pytest.approx(5, abs=1e-3)
    mask = np.ones(100, dtype=bool)
    mask[6] = False
    mask[8] = False
    assert np.all(model.atom_energies[mask] == 0)

def test_predict_energy(model: CompositionModel) -> None:
    atoms = Atoms([6, 8, 6, 8])
    assert model.predict_energy(atoms) == pytest.approx(30, abs=1e-3)

def test_predict_forces(model: CompositionModel) -> None:
    atoms = Atoms([6, 8, 6, 8])
    assert np.all(model.predict_forces(atoms) == 0)