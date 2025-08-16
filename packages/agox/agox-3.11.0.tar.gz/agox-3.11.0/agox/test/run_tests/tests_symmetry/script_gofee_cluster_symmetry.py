import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms

from agox import AGOX
from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.collectors import ParallelCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import SymmetryGenerator, SymmetryRattleGenerator
from agox.models.descriptors.fingerprint import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.models.GPR.priors import Repulsive
from agox.postprocessors import ParallelRelaxPostprocess
from agox.samplers import KMeansSampler

# Manually set seed and database-index
seed = 40
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

template = Atoms("", cell=np.eye(3) * 25)
confinement_cell = np.eye(3) * 20
confinement_corner = np.array([2.5, 2.5, 2.5])
environment = Environment(
    template=template,
    symbols="C24",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=5)

##############################################################################
# Search Settings:
##############################################################################

# Setup a ML model.
descriptor = Fingerprint(environment=environment)
beta = 0.01
k0 = C(beta, (beta, beta)) * RBF()
k1 = C(1 - beta, (1 - beta, 1 - beta)) * RBF()
kernel = C(5000, (1, 1e5)) * (k0 + k1) + Noise(0.01, (0.01, 0.01))
model = GPR(descriptor=descriptor, kernel=kernel, database=database, prior=Repulsive())

# Sampler to choose candidates to modify using the generators.
sample_size = 10
sampler = KMeansSampler(descriptor=descriptor, database=database, sample_size=sample_size)

# Generators to produce candidates structures
random_generator = SymmetryGenerator(**environment.get_confinement(), sym_type="cluster")
rattle_generator = SymmetryRattleGenerator(**environment.get_confinement(), let_lose_sym=0.5)

# Dict specificies how many candidates are created with and the dict-keys are iterations.
generators = [random_generator, rattle_generator]
num_candidates = {0: [2, 0], 2: [0, 2]}

# Collector creates a number of structures in each iteration.
collector = ParallelCollector(
    generators=generators,
    sampler=sampler,
    environment=environment,
    num_candidates=num_candidates,
    order=1,
)

# Acquisitor to choose a candidate to evaluate in the real potential.
acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=2, order=3)

# Number of steps is very low - should be set higher for a real search!
relaxer = ParallelRelaxPostprocess(
    model=acquisitor.get_acquisition_calculator(),
    constraints=environment.get_constraints(),
    optimizer_run_kwargs={"steps": 5},
    start_relax=8,
    order=2,
)


# Evaluator to evaluate the candidates in the real potential.
evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "prioritized_candidates"},
    optimizer_kwargs={"logfile": None},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 1},
    constraints=environment.get_constraints(),
    store_trajectory=True,
    order=4,
)

##############################################################################
# Let get the show running!
##############################################################################

# The oder of things here does not matter. But it can be simpler to understand
# what the expected behaviour is if they are put in order.
agox = AGOX(collector, relaxer, acquisitor, evaluator, database, seed=seed)

agox.run(N_iterations=5)
