from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.utils.sparsifiers import CUR

kernel = C(1, (1, 100)) * RBF(20, (10, 30))
descriptor = SOAP.from_species(
    species=["Ag", "O"],
    r_cut=5,
    nmax=3,
    lmax=2,
    sigma=1,
    weight=True,
    periodic=False,
)
model = SparseGPR(
    kernel=kernel,
    descriptor=descriptor,
    sparsifier=CUR(1000),  # sparsification using CUR algorithm with 1000 sparse points
    noise=0.01,  # eV/atom
)

# load the model from a file
model.load("sgpr.h5")
