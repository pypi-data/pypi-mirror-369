from agox.models.datasets import datasets
from agox.models.descriptors import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.models.GPR.priors import Repulsive
from agox.utils.filters import EnergyFilter, SparsifierFilter
from agox.utils.sparsifiers import CUR

data = datasets["Ag5O3"]
training_data = data[:80]
validation_data = data[80:90]
test_data = data[90:]

# Initialize global descriptor using the ASE atoms interface
descriptor = Fingerprint.from_atoms(training_data[0])

# Define a filter that remove high energy structures and
# if more than 50 structure are left, pick 50 among them with CUR.
data_filter = EnergyFilter() + SparsifierFilter(descriptor=descriptor, sparsifier=CUR(m_points=50))
# Initialize the kernel
kernel = C() * RBF() + Noise(0.01)

# Initialize the model
model = GPR(
    descriptor,
    kernel,
    filter=data_filter,
    prior=Repulsive(),
    use_ray=False,
)
# One can add validation data to the model
model.add_validation_data(validation_data)

model.train(training_data)

# predict energy, uncertainty and force of test data
E_pred = model.predict_energy(test_data)
F_pred = model.predict_forces(test_data)
S_pred = model.predict_uncertainty(test_data)

# save the model to a file
model.save("gpr.h5")
