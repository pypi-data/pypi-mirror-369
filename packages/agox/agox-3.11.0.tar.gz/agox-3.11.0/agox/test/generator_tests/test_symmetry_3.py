import pytest

from agox.candidates import CandidateBaseClass
from agox.generators import SymmetryGenerator
from agox.helpers.confinement import Confinement


@pytest.fixture(scope="module")
def random_symmetry_cluster_generator():
    def make_generator(environment):
        generator = SymmetryGenerator(**environment.get_confinement(), sym_type="cluster")
        return generator

    return make_generator


@pytest.fixture(scope="module")
def random_symmetry_cluster_candidate(random_symmetry_cluster_generator, test_environment_non_periodic):
    generator = random_symmetry_cluster_generator(test_environment_non_periodic)

    candidate = None
    attempt = 0
    while candidate is None and attempt < 100:  # This is bad, but...
        generator_output = generator(None, test_environment_non_periodic)
        attempt += 1

        if len(generator_output) > 0:
            candidate = generator_output[0]

    return candidate


def test_output_type(random_symmetry_cluster_candidate):
    assert isinstance(random_symmetry_cluster_candidate, CandidateBaseClass)


def test_output_symmetry_type(random_symmetry_cluster_candidate):
    space_group = random_symmetry_cluster_candidate.get_meta_information("space_group")
    assert isinstance(space_group, str)


def test_confinement(random_symmetry_cluster_candidate, test_environment_non_periodic):
    indices = test_environment_non_periodic.get_missing_indices()
    positions = random_symmetry_cluster_candidate.positions[indices, :]
    confinement = test_environment_non_periodic.get_confinement(as_dict=False)
    assert confinement.check_confinement(positions).all()


def test_template(random_symmetry_cluster_candidate, test_environment_non_periodic):
    template = test_environment_non_periodic.get_template()
    assert (random_symmetry_cluster_candidate.positions[0 : len(template)] == template.positions).all()


def test_cell(random_symmetry_cluster_candidate, test_environment_non_periodic):
    assert (random_symmetry_cluster_candidate.cell == test_environment_non_periodic.get_template().get_cell()).all()
