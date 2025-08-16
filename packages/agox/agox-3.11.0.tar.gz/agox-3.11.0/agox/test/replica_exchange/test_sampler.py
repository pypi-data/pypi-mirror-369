from agox.candidates import Candidate
from agox.samplers.replica_exchange import ReplicaExchangeSampler


def test_bare_sampler_type(bare_sampler: ReplicaExchangeSampler) -> None:
    assert isinstance(bare_sampler, ReplicaExchangeSampler)


def test_bare_sampler_is_empty(bare_sampler: ReplicaExchangeSampler) -> None:
    for sample_member in bare_sampler.sample:
        assert sample_member.empty()


def test_sampler_not_empty(sampler: ReplicaExchangeSampler) -> None:
    for sample_member in sampler.sample:
        assert not sample_member.empty()


def test_sampler_get_walker_type(sampler: ReplicaExchangeSampler) -> None:
    for i in range(sampler.sample_size):
        walker = sampler.get_walker(i)
        assert isinstance(walker, Candidate)


def test_sampler_members_have_calculators(sampler: ReplicaExchangeSampler) -> None:
    for walker in sampler.sample:
        if not walker.empty():
            assert walker.candidate.calc is not None


def test_sampler_energy_match(sampler: ReplicaExchangeSampler) -> None:
    for walker in sampler.sample:
        assert walker.get_energy() == walker.candidate.get_potential_energy()
