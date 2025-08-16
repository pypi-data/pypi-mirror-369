import os

import numpy as np
import pytest

from agox.models.datasets import datasets


def make_local_gpr():
    from agox.models.descriptors import SOAP
    from agox.models.GPR import SparseGPR
    from agox.models.GPR.kernels import RBF
    from agox.models.GPR.kernels import Constant as C

    kernel = C(1, (1, 100)) * RBF(10, (10, 30))
    descriptor = SOAP.from_species(species=["Ag", "O"])
    model = SparseGPR(
        kernel=kernel,
        descriptor=descriptor,
        unc_jitter=1e-3,
        train_uncertainty=True,
    )
    return model


def make_global_gpr():
    from agox.models.descriptors import Fingerprint
    from agox.models.GPR import GPR
    from agox.models.GPR.kernels import RBF, Noise
    from agox.models.GPR.kernels import Constant as C
    from agox.models.GPR.priors import Repulsive

    descriptor = Fingerprint.from_atoms(datasets["Ag5O3"][0])
    kernel = C() * RBF() + Noise(0.01)
    model = GPR(descriptor, kernel, prior=Repulsive(), n_optimize=0)
    return model


@pytest.mark.ray
@pytest.mark.parametrize("model_maker", [make_global_gpr, make_local_gpr])
def test_model(model_maker, cmd_options, tmpdir):
    tolerances = cmd_options["tolerance"]

    data = datasets["Ag5O3"]
    training_data = data[:-1]
    test_data = data[-1]

    model = model_maker()
    model.train(training_data)

    E = model.predict_energy(test_data)
    F = model.predict_forces(test_data)
    S = model.predict_uncertainty(test_data)

    tmpfile = str(tmpdir.join("test_model.h5"))
    model.save(tmpfile)

    new_model = model_maker()
    new_model.load(tmpfile)
    os.remove(tmpfile)

    E_new = new_model.predict_energy(test_data)
    F_new = new_model.predict_forces(test_data)
    S_new = new_model.predict_uncertainty(test_data)

    np.testing.assert_allclose(E, E_new, **tolerances)
    np.testing.assert_allclose(F, F_new, **tolerances)
    np.testing.assert_allclose(S, S_new, **tolerances)
