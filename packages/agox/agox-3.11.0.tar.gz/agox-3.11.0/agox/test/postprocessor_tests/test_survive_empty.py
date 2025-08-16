import pytest

from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.postprocessors import CenteringPostProcess, ParallelRelaxPostprocess, RelaxPostprocess, WrapperPostprocess


def base_setup(environment, dataset):
    return {}


def make_model(environment, dataset):
    model = GPR(descriptor=Fingerprint(environment=environment), kernel=C() * RBF() + Noise(0.01), database=None)
    model.train(dataset)
    return {"model": model}


@pytest.mark.ray
@pytest.mark.parametrize(
    "postprocess_class, setup_kwargs, setup_func",
    [
        (CenteringPostProcess, {}, base_setup),
        (WrapperPostprocess, {}, base_setup),
        (RelaxPostprocess, {"optimizer_run_kwargs": {"steps": 10}}, make_model),
        (ParallelRelaxPostprocess, {"optimizer_run_kwargs": {"steps": 10}}, make_model),
    ],
)
def test_postprocess(postprocess_class, setup_kwargs, setup_func, environment_and_dataset):
    environment, dataset = environment_and_dataset
    postprocessor = postprocess_class(**setup_kwargs, **setup_func(environment, dataset))

    postprocessor.process_list([])
