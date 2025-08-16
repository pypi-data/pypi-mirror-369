import pytest

from agox.test.run_tests.run_utils import agox_test_run


@pytest.mark.ray
def test_gofee_slab_symmetry(tmp_path, cmd_options, ray_fix):
    mode = "gofee_slab_symmetry"  # This determines the script that is imported.
    agox_test_run(mode, tmp_path, cmd_options, full_compare=False)
