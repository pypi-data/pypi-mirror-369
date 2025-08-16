from typing import Callable

import pytest

from agox.candidates import Candidate
from agox.samplers.replica_exchange import ReplicaExchangeSample
from agox.samplers.replica_exchange.sample import SampleMember


@pytest.fixture(scope='function')
def empty_sample() -> ReplicaExchangeSample:
    return ReplicaExchangeSample(10)

@pytest.fixture(scope='function')
def sample(candidate_factory: Callable[[int], list[Candidate]]) -> ReplicaExchangeSample:
    sample_size = 10
    sample = ReplicaExchangeSample(sample_size)
    candidates = candidate_factory(sample_size)
    for i, candidate in enumerate(candidates):
        sample.update(i, candidate, candidate.get_potential_energy())
    return sample

def test_sample(sample: ReplicaExchangeSample) -> None:
    assert isinstance(sample, ReplicaExchangeSample)

def test_sample_getitem(sample: ReplicaExchangeSample) -> None:
    assert isinstance(sample[0], SampleMember)

def test_sample_setitem(sample: ReplicaExchangeSample, candidate_factory: Callable) -> None:
    sample[0] = candidate_factory(1)[0]
    assert isinstance(sample[0], SampleMember)

def test_sample_swap(sample: ReplicaExchangeSample) -> None:
    e0 = sample[0].get_energy()
    e1 = sample[1].get_energy()
    c0 = sample[0].candidate
    c1 = sample[1].candidate

    sample.swap(0, 1)
    assert sample[0].get_energy() == e1
    assert sample[1].get_energy() == e0

    assert sample[0].candidate == c1
    assert sample[1].candidate == c0
    assert sample[0] != c0
    assert sample[1] != c1

def test_empty_sample_is_empty(empty_sample: ReplicaExchangeSample) -> None:
    assert all([sample.empty() for sample in empty_sample.sample])

def test_sample_is_not_empty(sample: ReplicaExchangeSample) -> None:
    assert not all([sample.empty() for sample in sample.sample])

def test_sample_update(sample: ReplicaExchangeSample, candidate_factory: Callable) -> None:

    initial_energies = [sample[i].get_energy() for i in range(len(sample.sample))]

    candidates = candidate_factory(10)
    new_energies_unset = [candidate.get_potential_energy() for candidate in candidates]

    for i, candidate in enumerate(candidates):
        sample.update(i, candidate, candidate.get_potential_energy())

    new_energies_set = [sample[i].get_energy() for i in range(len(sample.sample))]

    assert initial_energies != new_energies_unset
    assert new_energies_unset == new_energies_set

def test_sample_len(sample: ReplicaExchangeSample) -> None:
    assert len(sample) == len(sample.sample)

def test_sample_iter(sample: ReplicaExchangeSample) -> None:
    for sample_member in sample:
        assert isinstance(sample_member, SampleMember)

    