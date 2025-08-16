import numpy as np
import pytest

from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.test.test_utils import get_test_data, get_test_environment, test_data_dicts


@pytest.mark.ray
@pytest.mark.parametrize("test_data_dict", test_data_dicts)
def test_ray_global_gpr(test_data_dict, ray_fix, cmd_options):
    # Tolerances:
    tolerance = cmd_options["tolerance"]

    path = test_data_dict["path"]
    remove = test_data_dict["remove"]

    environment = get_test_environment(path, remove)
    data = get_test_data(path, environment)

    train_data = data[0:25]
    test_data = data[25:35]

    # Make a global model:
    descriptor = SOAP(environment=environment)

    # If the kernel hyperparameters are allowed to take extreme values (large amplitude, small length scale),
    # it can ocassionally fail - even when the hyperparameters are properly transferred to the actors.
    # But I think that has to be a numerical issue?
    kernel = C(1, (1, 100)) * RBF(10, (10, 50))

    model = SparseGPR(
        descriptor=descriptor, kernel=kernel, n_optimize=2, use_ray=True, unc_jitter=1e-3, train_uncertainty=True
    )

    model.train(train_data)
    model.pool.synchronize_module(model)

    # Check properties on actors:
    result_dicts = model.pool.get_module_attributes(model, model.dynamic_attributes)

    for result_dict in result_dicts:
        for attribute_name in ["X", "Xm", "Kmm_inv", "alpha", "C_inv"]:
            np.testing.assert_allclose(result_dict[attribute_name], model.__getattribute__(attribute_name), **tolerance)

        # Kernel check seperately because it is annoying.
        np.testing.assert_allclose(result_dict["kernel"].theta, model.kernel.theta, **tolerance)

    # Predictions without Ray:
    energies = np.array(model.predict_energy(test_data))
    forces = np.array(model.predict_forces(test_data))
    uncertainties = np.array(model.predict_uncertainty(test_data))
    unceertainty_forces = np.array(model.predict_uncertainty_forces(test_data))

    # Predictions with Ray:
    def predict(model, atoms):
        E = np.array(model.predict_energy(atoms))
        F = np.array(model.predict_forces(atoms))
        sigma = np.array(model.predict_uncertainty(atoms))
        sigma_F = np.array(model.predict_uncertainty_forces(atoms))

        results = {"E": E, "F": F, "sigma": sigma, "sigma_F": sigma_F}
        return results

    pool = model.pool
    # Make predictions on all actors:
    key = pool.get_key(model)
    results = pool.execute_on_actors(predict, [key], [test_data], {})

    # Check that all predictions on every actor are the same:
    results_actor_0 = results[0]
    for key in results[0].keys():
        for results_actor in results[1:]:
            np.testing.assert_allclose(results_actor_0[key], results_actor[key])

    # # Check that predictions are the same as without Ray:
    np.testing.assert_allclose(energies, results_actor_0["E"], **tolerance)
    np.testing.assert_allclose(forces, results_actor_0["F"], **tolerance)
    np.testing.assert_allclose(uncertainties, results_actor_0["sigma"], **tolerance)
    np.testing.assert_allclose(unceertainty_forces, results_actor_0["sigma_F"], **tolerance)
