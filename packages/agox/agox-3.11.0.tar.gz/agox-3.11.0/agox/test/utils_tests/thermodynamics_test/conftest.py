from typing import Dict, List

import numpy as np
import pytest
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator

from agox.candidates import StandardCandidate
from agox.utils.thermodynamics import ThermodynamicsData


@pytest.fixture(scope='module', params=[1, 2, 3])
def size(request: pytest.FixtureRequest) -> int:
    return request.param

@pytest.fixture(scope='module')
def total_energy(size: int) -> float:
    return -10.0 * size

@pytest.fixture(scope='module')
def formula(size: int) -> str:
    return f"Cu{size}O{2*size}"

@pytest.fixture(scope='module')
def symbols(size: int) -> List[str]:
    return ['Cu'] * size + ['O'] * 2*size

@pytest.fixture(scope='module')
def numbers(size: int) -> np.array:
    return np.array([29] * size + [8] * 2*size)

@pytest.fixture(scope='module')
def candidate(size: int, formula: str, total_energy: float) -> StandardCandidate:
    template = Atoms('', cell=np.eye(3)*10)
    atoms = Atoms(formula, positions=np.random.rand(size*3, 3)*10, cell=np.eye(3)*10)
    calculator = SinglePointCalculator(atoms, energy=total_energy)
    atoms.calc = calculator
    return StandardCandidate.from_atoms(template, atoms)

@pytest.fixture(scope='module')
def references() -> Dict[str, float]:
    return {'Cu': -1.0, 'O': -2.0}

@pytest.fixture(scope='module')
def chemical_potentials() -> Dict[str, float]:
    return {'Cu': -1.0, 'O': -2.0}

@pytest.fixture(scope='module')
def template_energy() -> float:
    return -10.0

@pytest.fixture(scope='module')
def thermo_data(references: Dict[str, float], chemical_potentials: Dict[str, float], template_energy: float) -> ThermodynamicsData:
    return ThermodynamicsData(references, chemical_potentials, template_energy)

@pytest.fixture(scope='module')
def expected_energy(symbols: List[str], total_energy: float, references: Dict[str, float], chemical_potentials: Dict[str, float], template_energy: float) -> float:

    gibbs = total_energy
    gibbs -= template_energy

    for symbol in symbols:
        gibbs -= references[symbol] + chemical_potentials[symbol]
    return gibbs
