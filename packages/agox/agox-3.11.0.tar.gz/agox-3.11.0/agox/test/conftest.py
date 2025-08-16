import os
from copy import deepcopy
from importlib.resources import files
from typing import List, Tuple

import numpy as np
import pytest
from ase.io import read

from agox.candidates import StandardCandidate
from agox.environments.environment import Environment


def pytest_addoption(parser):
    parser.addoption("--rtol", type=float, default=1e-05)
    parser.addoption("--atol", type=float, default=1e-08)
    parser.addoption("--create_mode", default=False, action="store_true")

class EnvironmentFactory:

    def __init__(self, environment: Environment) -> None:
        self.environment = environment
    
    def __call__(self) -> Environment:
        return self.environment
    
class DatasetFactory:
    
    def __init__(self, candidates: List[StandardCandidate]) -> None:
        self.candidates = candidates
    
    def __call__(self) -> List[StandardCandidate]:
        return deepcopy(self.candidates)



@pytest.fixture
def cmd_options(request):
    return {
        "tolerance": {"rtol": request.config.getoption("rtol"), "atol": request.config.getoption("atol")},
        "create_mode": request.config.getoption("create_mode"),
    }


@pytest.fixture(scope="module", autouse=True)
def ray_fix():
    import ray
    from agox.utils.ray import reset_ray_pool

    if ray.is_initialized():
        reset_ray_pool()
    yield


def pytest_sessionstart(session):
    from agox.utils.ray import ray_startup

    ray_startup(cpu_count=2, memory=None, tmp_dir=None, include_dashboard=False, max_grace_period=0.0)


test_folder_path = os.path.join(files("agox"), "test/")
test_data_dicts = [
    {"path": "datasets/AgO-dataset.traj", "remove": 6, "name": "AgO"},
    {"path": "datasets/B12-dataset.traj", "remove": 12, "name": "B12"},
    {"path": "datasets/C30-dataset.traj", "remove": 30, "name": "C30"},
]

for dictionary in test_data_dicts:
    dictionary['path'] = os.path.join(test_folder_path, dictionary['path'])

@pytest.fixture(params=test_data_dicts, scope="session")
def dataset_dict(request: pytest.FixtureRequest) -> dict:
    return request.param

@pytest.fixture(params=test_data_dicts, scope="module")
def environment_and_dataset(request: pytest.FixtureRequest) -> Tuple[Environment, List[StandardCandidate]]:
    atoms = read(request.param["path"])
    cell = atoms.get_cell()
    corner = np.array([0, 0, 0])
    remove = request.param["remove"]
    numbers = atoms.get_atomic_numbers()[len(atoms) - remove :]

    template = read(request.param["path"])
    del template[len(template) - remove : len(template)]
    environment = Environment(template=template, numbers=numbers, confinement_cell=cell, confinement_corner=corner)

    data = read(request.param["path"], ":")
    candidates = [StandardCandidate.from_atoms(template, a) for a in data]

    return environment, candidates

@pytest.fixture(scope="session")
def environment_factory(dataset_dict: dict) -> EnvironmentFactory:

    atoms = read(dataset_dict["path"])
    cell = atoms.get_cell()
    corner = np.array([0, 0, 0])
    remove = dataset_dict["remove"]
    numbers = atoms.get_atomic_numbers()[len(atoms) - remove :]

    template = read(dataset_dict["path"])
    del template[len(template) - remove : len(template)]
    environment = Environment(template=template, numbers=numbers, confinement_cell=cell, confinement_corner=corner)

    return EnvironmentFactory(environment)


@pytest.fixture(scope="session")
def dataset_factory(dataset_dict: dict) -> DatasetFactory:
    atoms = read(dataset_dict["path"])
    data = read(dataset_dict["path"], ":")
    candidates = [StandardCandidate.from_atoms(atoms, a) for a in data]
    return DatasetFactory(candidates)
