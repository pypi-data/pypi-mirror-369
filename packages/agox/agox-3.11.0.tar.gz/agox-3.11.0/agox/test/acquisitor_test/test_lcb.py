import numpy as np
import pytest

from agox.acquisitors import LowerConfidenceBoundAcquisitor
from agox.models.descriptors import Fingerprint
from agox.models.GPR import GPR
from agox.models.GPR.kernels import RBF, Noise
from agox.models.GPR.kernels import Constant as C
from agox.test.test_utils import get_test_data, get_test_environment, test_data_dicts
from agox.utils.numerical_derivative import atomic_numerical_derivative


@pytest.mark.ray
@pytest.mark.parametrize("test_data_dict", test_data_dicts[0:1])
def test_ray_global_gpr(test_data_dict, ray_fix, cmd_options):
    # Tolerances:
    tolerance = cmd_options["tolerance"]

    # Dataset:
    path = test_data_dict["path"]
    remove = test_data_dict["remove"]
    environment = get_test_environment(path, remove)
    data = get_test_data(path, environment)

    train_data = data[0:25]
    test_data = data[25:35]

    descriptor = Fingerprint(environment=environment)

    kernel = C(1) * RBF(1000000) + Noise(0.01)

    model = GPR(descriptor=descriptor, kernel=kernel, n_optimize=0, use_ray=False)

    model.train(train_data)

    kappa = 0
    acquisitor = LowerConfidenceBoundAcquisitor(model=model, kappa=kappa)
    calc = acquisitor.get_acquisition_calculator()

    def calc_lcb(atoms):
        lcb = model.predict_energy(atoms) - kappa * model.predict_uncertainty(atoms)
        return lcb

    # Numerical derivative:
    atoms = test_data[0].copy()
    F = atomic_numerical_derivative(calc_lcb, atoms)

    # Analytical derivative:
    atoms = test_data[0].copy()
    atoms.set_calculator(calc)
    F_analytical = atoms.get_forces()

    print(F.shape, F_analytical.shape)

    np.testing.assert_allclose(F, F_analytical, rtol=1e2, atol=1e-10)

    # np.testing.assert_allclose(np.linalg.norm(F), np.linalg.norm(F_analytical))
