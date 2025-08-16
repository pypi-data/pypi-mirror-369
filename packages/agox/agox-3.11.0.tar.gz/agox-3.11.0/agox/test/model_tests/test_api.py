
import pytest



@pytest.mark.ray
def test_local(tmp_path):
    pass


# @pytest.mark.ray
# def test_local_forces(tmp_path):
#     with TemporaryFolder(tmp_path):
#         import agox.test.model_tests.sgpr_api_forces

# @pytest.mark.ray
# def test_global(tmp_path):
#     with TemporaryFolder(tmp_path):
#         import agox.test.model_tests.gpr_api

# @pytest.mark.ray
# def test_descriptors(tmp_path):
#     with TemporaryFolder(tmp_path):
#         import agox.test.model_tests.descriptors_api
