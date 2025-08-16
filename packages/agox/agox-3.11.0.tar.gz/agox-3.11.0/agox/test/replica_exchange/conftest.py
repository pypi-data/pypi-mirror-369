from typing import Callable

import numpy as np
import pytest
from ase import Atoms
from ase.calculators.emt import EMT

from agox.candidates import Candidate
from agox.environments import Environment
from agox.generators import RandomGenerator
from agox.models import CalculatorModel
from agox.samplers.replica_exchange import ReplicaExchangeSampler


@pytest.fixture(scope="module")
def emt_environment() -> Environment:
    template = Atoms(cell=np.eye(3) * 15)
    conf_cell = np.eye(3) * 10
    conf_corner = np.ones(3) * 2.5
    env = Environment(symbols="Cu12", template=template, confinement_cell=conf_cell, confinement_corner=conf_corner)
    return env


@pytest.fixture(scope="module")
def random_generator(emt_environment: Environment) -> RandomGenerator:
    return RandomGenerator(**emt_environment.get_confinement())


@pytest.fixture(scope="module")
def candidate_factory(
    random_generator: RandomGenerator, emt_environment: Environment
) -> Callable[[int], list[Candidate]]:
    def factory(n: int) -> list[Candidate]:
        candidates = [random_generator(sampler=None, environment=emt_environment)[0] for _ in range(n)]
        for i, candidate in enumerate(candidates):
            candidate.add_meta_information("walker_index", i)
            candidate.calc = EMT()

        return candidates

    return factory


@pytest.fixture(scope="function")
def emt_model() -> CalculatorModel:
    return CalculatorModel(calculator=EMT())


@pytest.fixture(scope="function")
def bare_sampler(emt_model: CalculatorModel) -> ReplicaExchangeSampler:
    sampler = ReplicaExchangeSampler(model=emt_model, sample_size=10, t_min=0.2, t_max=2)

    sampler.iteration_counter = 1

    return sampler

@pytest.fixture(scope='function')
def sampler(emt_model: CalculatorModel, candidate_factory: Callable) -> ReplicaExchangeSampler:    
    sampler = ReplicaExchangeSampler(model=emt_model, sample_size=10, 
                                     t_min=0.2, t_max=2)
    
    sampler.iteration_counter = 1
    candidates = candidate_factory(10)
    sampler.setup(candidates)

    return sampler
