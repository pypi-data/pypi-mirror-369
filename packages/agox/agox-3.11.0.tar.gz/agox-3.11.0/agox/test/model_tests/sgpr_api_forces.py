from agox.models.datasets import datasets
from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.utils.sparsifiers import CUR

data = datasets["Ag5O3"]
transfer_data = data[:10]
training_data = data[10:80]
validation_data = data[80:90]
test_data = data[90:]

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
    noise_E=0.01,  # eV/atom
    noise_F=0.05,  # eV/Å/atom
    force_data_filter="all",
)

# one can also add transfer data e.g. from another system size to improve the model
model.add_transfer_data(transfer_data, noise=0.05)

# like for the GPR model, one can add validation data
model.add_validation_data(validation_data)

# train the model on the training data
model.train(training_data)

# save the model to a file
model.save("sgpr.h5")
