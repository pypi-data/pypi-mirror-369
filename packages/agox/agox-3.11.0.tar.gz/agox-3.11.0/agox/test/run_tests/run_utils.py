import os
from importlib import import_module
from pathlib import Path

import numpy as np

from agox.databases import Database
from agox.test.test_utils import TemporaryFolder, check_folder_is_empty, compare_candidates, test_folder_path


def agox_test_run(mode, tmp_path, cmd_options, full_compare=True):
    # Find the path to the current test file
    repo_path = Path(test_folder_path).parent.parent
    env_vars = os.getenv("PYTEST_CURRENT_TEST").split("::")[0]
    test_path = Path(env_vars).parent
    expected_path = repo_path / test_path / "expected_outputs" / f"{mode}_test"

    # Find the script path:
    rel_script_path = test_path / f"script_{mode}.py"
    full_script_path = repo_path / rel_script_path
    script_import = str(rel_script_path).replace("/", ".").replace(".py", "")

    # Check mode & tolerance
    create_mode = cmd_options["create_mode"]
    test_mode = not create_mode
    tolerance = cmd_options["tolerance"]

    if create_mode:
        tmp_path = expected_path
        check_folder_is_empty(tmp_path)

    # Prints for helping later:
    print("====== Test information ======")
    print(f"\tExpected results path: \n\t\t{expected_path}")
    print(f"\tScript path: \n\t\t{full_script_path}")
    print(f"\tScript import: \n\t\t{script_import}")
    print("")

    with TemporaryFolder(tmp_path):
        # This loads the database file from the script file.
        # This means that the documentation can link to this run-file.
        database = import_module(script_import).database

        if test_mode:
            expected_database = Database(f"{expected_path}/db0.db")
            compare_runs(database, expected_database, tolerance, full_compare=full_compare)


def compare_runs(database, expected_database, tolerance, full_compare=True):
    test_candidates = database.get_all_candidates()
    test_energies = database.get_all_energies()

    # Saved database:
    expected_database.restore_to_memory()
    expected_candidates = expected_database.get_all_candidates()
    expected_energies = expected_database.get_all_energies()

    np.testing.assert_allclose(expected_energies, test_energies, **tolerance)

    if full_compare:
        for candidate, expected_candidate in zip(test_candidates, expected_candidates):
            assert compare_candidates(
                candidate, expected_candidate, tolerance
            ), f"Candidates dont match. {candidate.positions = } {expected_candidate.positions = }"

        assert len(expected_candidates) == len(test_candidates), "Different numbers of candidates."

        expected_positions = np.vstack([atoms.get_positions() for atoms in expected_candidates])
        test_positions = np.vstack([atoms.get_positions() for atoms in test_candidates])

        np.testing.assert_allclose(expected_energies, test_energies, **tolerance)
        np.testing.assert_allclose(expected_positions, test_positions, **tolerance)
