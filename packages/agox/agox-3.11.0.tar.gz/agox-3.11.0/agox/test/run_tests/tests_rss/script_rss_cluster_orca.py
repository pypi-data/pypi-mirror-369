
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

from ase.calculators.orca import ORCA, OrcaProfile

# Replace with path to your orca installation.
profile = OrcaProfile(command="/comm/groupstacks/chemistry/apps/orca/5.0.4/orca")

# For more details on specifying orca settings see: https://wiki.fysik.dtu.dk/ase/ase/calculators/orca.html
calc = ORCA(
    profile=profile,
    directory="orca",
    orcasimpleinput="EnGrad PBE def2-SVP",
    orcablocks="%pal nprocs 8 end",
)  # Note number of processors is set manually!


##############################################################################
# System & general settings:
##############################################################################

template = Atoms("", cell=np.eye(3) * 12)
confinement_cell = np.eye(3) * 6
confinement_corner = np.array([3, 3, 3])
environment = Environment(
    template=template,
    symbols="Au6",
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=3)

##############################################################################
# Search Settings:
##############################################################################

random_generator = RandomGenerator(
    **environment.get_confinement(),
    environment=environment,
    order=1,
)

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
