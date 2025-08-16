from pathlib import Path


from agox.test.test_utils import test_folder_path

test_folder_path = Path(test_folder_path)
database_directories = {"bh": test_folder_path / "datasets/databases/bh_test_databases/"}


def test_restart_data():
    import numpy as np

    from agox.analysis.search_data import RestartData, read_database
    from agox.databases import Database

    path = database_directories["bh"] / "db1.db"
    _, candidates = read_database(path, Database)
    restart_data = RestartData(path, candidates)

    assert len(restart_data) == len(candidates)
    assert hasattr(restart_data, "identifier")
    assert isinstance(restart_data.energies, np.ndarray)
