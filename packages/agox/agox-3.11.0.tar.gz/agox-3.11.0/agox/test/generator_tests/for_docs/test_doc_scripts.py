import numpy as np

from agox.candidates import CandidateBaseClass


def test_non_seed_script():
    np.random.seed(42)
    from agox.test.generator_tests.for_docs.nonseeded_script import candidate

    assert isinstance(candidate, list)
    assert isinstance(candidate[0], CandidateBaseClass)


def test_seed_cript():
    np.random.seed(42)
    from agox.test.generator_tests.for_docs.seeded_script import rattle_candidate

    assert isinstance(rattle_candidate, list)
    assert isinstance(rattle_candidate[0], CandidateBaseClass)
