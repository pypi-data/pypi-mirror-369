import pytest

from agox.test.run_tests.run_utils import agox_test_run


@pytest.mark.ray
@pytest.mark.parametrize("mode", ["gofee_cluster_emt", "gofee_surface_emt", "gofee_bulk_emt"])
def test_gofee(mode, tmp_path, cmd_options, ray_fix):
    agox_test_run(mode, tmp_path, cmd_options)
