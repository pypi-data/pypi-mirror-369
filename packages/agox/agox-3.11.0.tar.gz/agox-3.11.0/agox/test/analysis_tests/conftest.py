from pathlib import Path
from typing import List

import pytest

from agox.analysis.property import EnergyProperty, FreeEnergyProperty, ArrayPropertyData
from agox.analysis.search_data import SearchCollection, SearchData
from agox.utils.thermodynamics.thermodynamics_data import ThermodynamicsData


@pytest.fixture(scope="module")
def database_directories() -> List[str]:
    from agox.test.test_utils import test_folder_path

    test_folder_path = Path(test_folder_path)
    database_directories = [
        test_folder_path / "datasets/databases/bh_test_databases/",
        test_folder_path / "datasets/databases/rss_test_databases/",
    ]
    return database_directories


@pytest.fixture(scope="module")
def search_data(database_directories: List[Path]) -> SearchData:
    return SearchData(database_directories[0], reload=True)


@pytest.fixture(scope="module")
def search_collection(database_directories: List[Path]) -> SearchCollection:
    search_collection = SearchCollection(reload=True)
    for directory in database_directories:
        search_collection.add_directory(directory=directory, label=str(directory))

    return search_collection


@pytest.fixture(scope="module", params=["indices", "iterations"])
def energy_property(request: pytest.FixtureRequest) -> EnergyProperty:
    time_axis = request.param
    prop = EnergyProperty(time_axis)
    return prop


@pytest.fixture(scope="module")
def energy_array_prop(search_data: SearchData, energy_property: EnergyProperty) -> ArrayPropertyData:
    return energy_property.compute(search_data)

@pytest.fixture(scope="module", params=['indices', 'iterations'])
def free_energy_property(request: pytest.FixtureRequest) -> FreeEnergyProperty:
    """
    Todo: Not working yet, need to fix it on the GC branch.
    """
    references = {'Ni': 0, 'Au': 0}
    chemical_potentials = {'Ni': 0, 'Au': 0}

    time_axis = request.param
    thermo_data = ThermodynamicsData(references=references, chemical_potentials=chemical_potentials)
    prop = FreeEnergyProperty(thermo_data=thermo_data, time_axis=time_axis)
    return prop

@pytest.fixture(scope="module")
def free_energy_array_prop(search_data: SearchData, energy_property: EnergyProperty) -> ArrayPropertyData:
    return energy_property.compute(search_data)
