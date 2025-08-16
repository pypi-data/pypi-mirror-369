import pytest

from agox.candidates import CandidateBaseClass, Candidate
from agox.generators import (
    CenterOfGeometryGenerator,
    RandomGenerator,
    RattleGenerator,
    ReplaceGenerator,
    SamplingGenerator,
)
from agox.samplers import MetropolisSampler
from agox.test.test_utils import TemporaryFolder

from uuid import uuid4


@pytest.mark.parametrize(
    "generator_class",
    [RandomGenerator, RattleGenerator, ReplaceGenerator, CenterOfGeometryGenerator, SamplingGenerator],
)
class TestGenerator:
    def assertions(self, candidates, environment, sampler):
        for candidate in candidates:
            assert issubclass(candidate.__class__, CandidateBaseClass)
            assert len(candidate) == len(environment.get_all_numbers())
            assert (candidate.cell == environment.get_template().get_cell()).all()

    def setup_generator(self, generator_class, environment, **kwargs):
        return generator_class(environment=environment, **environment.get_confinement(), **kwargs)

    def setup_sampler(self, dataset: list[Candidate]):
        sampler = MetropolisSampler()
        parent = dataset[0]
        parent.add_meta_information('spawn_uuids', [uuid4()])
        sampler.sample = [dataset[0]]
        return sampler

    def test_generators(self, generator_class, environment_and_dataset, tmp_path):
        with TemporaryFolder(tmp_path):
            environment, dataset = environment_and_dataset

            generator = self.setup_generator(generator_class, environment)
            sampler = self.setup_sampler(dataset)
            candidates = [None]
            for i in range(1):
                candidates = generator(sampler, environment)
                if not candidates[0] == None:
                    break
            self.assertions(candidates, environment, sampler)

            assert (tmp_path / f"confinement_plot_{generator.name}.png").is_file()
