import pytest

from agox.test.run_tests.run_utils import agox_test_run


@pytest.mark.parametrize("mode", ["rss_cluster_emt", "rss_bulk_emt", "rss_surface_emt", "rss_2d"])
def test_rss(mode, tmp_path, cmd_options):
    agox_test_run(mode, tmp_path, cmd_options)
