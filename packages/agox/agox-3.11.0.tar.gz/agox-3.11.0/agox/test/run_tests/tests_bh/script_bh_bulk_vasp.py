import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms

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

from ase.calculators.vasp import Vasp

nslots = 8  # Number of cores
calc = Vasp(
    command="mpirun -np {} vasp".format(nslots),
    prec="Low",
    lreal=False,
    lwave=False,
    xc="PBE",
    nwrite=2,
    istart=1,
    icharg=1,
    ispin=1,
    voskown=1,
    lmaxmix=6,
    nelm=500,
    nelmin=4,
    ibrion=-1,
    potim=0.3,
    iwavpr=1,
    nsw=0,
    ialgo=38,
    ismear=0,
    sigma=0.1,
    lorbit=11,
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
database = Database(filename=db_path, order=4)

##############################################################################
# Search Settings:
##############################################################################

sampler = MetropolisSampler(temperature=0.25, order=3)

rattle_generator = RattleGenerator(**environment.get_confinement(), environment=environment, sampler=sampler, order=1)

# Wont relax fully with steps:5 - more realistic setting would be 100+.
from ase.calculators.calculator import CalculationFailed
from ase.calculators.vasp import Vasp

def callback(candidate):
    if isinstance(candidate.calc, Vasp) and not candidate.calc.read_convergence():
        raise CalculationFailed('VASP: SCF not converged')

evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "candidates"},
    optimizer_run_kwargs={"fmax": 0.05, "steps": 5},
    store_trajectory=False,
    order=2,
    constraints=environment.get_constraints(),
    check_callback=callback,
)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(rattle_generator, database, sampler, evaluator, seed=seed)

agox.run(N_iterations=10)
