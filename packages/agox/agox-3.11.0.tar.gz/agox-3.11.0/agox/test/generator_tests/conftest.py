import os
from importlib.resources import files

import numpy as np
import pytest
from ase import Atoms
from ase.build import fcc100
from ase.io import read

from agox.candidates import StandardCandidate
from agox.environments.environment import Environment
from agox.generators import RandomGenerator
from agox.samplers.fixed_sampler import FixedSampler


def nonperiodic_environment(symbols):
    template = Atoms("", cell=np.eye(3) * 25, pbc=False)
    confinement_corner = np.array([2.5, 2.5, 2.5])
    confinement_cell = np.eye(3) * 20
    environment = Environment(
        template=template,
        symbols=symbols,
        confinement_corner=confinement_corner,
        confinement_cell=confinement_cell,
    )
    return environment


def slab_environment(symbols):
    template = fcc100("Al", size=(3, 3, 2), vacuum=10.0, orthogonal=True, periodic=True)
    template.positions[:, 2] -= template.positions[:, 2].min()

    confinement_corner = [0, 0, template.positions[:, 2].max()]
    confinement_cell = template.cell.copy()
    confinement_cell[2, 2] = 4

    environment = Environment(
        template=template, symbols=symbols, confinement_corner=confinement_corner, confinement_cell=confinement_cell
    )
    return environment


non_periodic_environment_params = [(nonperiodic_environment, ["B12"]), (nonperiodic_environment, ["B12N12"])]
non_periodic_environment_param_ids = ["nonperiodic_B12", "nonperiodic_B12N12"]


@pytest.fixture(params=non_periodic_environment_params, ids=non_periodic_environment_param_ids, scope="module")
def test_environment_non_periodic(request):
    return request.param[0](*request.param[1])


slab_environment_params = [(slab_environment, ["Al9"]), (slab_environment, ["Al5O4"])]
slab_environment_param_ids = ["slab_Al9", "slab_Al5O4"]


@pytest.fixture(params=slab_environment_params, ids=slab_environment_param_ids, scope="module")
def test_environment_slab(request):
    return request.param[0](*request.param[1])


all_environment_params = slab_environment_params + non_periodic_environment_params
all_environment_param_ids = slab_environment_param_ids + non_periodic_environment_param_ids


@pytest.fixture(params=all_environment_params, ids=all_environment_param_ids, scope="module")
def test_environment(request):
    return request.param[0](*request.param[1])


@pytest.fixture(scope="module")
def random_generator():
    def make_generator(environment):
        generator = RandomGenerator(**environment.get_confinement())
        return generator

    return make_generator


@pytest.fixture(scope="module")
def random_candidate(random_generator, test_environment):
    generator = random_generator(test_environment)
    return generator(None, test_environment)[0]


@pytest.fixture(scope="module")
def sampler(random_candidate):
    return FixedSampler(random_candidate)


