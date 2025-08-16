import numpy as np
from ase import Atoms
from chgnet.model.dynamics import CHGNetCalculator

from agox import AGOX
from agox.acquisitors import ReplicaExchangeAcquisitor
from agox.collectors import ReplicaExchangeCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import SinglePointEvaluator
from agox.helpers.gpaw_subprocess import SubprocessGPAW
from agox.models import CalculatorModel
from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.postprocessors import ParallelRelaxPostprocess
from agox.samplers import ReplicaExchangeSampler
from agox.utils.sparsifiers.CUR import CUR

##############################################################################
# General settings:
##############################################################################

seed = 42            # Random seed for reproducibility - should be set to a unique value for each run. 
database_index = 0   # Index for database file - should be unique for each run to avoid overwriting previous results.
n_iterations = 1000  # Number of iterations to run the AGOX loop.

##############################################################################
# Replica exchange settings:
##############################################################################

temperature_range = [0.02, 2.0]  # Temperature range for the walkers in eV.
sample_size = 10  # Number of walkers in the replica exchange simulation.
swap_interval = 10  # How often to attempt a swap between walkers.
rattle_amplitudes = np.linspace(0.1, 5, sample_size)  # Rattle amplitudes for the walkers.
dft_interval = 100  # Iterations between DFT evaluations.
n_dft = 5  # Number of structures to evaluate with DFT when selected.

##############################################################################
# Calculator
##############################################################################

calculator = SubprocessGPAW(
    mode={"name": "pw", "ecut": 500},
    xc="PBE",
    maxiter=200,
    kpts=(1, 1, 1),
    convergence={"energy": 0.0001, "density": 1.0e-4, "eigenstates": 1.0e-4, "bands": "occupied"},
    occupations={"name": "fermi-dirac", "width": 0.1},
    nbands="110%",
)

##############################################################################
# System & general settings:
##############################################################################

symbols = "Ag16S8"
cell_size = 20.0
confinement_size = 15.0
template = Atoms(cell=np.eye(3) * cell_size)
confinement_cell = np.eye(3) * confinement_size
confinement_corner = np.ones(3) * (cell_size - confinement_size) / 2
environment = Environment(
    template=template,
    symbols=symbols,
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
    box_constraint_pbc=[False, False, False],
)

constraints = environment.get_constraints()

# Database
db_path = "db{}.db".format(database_index)
database = Database(filename=db_path, order=6)

##############################################################################
# Machine learning surrogate model:
##############################################################################

# Prior - Pretrained CHGNet model.
prior = CalculatorModel(calculator=CHGNetCalculator(on_isolated_atoms="ignore"))

# Descriptor
symbols = environment.get_all_species()
descriptor = SOAP.from_species(symbols, r_cut=7.0)

# GPR Kernel
kernel = C(1) * RBF(40)
noise = 0.01

sparsifier = CUR(1000)

model = SparseGPR(
    database=database,
    kernel=kernel,
    descriptor=descriptor,
    prior=prior,
    n_optimize=0,
    sparsifier=sparsifier,
    noise=noise,
    centralize=True,
)

##############################################################################
# Search Settings:
##############################################################################

sampler = ReplicaExchangeSampler(
    model=model,
    t_min=temperature_range[0],
    t_max=temperature_range[1],
    swap_interval=swap_interval,
    sample_size=sample_size,
    order=3,
    verbosity=2,
)

collector = ReplicaExchangeCollector.from_sampler(
    sampler,
    environment,
    rattle_amplitudes,
)

# If any generators will have dynamic parameters i.e. rattle amplitude, define them here
for i in range(sample_size - 1):
    collector.add_generator_update(i, "rattle_amplitude", min_val=0.01, max_val=5)

# Define an acquisitor which manages what and when structures are passed to the evaluator
acquisitor = ReplicaExchangeAcquisitor.with_interval(dft_interval=dft_interval)

relaxer = ParallelRelaxPostprocess(
    model=model,
    constraints=constraints,
    optimizer_run_kwargs={"steps": 100, "fmax": 0.025},  # Choose this appropriately.
    start_relax=0,
    order=2,
)

evaluator = SinglePointEvaluator(calculator, number_to_evaluate=n_dft)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(collector, relaxer, acquisitor, evaluator, sampler, database, seed=seed)

agox.run(N_iterations=n_iterations)
