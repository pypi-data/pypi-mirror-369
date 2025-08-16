
import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators.MD import MDgenerator
from agox.samplers import MetropolisSampler

# Manually set seed and database-index
seed = 42
database_index = 0

# Using argparse if e.g. using array-jobs on Slurm to do several independent searches.
# from argparse import ArgumentParser
# parser = ArgumentParser()
# parser.add_argument('-i', '--run_idx', type=int, default=0)
# args = parser.parse_args()

# seed = args.run_idx
# database_index = args.run_idx

##############################################################################
# Calculator
##############################################################################

from ase.calculators.emt import EMT

calc = EMT()

##############################################################################
# System & general settings:
##############################################################################

template = Atoms("", cell=np.eye(3) * 12)
confinement_cell = np.eye(3) * 6
confinement_corner = np.array([3, 3, 3])
environment = Environment(
    template=template,
    symbols="Au2Ni2",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=3)

##############################################################################
# Search Settings:
##############################################################################

sampler = MetropolisSampler(temperature=0.25, order=3)

generator = MDgenerator(
    **environment.get_confinement(),
    calculator=calc,
    temperature_program=[(50, 5)],  # 50 K for 5 steps
    constraints=environment.get_constraints(),
    environment=environment,
    sampler=sampler,
    order=1,
)

# Do single-point relaxation after MD
evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "candidates"},
    optimizer_run_kwargs={"steps": 0},
    store_trajectory=False,
    order=2,
    constraints=environment.get_constraints(),
)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(generator, database, sampler, evaluator, seed=seed)

agox.run(N_iterations=10)
