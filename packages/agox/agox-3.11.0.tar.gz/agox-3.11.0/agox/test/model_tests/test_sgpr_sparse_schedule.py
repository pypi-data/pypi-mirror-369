import numpy as np
import pytest
from ase import Atoms
from ase.calculators.lj import LennardJones

from agox.models.descriptors import SOAP
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import RBF
from agox.models.GPR.kernels import Constant as C
from agox.models.GPR.priors import Repulsive
from agox.utils.sparsifiers.CUR import CUR


def model_factory(sparsification_schedule=None):
    # Setup a model:
    descriptor = SOAP.from_species(["H"], periodic=False, r_cut=7)
    kernel = C(1, (1, 1)) * RBF(10, (20, 20))
    sparsifier = CUR(5)

    general_kwargs = dict(
        descriptor=descriptor,
        kernel=kernel,
        sparsifier=sparsifier,
        noise=1,
        prior=Repulsive(ratio=0.7),
        use_ray=False,
        n_optimize=0,
        sparsification_schedule=sparsification_schedule,
    )

    model = SparseGPR(**general_kwargs)
    return model


def pair_potential_data():
    d = np.linspace(0.88, 1.7, 20)
    data = []
    for d_ in d:
        atoms = Atoms("HH", positions=[[0, 0, 0], [0, 0, d_]])
        atoms.calc = LennardJones()
        atoms.get_potential_energy()
        data.append(atoms)

    return data


@pytest.mark.ray
def test_sparse_model_schedule_1():
    # Setup a model:
    model = model_factory()
    data = pair_potential_data()

    # Train the model and it selects sparse points:
    model.train(data)

    # Check that the model has selected the correct number of sparse points:
    assert len(model.Xm) == 5

    # Reset the model and check that it does sparsification:
    model.Xm = model.Xm[0:1, :]
    model.train(data)
    assert len(model.Xm) == 5


@pytest.mark.ray
def test_sparse_model_schedule_2():
    def sparsification_schedule(*args, **kwargs):
        return False

    # Setup a model:
    model = model_factory(sparsification_schedule=sparsification_schedule)

    data = pair_potential_data()

    # Train the model and it selects sparse points:
    model.train(data)

    # Check that the model has selected the correct number of sparse points:
    assert len(model.Xm) == 5

    # Reset the model and check that it doesn't do sparsification:
    model.iteration_counter = 1
    model.Xm = model.Xm[0:1, :]
    model.train(data)
    assert len(model.Xm) == 1
