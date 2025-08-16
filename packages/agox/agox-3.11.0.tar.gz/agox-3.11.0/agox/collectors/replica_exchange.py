from dataclasses import dataclass
from typing import Optional

import numpy as np

import ray
from agox.candidates import Candidate
from agox.collectors.ABC_collector import CollectorBaseClass
from agox.environments import Environment
from agox.generators import Generator
from agox.samplers import Sampler
from agox.samplers.fixed_sampler import FixedSampler
from agox.utils.ray import RayPoolUser


@dataclass
class Walker:
    index: int
    generator_index: int
    generator_pool_id: str

    @property
    def name(self) -> str:
        return f"walker-{self.index}"

def remote_generate(generator: Generator, sampler: Sampler, environment: Environment, walker: Walker) -> list[Candidate]:
    candidates = generator(sampler, environment)
    if len(candidates) == 1:
        candidate = candidates[0]
        candidate.add_meta_information("walker_index", walker.index)
    else:
        candidate = None
    return candidate


@dataclass
class DynamicGeneratorInfo:
    attribute: str
    correlated: bool
    caps: list[float]


class ReplicaExchangeCollector(CollectorBaseClass, RayPoolUser):
    name = "RepliceExchangeCollector"

    """
    Parameters
    ----------
    """

    def __init__(
        self, generator_dict: dict[int, Generator], fallback_generator: Optional[Generator] = None, **kwargs
    ) -> None:
        # Get the kwargs that are relevant for RayPoolUser
        RayPoolUser.__init__(self)
        self.dynamic_generators = {}

        # Determine the unique generators and their pool keys.
        unique_generators = []
        walker_index_to_unique_generator = {}
        for walker_index, generator in generator_dict.items():
            if generator not in unique_generators:
                unique_generators.append(generator)
                pool_key = self.pool_add_module(generator)
            walker_index_to_unique_generator[walker_index] = (unique_generators.index(generator), pool_key)

        # Give the rest to the CollectorBaseClass.
        CollectorBaseClass.__init__(self, unique_generators, **kwargs)

        # Setup walkers
        self.walkers = []
        for walker_index, generator in generator_dict.items():
            generator_index, pool_key = walker_index_to_unique_generator[walker_index]
            assert self.generators[generator_index] is generator
            walker = Walker(walker_index, generator_index, pool_key)
            self.walkers.append(walker)

        # Fallback
        if fallback_generator is None:
            fallback_generator = self.get_fallback_generator()
        self.fallback_generator_id = self.pool_add_module(fallback_generator)

    def make_candidates(self) -> list[Candidate]:
        # Update dynamic generators, e.g. rattle amplitudes
        if len(self.dynamic_generators) != 0:
            self.update_generators()

        environment_id = ray.put(self.environment)
        args = []
        kwargs = []
        modules = []
        for walker in self.walkers:
            # Retrieve parent candidate and create a sampler
            parent = self.sampler.get_walker(walker.index)
            sampler = FixedSampler(parent)
            sampler_id = ray.put(sampler)

            args.append((sampler_id, environment_id, walker))
            kwargs.append({})

            # Determine which generator to use
            if sampler.has_none():
                modules.append([self.fallback_generator_id])
            else:
                modules.append([walker.generator_pool_id])

        # Generate in parallel using the pool.
        candidates = self.pool_map(remote_generate, modules, args, kwargs)
        candidates = [c for c in candidates if c is not None]

        return candidates

    def get_number_of_candidates(self) -> list[int]:
        return [self.sampler.sample_size]

    @classmethod
    def from_sampler(
        cls,
        sampler: Sampler,
        environment: Environment,
        amplitudes: np.array,
        generator_dict: dict[int, Generator] = None,
        random_generator_kwargs: dict | None = None,
        rattle_kwargs: dict | None = None,
        **kwargs,
    ):
        from agox.generators import RandomGenerator, RattleGenerator

        # Validate inputs
        if not len(amplitudes) == len(sampler.temperatures):
            raise ValueError("The number of amplitudes must match the number of temperatures in the sampler.")
        
        generator_dict = generator_dict or {}
        rattle_kwargs = rattle_kwargs or {}
        random_generator_kwargs = random_generator_kwargs or {}

        # Setup generators for each walker
        for walker_index in range(sampler.sample_size):
            if walker_index in generator_dict.keys():
                continue

            if walker_index == sampler.sample_size - 1:
                # Setup random generator
                generator = RandomGenerator(**environment.get_confinement(), **random_generator_kwargs)
            else:
                # Setup rattle generators
                n_atoms = len(environment.get_missing_indices())
                generator = RattleGenerator(
                    **environment.get_confinement(), 
                    rattle_amplitude=amplitudes[walker_index], 
                    n_rattle=n_atoms,
                    **rattle_kwargs
                )
            generator_dict[walker_index] = generator

        fallback_generator = RandomGenerator(**environment.get_confinement(), **random_generator_kwargs)
        return cls(generator_dict, sampler=sampler, environment=environment, order=1, fallback_generator=fallback_generator, **kwargs)

    def add_generator_update(
        self,
        walker_index: int,
        attribute: str,
        correlated: bool = False,
        min_val: float = 0.25,
        max_val: float = 2,
    ) -> None:

        found = False        
        for walker in self.walkers:
            if walker.index == walker_index:
                found = True
                break

        if not found:
            raise ValueError(f"Walker with index {walker_index} not found.")

        generator = self.generators[walker.generator_index]
        if hasattr(generator, attribute):
            temperature = self.sampler.temperatures[walker_index]
            generator.add_dynamic_attribute(attribute)
            # self.dynamic_generators[walker_index] = DynamicGeneratorInfo(
            #     attribute, correlated, [min_val * temperature, max_val * temperature]
            # )
            self.dynamic_generators[walker_index] = DynamicGeneratorInfo(
                attribute, correlated, [min_val, max_val]
            )


    def update_generators(self) -> None:
        for walker in self.walkers:
            if walker.index not in self.dynamic_generators:
                continue
            generator = self.generators[walker.generator_index]
            acceptance = self.sampler.tracker.get_acceptance_rate(
                walker.index, start=-10
            )  # Acceptance rate over the last 10 iterations.

            if acceptance.size == 0:
                continue

            info = self.dynamic_generators[walker.index]

            attribute = info.attribute
            caps = info.caps
            cap_functions = [max, min]
            correlation_factors = [0.99, 1.01]
            if not info.correlated:
                pass
            else:  # What is this doing? And why is it doing it? It will flip every time - which seems weird?
                correlation_factors.reverse()
                cap_functions.reverse()
                caps.reverse()

            # Rattle update amplitude
            if hasattr(generator, attribute):
                amplitude = getattr(generator, attribute)
                self.sampler.tracker.rattle_amplitudes[walker.index] = amplitude
                if acceptance < 0.5:
                    setattr(generator, attribute, cap_functions[0](caps[0], amplitude * correlation_factors[0]))
                else:
                    setattr(generator, attribute, cap_functions[1](caps[1], amplitude * correlation_factors[1]))
            
            self.writer.debug(f'{walker.index}: {attribute} = {getattr(generator, attribute)}')
