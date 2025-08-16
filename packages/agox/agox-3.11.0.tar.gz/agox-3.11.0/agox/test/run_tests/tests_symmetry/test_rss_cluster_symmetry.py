
from agox.test.run_tests.run_utils import agox_test_run


# @pytest.mark.skip(reason='Not reproducible on CI at the moment.')
def test_rss_cluster_symmetry(tmp_path, cmd_options):
    mode = "rss_cluster_symmetry"  # This determines the script that is imported.
    agox_test_run(mode, tmp_path, cmd_options, full_compare=False)
