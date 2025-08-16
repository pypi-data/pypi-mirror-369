import numpy as np
from ase import Atoms

from agox.environments import Environment
from agox.models.descriptors import SOAP, Fingerprint

# using AGOX environment
environment = Environment(Atoms(cell=np.eye(3) * 10), symbols="H6C6", print_report=False)
global_descriptor = Fingerprint(environment=environment, rc1=5.0)

# using ASE atoms object
atoms = Atoms("H6C6", cell=np.eye(3) * 10)
global_descriptor = Fingerprint.from_atoms(atoms, rc1=5.0)

# using AGOX environment
environment = Environment(Atoms(), symbols="HC", print_report=False)
local_descriptor = SOAP(environment=environment, r_cut=5.0)

# using species list
local_descriptor = SOAP.from_species(["H", "C"], r_cut=5.0)
