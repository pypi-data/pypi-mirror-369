import numpy as np
import pytest

from agox.candidates import CandidateBaseClass
from agox.generators import (
    CenterOfGeometryGenerator,
    RandomGenerator,
    RattleGenerator,
    ReplaceGenerator,
    SamplingGenerator,
)
from agox.helpers.confinement import Confinement

generator_params = [
    (RandomGenerator, (), {}),
    (RandomGenerator, (), {"may_nucleate_at_several_places": True, "c2": 2.5}),
    (RattleGenerator, (), {}),
    (RattleGenerator, (), {"n_rattle": 1}),
    (RattleGenerator, (), {"rattle_amplitude": 1}),
    (ReplaceGenerator, (), {}),
    (ReplaceGenerator, (), {"n_replace": 3}),
    (ReplaceGenerator, (), {"amplitude": 1}),
    (CenterOfGeometryGenerator, (), {}),
    (SamplingGenerator, (), {}),
]


@pytest.fixture(scope="module", params=generator_params)
def candidate(request, sampler, test_environment):
    generator = request.param[0](*request.param[1], **test_environment.get_confinement(), **request.param[2])

    candidate = None
    attempt = 0
    while candidate is None and attempt < 10:
        candidate = generator(sampler, test_environment)[0]
        attempt += 1
    return candidate


def test_output_type(candidate):
    assert isinstance(candidate, CandidateBaseClass)


def test_atomic_formula(candidate, test_environment):
    candidate_numbers = np.sort(np.array(candidate.get_atomic_numbers()))
    env_numbers = np.sort(np.array(test_environment.get_all_numbers()))

    assert (candidate_numbers == env_numbers).all()


def test_confinement(candidate, test_environment):
    indices = test_environment.get_missing_indices()
    positions = candidate.positions[indices, :]
    confinement = test_environment.get_confinement(as_dict=False)
    assert confinement.check_confinement(positions).all()


def test_template(candidate, test_environment):
    template = test_environment.get_template()
    assert (candidate.positions[0 : len(template)] == template.positions).all()


def test_cell(candidate, test_environment):
    assert (candidate.cell == test_environment.get_template().get_cell()).all()
