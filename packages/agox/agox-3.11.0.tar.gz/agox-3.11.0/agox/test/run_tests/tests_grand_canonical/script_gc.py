import matplotlib

matplotlib.use("Agg")

import numpy as np
from ase import Atoms
from ase.build import fcc100
from ase.calculators.emt import EMT

from agox import AGOX
from agox.acquisitors import GibbsFreeEnergyAquisitor
from agox.collectors import ParallelCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import LocalOptimizationEvaluator
from agox.generators import AddRemoveGenerator, RandomGenerator, RattleGenerator
from agox.models.descriptors.soap import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.models.GPR.priors import Repulsive
from agox.postprocessors import ParallelRelaxPostprocess
from agox.samplers import GFEKMeansSampler
from agox.utils.sparsifiers import CUR
from agox.utils.thermodynamics import ThermodynamicsData

seed = 42
database_index = 0

##############################################################################
# System & general settings:
##############################################################################

# Define a template surface using ASE functions.
template = fcc100("Cu", size=(3, 3, 2), vacuum=5.0)
template.pbc = [True, True, False]
template.positions[:, 2] -= template.positions[:, 2].min()

# Confinement cell matches the template cell in x & y but is smaller in z.
confinement_cell = template.cell.copy()
confinement_cell[2, 2] = 4.0

# Confinement corner is at the origin of the template cell, except in z where
# it is shifted up.
z0 = template.positions[:, 2].max()
confinement_corner = np.array([0, 0, z0])  # Confinement corner is at cell origin

# The environment now specifies a range of how many atoms of each species can be
# present in the system.
environment = Environment(
    template=template,
    symbols_range={"Cu": [5, 6, 7], "O": [3, 4]},
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[True, True, False],  # Confinement is not periodic in z
)

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=7)

##############################################################################
# Calculator
##############################################################################

calc = EMT()

################################################################################
# Reference energies.
################################################################################

# References energies should be correctly calculated, e.g. from molecular oxygen
# and energy differences between Cu-slabs of different thickness.
references = {"Cu": 0, "O": -1.0}
chemical_potentials = {"Cu": 0, "O": -1.0}  # Choice of chemical potential.
thermo_data = ThermodynamicsData(references, chemical_potentials)

##############################################################################
# Search Settings:
##############################################################################

descriptor = SOAP(
    environment=environment,
    r_cut=6,
    nmax=3,
    lmax=2,
    sigma=1,
    weight=True,
    periodic=True,
)
kernel = C(1, (1, 100)) * RBF(20, (10, 30))

single_atom_energies = np.zeros(100)
for symbol in references.keys():
    number = Atoms(symbol).numbers[0]
    single_atom_energies[number] = references[symbol]

model = SparseGPR(
    descriptor=descriptor,
    kernel=kernel,
    database=database,
    sparsifier=CUR(1000),  
    sigma=0.01,
    prior=Repulsive(),
    train_uncertainty=True,
    single_atom_energies=single_atom_energies,
)

sample_size = 10
sampler = GFEKMeansSampler(
    thermo_data=thermo_data,
    model=model,
    descriptor=descriptor,
    database=database,
    sample_size=sample_size,
)
rattle_generator = RattleGenerator(**environment.get_confinement())
random_generator = RandomGenerator(**environment.get_confinement(), contiguous=False)
addrm_generator = AddRemoveGenerator(**environment.get_confinement())

# Dict specificies how many candidates are created with and the dict-keys are iterations.
generators = [random_generator, rattle_generator, addrm_generator]
num_candidates = {0: [10, 0, 0], 5: [2, 4, 4]}

# Acquisitor that uses the Gibbs free energy to select candidates.
acquisitor = GibbsFreeEnergyAquisitor(
    thermo_data=thermo_data,
    model=model,
    kappa=1,
    order=3,
)
# CPU-count is set here for Ray - leave it out to use as many cores as are available.
collector = ParallelCollector(
    generators=generators,
    sampler=sampler,
    environment=environment,
    num_candidates=num_candidates,
    order=1,
)
# Number of steps is very low - should be set higher for a real search!
relaxer = ParallelRelaxPostprocess(
    model=acquisitor.get_acquisition_calculator(),
    constraints=environment.get_constraints(),
    optimizer_run_kwargs={"steps": 5},
    start_relax=8,
    order=2,
)

evaluator = LocalOptimizationEvaluator(
    calc,
    gets={"get_key": "prioritized_candidates"},
    optimizer_kwargs={"logfile": None},
    store_trajectory=True,
    optimizer_run_kwargs={"fmax": 0.05, "steps": 0},
    order=6,
)
##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(collector, acquisitor, relaxer, database, evaluator, seed=seed)

agox.run(N_iterations=10)
