import pytest

from agox.test.run_tests.run_utils import agox_test_run


@pytest.mark.ray
def test_ce_gofee(tmp_path, cmd_options):
    mode = "ce_default_gofee"  # This determines the script that is imported.
    agox_test_run(mode, tmp_path, cmd_options)
