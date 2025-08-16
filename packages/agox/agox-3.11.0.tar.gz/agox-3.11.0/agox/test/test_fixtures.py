from collections.abc import Callable

import numpy as np
from ase import Atoms

from agox.environments import Environment


def test_factory_fixtures(dataset_factory: Callable[[], list[Atoms]], environment_factory: Callable[[], Environment]) -> None:
    dataset = dataset_factory()
    environment = environment_factory()

    numbers_data = np.sort(np.unique(dataset[0].get_atomic_numbers()))
    numbers_env = np.sort(np.unique(environment.get_all_numbers()))
    np.testing.assert_array_equal(numbers_data, numbers_env)
