import numpy as np
import pytest
from ase import Atoms
from ase.calculators.emt import EMT

from agox.models import CalculatorModel


class CountingEMT(EMT):

    def __init__(self) -> None:
        super().__init__()
        self.calculate_count = 0

    def calculate(self, *args, **kwargs) -> None:
        self.calculate_count += 1
        return super().calculate(*args, *kwargs)

@pytest.fixture
def dataset() -> list[Atoms]:

    data = []
    for _ in range(10):
        atoms = Atoms('Cu5Ni5', scaled_positions=np.random.rand(10, 3), pbc=[True, True, True], cell=np.eye(3)*5)
        atoms.calc = EMT()
        atoms.get_potential_energy()
        data.append(atoms)

    return data

@pytest.fixture
def model() -> CalculatorModel:
    return CalculatorModel(calculator=CountingEMT())

def test_predict_energy(model: CalculatorModel, dataset: list[Atoms]) -> None:
    for atoms in dataset:
        assert model.predict_energy(atoms) == atoms.get_potential_energy()

def test_predict_forces(model: CalculatorModel, dataset: list[Atoms]) -> None:
    for atoms in dataset:
        assert np.all(model.predict_forces(atoms) == atoms.get_forces())

def test_predict_energy_count(model: CalculatorModel, dataset: list[Atoms]) -> None:
    for i, atoms in enumerate(dataset):
        model.predict_energy(atoms)
        assert model.calculator.calculate_count == i+1

def test_predict_forces_count(model: CalculatorModel, dataset: list[Atoms]) -> None:
    for i, atoms in enumerate(dataset):
        model.predict_forces(atoms)
        assert model.calculator.calculate_count == i+1

def test_predict_energy_forces_count(model: CalculatorModel, dataset: list[Atoms]) -> None:
    for i, atoms in enumerate(dataset):
        model.predict_energy(atoms)
        model.predict_forces(atoms)
        assert model.calculator.calculate_count == i+1

def test_not_attach_calc(model: CalculatorModel, dataset: list[Atoms]) -> None:
    atoms = dataset[0]
    atoms.calc = None
    model.predict_energy(atoms)
    assert atoms.calc is None

def test_preserve_calc(model: CalculatorModel, dataset: list[Atoms]) -> None:
    atoms = dataset[0]
    calc_mem_address = id(atoms.calc)
    model.predict_energy(atoms)
    assert id(atoms.calc) == calc_mem_address