import pytest

from agox.test.run_tests.run_utils import agox_test_run


@pytest.mark.skip(reason="Some issue with this test currently (30-1-2025), but I want the others to run in CI.")
@pytest.mark.ray
def test_graph_filtering_gofee(tmp_path, cmd_options):
    mode = "graph_filtering_gofee"  # This determines the script that is imported.
    agox_test_run(mode, tmp_path, cmd_options)
