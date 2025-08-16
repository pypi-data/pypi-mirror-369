import pytest

from agox.test.run_tests.run_utils import agox_test_run


@pytest.mark.parametrize("mode", ["bh_cluster_emt", "bh_surface_emt", "bh_bulk_emt"])
def test_bh(mode, tmp_path, cmd_options):
    agox_test_run(mode, tmp_path, cmd_options)
