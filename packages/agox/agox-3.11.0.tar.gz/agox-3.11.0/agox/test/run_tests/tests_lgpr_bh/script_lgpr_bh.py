import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms
from ase.optimize import BFGS

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RattleGenerator
from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.postprocessors import RelaxPostprocess
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
    symbols="Au8Ni8",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=5)

##############################################################################
# Search Settings:
##############################################################################

kernel = C(1, (1, 100)) * RBF(20, (10, 30))
descriptor = SOAP(
    environment=environment,
    r_cut=5.0,
    nmax=3,
    lmax=2,
    sigma=1,
    weight=True,
    periodic=False,
)

model = SparseGPR(
    database=database,
    kernel=kernel,
    descriptor=descriptor,
    n_optimize=0,
    noise=0.01,  # eV/atom
    iteration_start_training=0,
    jitter=1e-4,  # only for CI testing
)

# Number of steps is very low - should be set higher for a real search!
relaxer = RelaxPostprocess(model, optimizer=BFGS, order=2, optimizer_run_kwargs={"steps": 5, "fmax": 0.1})

sampler = MetropolisSampler(temperature=0.25, order=4)

rattle_generator = RattleGenerator(**environment.get_confinement(), environment=environment, sampler=sampler, order=1)

# With the model pre-relax we dont want to take many steps in the real potential!
# As we are training the model all the data is saved with the store_trajectory argument.
evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "candidates"},
    store_trajectory=True,
    optimizer_run_kwargs={"fmax": 0.05, "steps": 3},
    order=3,
    constraints=environment.get_constraints(),
)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(rattle_generator, database, sampler, evaluator, relaxer, seed=seed)

agox.run(N_iterations=10)
