import numpy as np
from ase import Atoms
from ase.build import bulk
from ase.calculators.emt import EMT
from ase.optimize import FIRE

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
from agox.postprocessors.minimum_dist import MinimumDistPostProcess
from agox.samplers import GFEKMeansSampler
from agox.utils.sparsifiers import CUR
from agox.utils.thermodynamics import ThermodynamicsData

##############################################################################
# General settings:
##############################################################################

# Manually set seed and database-index - for production searches with repeated independent runs the seed should be be set to different values.
seed = 41
database_index = 0

# Candidate gnerator settings:
# Number of candidates to generate for each iteration with each generator: random, rattle, add/remove.
# For efficiency the total number should be an integer multiple of the number of the number of CPUs used.
generator_dictionary = {0: [32, 0, 0], 5: [6, 26, 0], 10: [4, 20, 8]}
C_dict = {"c1": 0.85, "c2": 1.5}  # Constants for the generators, used in rattle and add/remove generators.

# Model relaxations settings:
model_relax_steps = 10  # Number of steps to relax the surrogate model.
model_fmax = 0.05  # Force convergence criterion for the model relaxations in eV/Angstrom.

N_iterations = 10  # Number of iterations to run the AGOX loop.

##############################################################################
# Grand Canonical Global Optimization settings:
##############################################################################

mu_Ni = -0.1  # Chemical potential for nickel in eV.
mu_Cu = -0.1  # Chemical potential for copper in eV.
symbols_range = {"Ni": [4, 5], "Cu": [0, 1, 2]}  # Range of stoichiometries for the elements in the system.

# The reference energies for the elements are calculated using the EMT calculator.
# How to best calculate these reference energies depends on the system.
# Here the reference is set to the potential energy of a bulk crystal of the element.
calculator = EMT()
nickel_reference = bulk("Ni", cubic=True)
copper_reference = bulk("Cu", cubic=True)
ref_Ni = calculator.get_potential_energy(nickel_reference) / len(
    nickel_reference
)  # Reference energy for nickel in eV/atom.
ref_Cu = calculator.get_potential_energy(copper_reference) / len(
    copper_reference
)  # Reference energy for copper in eV/atom.

template_energy = (
    0  # eV - If using a slab the Gibbs energy calculation needs to be adjusted to account for the slab energy.
)


##############################################################################
# System & general settings:
##############################################################################

template = Atoms("", cell=np.eye(3) * 12)
confinement_cell = np.eye(3) * 6
confinement_corner = np.array([3, 3, 3])
environment = Environment(
    template=template,
    symbols_range=symbols_range,
    confinement_cell=confinement_cell,
    confinement_corner=confinement_corner,
)

# Database
db_path = "db{}.db".format(database_index)
database = Database(filename=db_path, order=7)

##############################################################################
# Calculator
##############################################################################

calculator = EMT()

################################################################################
# Reference energies.
################################################################################

# Loading thermodynamics data from a file and adjusting the chemical potentials.
# path = data_directory / "thermo_data_dft_pw400_2x2.json"
# thermo_data = ThermodynamicsData.from_file(path) 
# thermo_data.set_chemical_potential("Cu", mu_Cu)
# thermo_data.set_chemical_potential("Ni", mu_Ni)
# thermo_data.save("gfe.json")

# Creating a ThermodynamicsData object directly

thermo_data = ThermodynamicsData(
    references={
        "Ni": ref_Ni,  # eV/atom
        "Cu": ref_Cu,  # eV/atom
    },
    chemical_potentials={
        "Cu": mu_Ni,  # eV/atom
        "Ni": mu_Ni,  # eV/atom
    },
    template_energy=template_energy,  # eV
)

# Can store the ThermodynamicsData object to a file for later use:
thermo_data.save("thermo_data.json")

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
kernel = C(5, (1, 100)) * RBF(20, (10, 30))

single_atom_energies = np.zeros(100)
for symbol in thermo_data.references.keys():
    number = Atoms(symbol).numbers[0]
    single_atom_energies[number] = thermo_data.references[symbol]

model = SparseGPR(
    descriptor=descriptor,
    kernel=kernel,
    database=database,
    sparsifier=CUR(1000),  # sparsification using CUR algorithm with 1000 sparse points
    sigma=0.01,  # eV/atom
    prior=Repulsive(ratio=0.8),
    use_ray=False,
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
rattle_generator = RattleGenerator(**C_dict, **environment.get_confinement())
random_generator = RandomGenerator(**C_dict, **environment.get_confinement(), contiguous=False)
addrm_generator = AddRemoveGenerator(**C_dict, **environment.get_confinement())

# Dict specificies how many candidates are created with and the dict-keys are iterations.
generators = [random_generator, rattle_generator, addrm_generator]
num_candidates = generator_dictionary

acquisitor = GibbsFreeEnergyAquisitor(
    thermo_data=thermo_data,
    model=model,
    kappa=2,
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
    optimizer=FIRE,
    optimizer_run_kwargs={"steps": model_relax_steps, "fmax": model_fmax},
    start_relax=5,
    order=2,
)

min_dist = MinimumDistPostProcess(order=2.5, **C_dict)

evaluator = LocalOptimizationEvaluator(
    calculator,
    gets={"get_key": "prioritized_candidates"},
    optimizer_kwargs={"logfile": None},
    store_trajectory=True,
    optimizer_run_kwargs={"fmax": 0.05, "steps": 0},
    order=6,
)
##############################################################################
# Let get the show running!
##############################################################################

agox = AGOX(collector, acquisitor, relaxer, database, evaluator, min_dist, seed=seed)

agox.run(N_iterations=N_iterations)
