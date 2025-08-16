from agox.test.run_tests.run_utils import agox_test_run
import pytest 

@pytest.mark.skip(reason="Somehow doesn't work on CI")
def test_md_bh(tmp_path, cmd_options):
    mode = "md_bh"  # This determines the script that is imported.
    agox_test_run(mode, tmp_path, cmd_options)
