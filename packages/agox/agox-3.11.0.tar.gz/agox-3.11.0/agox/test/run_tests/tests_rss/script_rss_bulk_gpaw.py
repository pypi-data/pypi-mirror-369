
import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms

from agox import AGOX
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import RandomGenerator

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
    kpts=(2, 2, 2),
)

##############################################################################
# System & general settings:
##############################################################################

# Make an empty template with a cubic cell of size 6x6x6 with periodic boundary conditions
# in all directions
template = Atoms("", cell=np.eye(3) * 6, pbc=True)

# Confinement cell matches the template cell in all dimensions and is placed at
# the origin of the template cell.
confinement_cell = template.cell.copy()
confinement_corner = np.array([0, 0, 0])

environment = Environment(
    template=template,
    symbols="Au6Ni6",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[True, True, True],  # Confinement is periodic in all directions.
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=3)

##############################################################################
# Search Settings:
##############################################################################

random_generator = RandomGenerator(**environment.get_confinement(), environment=environment, order=1)

# Wont relax fully with steps:5 - more realistic setting would be 100+.
evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "candidates"},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 5},
    store_trajectory=False,
    order=2,
    constraints=environment.get_constraints(),
)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(random_generator, database, evaluator, seed=seed)

agox.run(N_iterations=10)
