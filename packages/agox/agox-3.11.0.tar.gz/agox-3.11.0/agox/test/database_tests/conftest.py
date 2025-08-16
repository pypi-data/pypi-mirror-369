from pathlib import Path
from typing import Callable, Dict, List, Tuple

import numpy as np
import pytest
from ase.symbols import Symbols

from agox.candidates import Candidate
from agox.databases import Database
from agox.environments import Environment


@pytest.fixture(scope='module')
def database_path(tmpdir_factory: Callable, environment_and_dataset: Tuple[Environment, List[Candidate]]) -> str:
    environment, dataset = environment_and_dataset
    total_symbols = Symbols(environment.get_all_numbers())

    # Make and move to temp dir:
    d = tmpdir_factory.mktemp("database_test")
    return d / f"db_{total_symbols}.db"

@pytest.fixture(scope='module')
def meta_dict() -> Dict:
    return {
        "str": "str",
        "int": 0,
        "float": 0.1,
        "1darr": np.array([0, 1, 2]),
        "2darr": np.random.rand(3, 3)
    }

@pytest.fixture(scope='module')
def dataset(environment_and_dataset: Tuple[Environment, List[Candidate]], meta_dict: Dict) -> list:
    environment, dataset = environment_and_dataset

    meta_data_names = list(meta_dict.keys())
    meta_data_examples = list(meta_dict.values())

    with_meta_data = []
    for candidate in dataset:
        candidate = candidate.copy()
        for meta_data_name, meta_data in zip(meta_data_names, meta_data_examples):
            candidate.add_meta_information(meta_data_name, meta_data)
        with_meta_data.append(candidate)
    return dataset

@pytest.fixture(scope='module')
def database_created(database_path: Path, dataset: list, meta_dict: dict) -> Database:
    # Make and move to temp dir:
    database_created = Database(database_path)
    meta_data_names = list(meta_dict.keys())
    meta_data_examples = list(meta_dict.values())

    for candidate in dataset:
        for meta_data_name, meta_data in zip(meta_data_names, meta_data_examples):
            candidate.add_meta_information(meta_data_name, meta_data)
        database_created.store_candidate(candidate)

    return database_created

@pytest.fixture(scope='module')
def database_loaded(database_path: Path) -> Database:
    database_loaded = Database(database_path)
    database_loaded.restore_to_memory()
    return database_loaded