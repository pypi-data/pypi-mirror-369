from typing import List

import numpy as np
from ase import Atoms

from agox.models.GPR.sGPR import SparseGPR
from agox.utils import candidate_list_comprehension


class SparseGPREnsemble(SparseGPR):
    """
    Sparse Gaussian Process Regression with ensemble of models.

    Parameters
    ----------
    N_ensemble : int
        Number of models in the ensemble.
    target_noise : float
        Noise added to the target values pr. atom
    prior_noise : float
        Noise added to the prior values pr. atom
    """

    name = "SparseGPREnsemble"

    def __init__(self, N_ensemble=5, target_noise=0.25, prior_noise=0, *args, **kwargs):
        self.priors_per_atom = None
        self.ensemble_alpha = None
        self.N_ensemble = N_ensemble
        self.target_noise = target_noise
        self.prior_noise = prior_noise

        super().__init__(*args, **kwargs)
        for attr in ["priors_per_atom", "ensemble_alpha"]:
            self.add_dynamic_attribute(attr)

    def _preprocess(self, data: List[Atoms]):
        X, y = super()._preprocess(data)

        all_data = self.get_all_data(data)

        # Repeat y in the ensemble dimension
        y = np.repeat(y, self.N_ensemble + 1, axis=1)

        # Add noise to y in the ensemble dimension:
        centers = np.array([self.descriptor.get_number_of_centers(atoms) for atoms in all_data]).reshape(-1, 1)
        target_noise = np.repeat(self.target_noise * centers, self.N_ensemble, axis=1)
        random_noise = np.random.normal(scale=target_noise, size=y[: self._N_energies, 1:].shape)
        y[: self._N_energies, 1:] += random_noise

        # Calculate prior for each model:
        self.priors_per_atom = np.random.normal(scale=self.prior_noise, size=(1, y.shape[1]))
        self.priors_per_atom[0, 0] = 0
        y -= centers * self.priors_per_atom
        return X, y

    def _train_model(self, data: List[Atoms], synchronize=True) -> None:
        super()._train_model(data, synchronize=True, train_projected_process=False)
        self.ensemble_alpha = self.alpha[:, 1:].copy()
        self.alpha = self.alpha[:, 0]

        if self.use_ray and synchronize:
            self.pool_synchronize(
                attributes=["X", "alpha", "ensemble_alpha", "kernel", "priors_per_atom", "mean_energy"],
                writer=self.writer,
            )

    @candidate_list_comprehension
    def predict_uncertainty(self, atoms: Atoms, k: np.ndarray = None, x: np.ndarray = None, **kwargs) -> float:
        if self.ensemble_alpha is not None:
            k = self._get_kernel_vector(k, x, atoms)
            centers = self.descriptor.get_number_of_centers(atoms)
            e_pred = np.sum(k.T @ self.ensemble_alpha, axis=0) + centers * self.priors_per_atom[0, 1:]
            return np.std(e_pred)
        else:
            return 0.0

    def predict_variances(self, atoms: Atoms, x: np.ndarray = None, k: np.ndarray = None, **kwargs) -> float:
        if self.ensemble_alpha is not None:
            k = self._get_kernel_vector(k, x, atoms)
            centers = self.descriptor.get_number_of_centers(atoms)
            e_pred = k.T @ self.ensemble_alpha + centers * self.priors_per_atom[0, 1:]
            return e_pred.var(axis=1)
        else:
            return 0.0

    @candidate_list_comprehension
    def predict_uncertainty_forces(self, atoms, x=None, k=None, dk_dr=None, **kwargs):
        if k is None:
            if x is None:
                x = self._get_features(atoms)
            k = self.kernel(self.Xm, x)

        if dk_dr is None:
            dk_dr = self._get_kernel_derivative(atoms, x=x)

        # Predict the forces:
        forces = (-dk_dr.sum(axis=0) @ self.ensemble_alpha).squeeze()

        centers = self.descriptor.get_number_of_centers(atoms)
        energies = np.sum(k.T @ self.ensemble_alpha, axis=0) + centers * self.priors_per_atom[0, 1:]
        std = np.std(energies)

        std_forces = (1 / (self.N_ensemble * std) * (energies - energies.mean()) * (forces - forces.mean())).sum(axis=2)

        return std_forces
