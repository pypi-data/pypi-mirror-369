import pytest

from agox.test.run_tests.run_utils import agox_test_run


def test_schnet_bh(tmp_path, cmd_options):
    pytest.skip("This test is not designed to run on the CI")
    mode = "schnet_bh"  # This determines the script that is imported.
    options = {"tolerance": {"rtol": 1e-03, "atol": 1e-03}, "create_mode": cmd_options["create_mode"]}
    agox_test_run(mode, tmp_path, options)
