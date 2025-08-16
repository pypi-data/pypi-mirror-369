import os
import pickle
from importlib.resources import files
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
from uuid import uuid4

import numpy as np
from ase import Atoms
from ase.io import read

from agox.candidates import StandardCandidate
from agox.environments import Environment
from agox.samplers import SamplerBaseClass

test_folder_path = os.path.join(files("agox"), "test/")

test_data_dicts = [
    {"path": "datasets/AgO-dataset.traj", "remove": 6, "name": "AgO"},
    {"path": "datasets/B12-dataset.traj", "remove": 12, "name": "B12"},
    {"path": "datasets/C30-dataset.traj", "remove": 30, "name": "C30"},
]

for dictionary in test_data_dicts:
    dictionary["path"] = os.path.join(test_folder_path, dictionary["path"])


class TemporaryFolder:
    def __init__(self, path: Union[str, Path]) -> None:
        d = path / ""
        if not os.path.exists(d):
            d.mkdir()
        self.start_dir = os.getcwd()
        self.path = d

    def __enter__(self) -> None:
        os.chdir(self.path)

    def __exit__(self, *args) -> None:
        os.chdir(self.start_dir)


def compare_candidates(atoms_1: Atoms, atoms_2: Atoms, tolerance: float) -> bool:
    if atoms_1 is None and atoms_2 is None:
        return True

    np.testing.assert_allclose(atoms_1.positions, atoms_2.positions, **tolerance)
    np.testing.assert_allclose(atoms_1.cell, atoms_2.cell, **tolerance)
    np.testing.assert_allclose(atoms_1.numbers, atoms_2.numbers, **tolerance)
    return True


def get_test_environment(path: Union[str, Path], remove: int) -> Environment:
    from agox.environments import Environment

    atoms = read(path, index=0)
    cell = atoms.get_cell()
    corner = np.array([0, 0, 0])
    numbers = atoms.get_atomic_numbers()[len(atoms) - remove :]

    template = atoms.copy()
    del template[len(template) - remove : len(template)]
    environment = Environment(template=template, numbers=numbers, confinement_cell=cell, confinement_corner=corner)

    return environment


def get_test_data(path: Union[str, Path], environment: Environment) -> List[StandardCandidate]:
    template = environment.get_template()
    atoms_data = read(path, index=":")
    candidate_data = [StandardCandidate.from_atoms(template, atoms) for atoms in atoms_data]
    return candidate_data


def get_test_sampler(data: List[StandardCandidate]) -> SamplerBaseClass:
    from agox.samplers import SamplerBaseClass

    class DummySampler(SamplerBaseClass):
        name = "DummySampler"
        initialized = False

        def __init__(self, data: List[StandardCandidate]) -> None:
            self.sample = data

            for candidate in self.sample:
                candidate.add_meta_information("spawn_uuids", [uuid4()])

        def setup(self, *args, **kwargs):
            return None

    return DummySampler(data)


def get_name(module_name: str, subfolder: str, dataset_name: str, parameter_index: str) -> str:
    folder = "expected_outputs/"
    name = f"{test_folder_path}{subfolder}{folder}{module_name}_data{dataset_name}_parameter{parameter_index}.pckl"
    return name


def save_expected_data(name: str, data: Any) -> None:
    check_file_is_deleted(name)
    with open(name, "wb") as f:
        pickle.dump(data, f)


def load_expected_data(name: str) -> Any:
    with open(name, "rb") as f:
        data = pickle.load(f)
    return data


def label_dict_list(list_of_dicts: List[Dict]) -> List[Tuple[Dict, int]]:
    for index, dictionary in enumerate(list_of_dicts):
        list_of_dicts[index] = (dictionary, index)
    return list_of_dicts


def check_folder_is_empty(path: Union[str, Path]) -> None:
    path = Path(path)

    if not path.exists():
        print("Creating path")
        path.mkdir(parents=True)

    files = list(path.glob("*"))
    assert len(files) == 0, "Expected path is not empty, delete the files if you are sure you want to remake them!"


def check_file_is_deleted(filepath: Path) -> None:
    assert not os.path.exists(
        filepath
    ), "File already exists - manually delete it if youre sure you want to recreate it."
