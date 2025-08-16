import numpy as np
import pytest

from agox.candidates import StandardCandidate
from agox.utils.thermodynamics import ThermodynamicsData
from agox.utils.thermodynamics.gibbs import gibbs_free_energy


def test_gibbs_candidate(candidate: StandardCandidate, thermo_data: ThermodynamicsData, expected_energy: float) -> None:
    assert gibbs_free_energy(candidate, thermo_data=thermo_data) == expected_energy

def test_gibbs_numbers(numbers: np.ndarray, total_energy: int, thermo_data: ThermodynamicsData, expected_energy: float) -> None:
    assert gibbs_free_energy(numbers=numbers, total_energy=total_energy, thermo_data=thermo_data) == expected_energy

def test_gibbs_candidate_dicts(candidate: StandardCandidate, references: dict, chemical_potentials: dict, template_energy: float, expected_energy: float) -> None:
    assert gibbs_free_energy(candidate, references=references, chemical_potentials=chemical_potentials, template_energy=template_energy) == expected_energy

def test_gibbs_raise(candidate: StandardCandidate) -> None:

    with pytest.raises(ValueError):
        gibbs_free_energy(candidate)
