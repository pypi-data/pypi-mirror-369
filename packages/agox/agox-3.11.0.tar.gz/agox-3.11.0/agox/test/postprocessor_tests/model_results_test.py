import pytest
from ase.calculators.singlepoint import SinglePointCalculator

from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.postprocessors import ParallelRelaxPostprocess, RelaxPostprocess


def make_model(environment, dataset):
    model = GPR(
        descriptor=Fingerprint(environment=environment),
        kernel=C() * RBF() + Noise(0.01),
        database=None,
    )
    model.train(dataset)
    return model


@pytest.mark.ray
@pytest.mark.parametrize(
    "postprocess_class",
    [RelaxPostprocess, ParallelRelaxPostprocess],
)
def test_postprocess_results(postprocess_class, environment_and_dataset):
    environment, dataset = environment_and_dataset
    postprocessor = postprocess_class(model=make_model(environment, dataset), optimizer_run_kwargs={"steps": 1})

    try:
        candidates = [postprocessor.postprocess(dataset[0])]
    except NotImplementedError:
        candidates = postprocessor.process_list(dataset[0:8])

    assert len(candidates) > 0

    for candidate in candidates:
        assert isinstance(candidate.calc, SinglePointCalculator)
        assert candidate.get_potential_energy() != 0
