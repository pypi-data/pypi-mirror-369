
import numpy as np

from agox.models.descriptors.type_descriptor import TypeDescriptor
from agox.models.GPR import SparseGPR
from agox.models.GPR.kernels import DotProduct
from agox.models.GPR.priors import Repulsive
from agox.utils.sparsifiers.ABC_sparsifier import SparsifierBaseClass


class OnehotUniqueSparsifier(SparsifierBaseClass):
    name = "OnehotUnique"

    def __init__(self, n_species):
        self.m_points = n_species

    def sparsify(self, X: np.ndarray) -> np.ndarray:
        return np.eye(self.m_points), None


class LocalMean(SparseGPR):
    name = "LocalMeanModel"

    def __init__(self, species, database=None, prior=Repulsive(ratio=0.7), **kwargs):
        kernel = DotProduct(0)
        descriptor = TypeDescriptor.from_species(species)
        sparsifier = OnehotUniqueSparsifier(n_species=len(species))
        super().__init__(
            kernel=kernel,
            descriptor=descriptor,
            noise=0.001,
            use_ray=False,
            n_optimize=0,
            prior=prior,
            sparsifier=sparsifier,
            database=database,
        )

        self.dynamic_attributes = ["X", "Xm", "Kmm_inv", "alpha", "C_inv", "kernel", "mean_energy"]

    def predict_forces(self, atoms, **kwargs):
        F = np.zeros((len(atoms), 3))
        return self._postprocess_forces(atoms, F)

    def train(self, data):
        super().train(data)

        self.writer("Energies for each species:")
        for alpha, species in zip(self.alpha.flatten(), self.descriptor.unique_numbers):
            self.writer(f"    Atomic number {species}: {alpha:.3f}")
