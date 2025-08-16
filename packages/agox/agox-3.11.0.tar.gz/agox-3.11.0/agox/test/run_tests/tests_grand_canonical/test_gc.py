from agox.test.run_tests.run_utils import agox_test_run
import pytest

def test_bh(tmp_path, cmd_options):
    mode = "gc"
    agox_test_run(mode, tmp_path, cmd_options, full_compare=False)