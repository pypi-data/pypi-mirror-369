import pytest

from agox.models.descriptors import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
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

kernel = C() * RBF() + Noise(0.01)
model_class = GPR
model_maker = GPR
model_base_args = []
model_base_kwargs = {"use_ray": False}

model_update_kwargs = [{"kernel": kernel}]

model_update_kwargs = label_dict_list(model_update_kwargs)


@pytest.fixture(params=model_update_kwargs)
def update_kwargs(request):
    return request.param


@pytest.mark.ray
@pytest.mark.parametrize("test_data_dict", test_data_dicts)
def test_model(test_data_dict, update_kwargs, cmd_options):
    create_mode = cmd_options["create_mode"]
    test_mode = not create_mode
    tolerance = cmd_options["tolerance"]

    update_kwargs, parameter_index = update_kwargs

    path = test_data_dict["path"]
    remove = test_data_dict["remove"]
    dataset_name = test_data_dict["name"]
    parameter_index = 0

    environment = get_test_environment(path, remove)
    data = get_test_data(path, environment)

    # Update the kwargs for the model.
    descriptor = Fingerprint(environment=environment)
    update_kwargs["descriptor"] = descriptor

    model_kwargs = model_base_kwargs.copy()
    model_kwargs.update(update_kwargs)

    # Where to load/save data.
    subfolder = "model_tests/"
    module_name = "GlobalGPR"
    name = get_name(module_name, subfolder, dataset_name, parameter_index)
    if test_mode:
        expected_data = load_expected_data(name)
    else:
        expected_data = None

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
