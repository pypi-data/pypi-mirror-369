import pytest

from agox.candidates.ABC_candidate import CandidateBaseClass
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.samplers import (
    DistanceComparator,
    FixedSampler,
    GeneticSampler,
    KernelSimSampler,
    KMeansSampler,
    MetropolisSampler,
    SpectralGraphSampler,
)
from agox.test.test_utils import TemporaryFolder


def base_setup(environment, dataset):
    def args_func(dataset):
        return []

    return {"args_func": args_func}


def kmeans_setup(environment, dataset):
    descriptor = Fingerprint(environment=environment)
    model = GPR(descriptor=descriptor, kernel=C() * RBF() + Noise(0.01), database=None, use_ray=False)

    model.train(dataset[0:10])

    def args_func(dataset):
        return []

    return {"model": model, "descriptor": descriptor, "args_func": args_func}


def kernel_sim_setup(environment, dataset):
    descriptor = Fingerprint(environment=environment)
    kernel = C() * RBF() + Noise(0.01)
    model = GPR(descriptor=descriptor, kernel=kernel, database=None, use_ray=False)

    model.train(dataset[0:10])

    def args_func(dataset):
        return []

    return {
        "model": model,
        "descriptor": descriptor,
        "args_func": args_func,
        "kernel": None,
    }


def genetic_setup(environment, dataset):
    descriptor = Fingerprint.from_atoms(dataset[0])
    comparator = DistanceComparator(descriptor, 0.05)

    def args_func(dataset):
        return [dataset]

    return {"comparator": comparator, "args_func": args_func}


def spectral_graph_setup(environment, dataset):
    descriptor = Fingerprint(environment=environment)
    model = GPR(descriptor=descriptor, kernel=C() * RBF() + Noise(0.01), database=None, use_ray=False)
    model.train(dataset[0:10])

    def args_func(dataset):
        return []

    return {"model_calculator": model, "args_func": args_func}


def fixed_sampler_setup(environment, dataset):
    def args_func(dataset):
        return []

    return {"args_func": args_func, "sample": dataset[0:10]}


@pytest.mark.parametrize(
    "sampler_class, setup_kwargs, setup_func",
    [
        [KMeansSampler, {}, kmeans_setup],
        [MetropolisSampler, {}, base_setup],
        [GeneticSampler, {}, genetic_setup],
        [SpectralGraphSampler, {}, spectral_graph_setup],
        [KernelSimSampler, {}, kernel_sim_setup],
        [FixedSampler, {}, fixed_sampler_setup],
    ],
)
def test_sampler(sampler_class, setup_kwargs, setup_func, environment_and_dataset, tmp_path):
    with TemporaryFolder(tmp_path):
        environment, dataset = environment_and_dataset

        additional_kwargs = setup_func(environment, dataset)
        args_func = additional_kwargs.pop("args_func")
        sampler = sampler_class(**setup_kwargs, **additional_kwargs)
        sampler.iteration_counter = 0

        if not sampler.initialized:
            candidate = sampler.get_parents()  # Empty sampler should return [].
            assert candidate == []

        sampler.setup(dataset, *args_func(dataset))
        member = sampler.get_parents()
        all_members = sampler.get_all_members()
        member_calc = sampler.get_parents()

        assert issubclass(member[0].__class__, CandidateBaseClass)
        assert isinstance(all_members, list)
        assert member_calc[0].get_potential_energy()
        assert len(sampler) != 0
        assert len(sampler) == len(all_members)
