import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase.build import fcc100

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.samplers import MetropolisSampler

# Manually set seed and database-index
seed = 42
database_index = 0

##############################################################################
# Calculator
##############################################################################

from agox.helpers import SubprocessGPAW

calc = SubprocessGPAW(
    mode={"name": "pw", "ecut": 400},
    xc="PBE",
    kpts=(2, 2, 1),
)

##############################################################################
# System & general settings:
##############################################################################

# Define a template surface using ASE functions.
template = fcc100("Au", size=(4, 4, 2), vacuum=5.0)
template.pbc = [True, True, False]
template.positions[:, 2] -= template.positions[:, 2].min()

# Confinement cell matches the template cell in x & y but is smaller in z.
confinement_cell = template.cell.copy()
confinement_cell[2, 2] = 4.0

# Confinement corner is at the origin of the template cell, except in z where
# it is shifted up.
z0 = template.positions[:, 2].max()
confinement_corner = np.array([0, 0, z0])  # Confinement corner is at cell origin

environment = Environment(
    template=template,
    symbols="Ni8",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[True, True, False],  # Confinement is not periodic in z
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=4)

##############################################################################
# Search Settings:
##############################################################################

sampler = MetropolisSampler(temperature=0.25, order=3)

rattle_generator = RattleGenerator(**environment.get_confinement(), environment=environment, sampler=sampler, order=1)

# Wont relax fully with steps:5 - more realistic setting would be 100+.
evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "candidates"},
    store_trajectory=False,
    optimizer_run_kwargs={"fmax": 0.05, "steps": 5},
    order=2,
    constraints=environment.get_constraints(),
)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(rattle_generator, database, sampler, evaluator, seed=seed)

agox.run(N_iterations=10)
