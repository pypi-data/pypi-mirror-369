import numpy as np
import pytest

from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.test.model_tests.model_utils import model_tester
from agox.test.test_utils import (
    check_file_is_deleted,
    get_name,
    get_test_data,
    get_test_environment,
    label_dict_list,
    load_expected_data,
    save_expected_data,
    test_data_dicts,
)

# Weird kernel specification is because of accurcay in Sklearn that does such a conversion.
kernel = C(1.0) * RBF(length_scale=np.exp(np.log(20.0)))
model_class = SparseGPR
model_maker = SparseGPR
model_base_args = []
model_base_kwargs = {}

model_update_kwargs = [
    {
        "kernel": kernel,
        "noise_E": 0.05,
        "noise_F": 0.5,
        "force_data_filter": "all",
        "database": None,
        "use_ray": False,
        "jitter": 5e-3,
    },
]

model_update_kwargs = label_dict_list(model_update_kwargs)


@pytest.fixture(params=model_update_kwargs)
def update_kwargs(request):
    return request.param


@pytest.mark.ray
@pytest.mark.parametrize("test_data_dict", test_data_dicts)
def test_model(test_data_dict, update_kwargs, cmd_options):
    # pytest.skip('This test is not yet working, due to tolerances on different machines making it unreliable.')

    create_mode = cmd_options["create_mode"]
    test_mode = not create_mode
    tolerance = cmd_options["tolerance"]
    tolerance["atol"] = 1e-4
    tolerance["rtol"] = 1e-2

    update_kwargs, parameter_index = update_kwargs

    path = test_data_dict["path"]
    remove = test_data_dict["remove"]
    dataset_name = test_data_dict["name"]
    parameter_index = 0

    # Gather environment and data:
    environment = get_test_environment(path, remove)
    data = get_test_data(path, environment)

    # Update the kwargs for the model.
    descriptor = SOAP(environment=environment, periodic=environment.get_template().pbc.any())
    update_kwargs["descriptor"] = descriptor
    # Slightly complicated way of building input args & kwargs:
    if "environment" in update_kwargs.keys():
        update_kwargs["environment"] = environment

    model_kwargs = model_base_kwargs.copy()
    model_kwargs.update(update_kwargs)

    # Where to load/save data.
    subfolder = "model_tests/"
    module_name = "LocalSparseGPRForces"
    name = get_name(module_name, subfolder, dataset_name, parameter_index)
    if test_mode:
        expected_data = load_expected_data(name)
    else:
        expected_data = None

    np.random.seed(42)
    output = model_tester(
        model_maker,
        model_base_args,
        model_kwargs,
        data,
        test_mode=test_mode,
        expected_data=expected_data,
        tolerance=tolerance,
    )

    if not test_mode:
        check_file_is_deleted(name)
        save_expected_data(name, output)
