import numpy as np
from ase import Atoms

from agox import AGOX
from agox.acquisitors import ReplicaExchangeAcquisitor
from agox.collectors import ReplicaExchangeCollector
from agox.databases import Database
from agox.environments import Environment
from agox.evaluators import SinglePointEvaluator
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

seed = 41
database_index = 0
n_iterations = 10  # Number of iterations to run the AGOX loop.

##############################################################################
# Replica exchange settings:
##############################################################################

temperature_range = [0.02, 2.0] # Temperature range for the walkers in eV.
sample_size = 2                # Number of walkers in the replica exchange simulation.
swap_interval = 10              # How often to attempt a swap between walkers.
rattle_amplitudes = np.linspace(0.1, 5, sample_size) # Rattle amplitudes for the walkers.
dft_interval = 5                # Iterations between DFT evaluations.
n_dft = 2                       # Number of structures to evaluate with DFT when selected.

##############################################################################
# Calculator
##############################################################################

from ase.calculators.emt import EMT

calculator = EMT()

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

constraints = environment.get_constraints()

# Database
db_path = "db{}.db".format(database_index)  # From input argument!
database = Database(filename=db_path, order=6)

##############################################################################
# Machine learning surrogate model:
##############################################################################

# Prior - Pretrained CHGNet model.

# Uncomment the following lines to use a pretrained CHGNet model.
# from chgnet.model.dynamics import CHGNetCalculator
# prior = CalculatorModel(calculator=CHGNetCalculator(on_isolated_atoms="ignore"))

from ase.calculators.lj import LennardJones
prior = CalculatorModel(calculator=LennardJones(epsilon=1.0, sigma=1.0))

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
    centralize=True)
    
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
acquisitor = ReplicaExchangeAcquisitor.with_interval(
    dft_interval=dft_interval)

relaxer = ParallelRelaxPostprocess(
    model=model,
    constraints=constraints,
    optimizer_run_kwargs={"steps": 5, "fmax": 0.025},  # Choose this appropriately.
    start_relax=0,
    order=2,
)

evaluator = SinglePointEvaluator(calculator, number_to_evaluate=n_dft)

##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(collector, relaxer, acquisitor, evaluator, sampler, database, seed=seed)

agox.run(N_iterations=n_iterations)