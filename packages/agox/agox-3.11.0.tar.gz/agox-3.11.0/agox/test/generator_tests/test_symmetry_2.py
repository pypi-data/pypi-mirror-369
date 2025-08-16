import numpy as np
from ase import Atoms

from agox.candidates import CandidateBaseClass
from agox.environments.environment import Environment
from agox.generators import SymmetryGenerator, SymmetryPermutationGenerator, SymmetryRattleGenerator
from agox.samplers.fixed_sampler import FixedSampler


def environment_factory():
    template = Atoms("", cell=np.eye(3) * 22, pbc=False)
    confinement_corner = np.array([5.5, 5.5, 5.5])
    confinement_cell = np.eye(3) * 11
    environment = Environment(
        template=template, symbols="B12N12", confinement_corner=confinement_corner, confinement_cell=confinement_cell
    )
    return environment


def generator_factory(environment):
    generator = SymmetryGenerator(
        sym_type="cluster", force_group="D6", may_nucleate_at_several_places=True, **environment.get_confinement()
    )
    return generator


def rattle_generator_factory(environment):
    rattle_generator = SymmetryRattleGenerator(**environment.get_confinement(), let_lose_sym=1.0)
    return rattle_generator


def permutation_generator_factory(environment):
    permutation_generator = SymmetryPermutationGenerator(**environment.get_confinement())
    return permutation_generator


def test_symmetry_generator():
    np.random.seed(1)
    environment = environment_factory()
    generator = generator_factory(environment)
    candidate = generator(None, environment)[0]
    assert isinstance(candidate, CandidateBaseClass)


def test_symmetry_rattle_generator():
    np.random.seed(1)
    environment = environment_factory()
    generator = generator_factory(environment)
    rattle_generator = rattle_generator_factory(environment)
    symmetry_candidate = generator(None, environment)[0]
    sampler = FixedSampler(symmetry_candidate)
    candidate = rattle_generator(sampler, environment)[0]
    assert isinstance(candidate, CandidateBaseClass)


def test_symmetry_permutation_generator():
    np.random.seed(1)
    environment = environment_factory()
    generator = generator_factory(environment)
    permutation_generator = permutation_generator_factory(environment)
    symmetry_candidate = generator(None, environment)[0]
    sampler = FixedSampler(symmetry_candidate)
    candidate = permutation_generator(sampler, environment)[0]
    assert isinstance(candidate, CandidateBaseClass)
