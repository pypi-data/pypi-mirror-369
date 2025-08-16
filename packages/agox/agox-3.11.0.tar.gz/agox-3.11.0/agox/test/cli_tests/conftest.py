from pathlib import Path
from typing import List

import pytest

from agox.analysis.search_data import SearchCollection


@pytest.fixture(scope="module")
def database_directories() -> List[Path]:
    from agox.test.test_utils import test_folder_path

    test_folder_path = Path(test_folder_path)
    database_directories = [
        test_folder_path / "datasets/databases/bh_test_databases/",
        test_folder_path / "datasets/databases/rss_test_databases/",
    ]
    return database_directories


@pytest.fixture(scope="module")
def database_file_path() -> Path:
    from agox.test.test_utils import test_folder_path

    test_folder_path = Path(test_folder_path)
    database_file_path = test_folder_path / "datasets/databases/bh_test_databases/db1.db"

    return database_file_path


@pytest.fixture(scope="module")
def trajectory_file_path() -> Path:
    from agox.test.test_utils import test_folder_path

    test_folder_path = Path(test_folder_path)
    trajectory_file_path = test_folder_path / "datasets/AgO-dataset.traj"

    return trajectory_file_path


@pytest.fixture(scope="module")
def search_collection(database_directories: List[Path]) -> SearchCollection:
    search_collection = SearchCollection(reload=False)
    for directory in database_directories:
        search_collection.add_directory(directory=directory, label=str(directory))

    return search_collection
