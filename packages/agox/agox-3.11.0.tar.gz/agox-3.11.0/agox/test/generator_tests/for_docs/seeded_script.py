import numpy as np
from ase import Atoms

from agox.environments import Environment
from agox.generators import RandomGenerator, RattleGenerator
from agox.samplers import FixedSampler

template = Atoms("", cell=np.eye(3) * 12)
confinement_cell = np.eye(3) * 6
confinement_corner = np.array([3, 3, 3])
environment = Environment(
    template=template,
    symbols="Au8Ni8",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

random_generator = RandomGenerator(**environment.get_confinement())

rattle_generator = RattleGenerator(**environment.get_confinement())

random_candidate = random_generator(sampler=None, environment=environment)

sampler = FixedSampler(random_candidate)

rattle_candidate = rattle_generator(sampler, environment)

print(f"{rattle_candidate = }")
