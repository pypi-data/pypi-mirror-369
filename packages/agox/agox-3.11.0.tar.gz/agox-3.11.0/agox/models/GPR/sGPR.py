import warnings
from timeit import default_timer as dt
from typing import List, Optional, Tuple

import numpy as np
from ase import Atoms
from scipy.linalg import lstsq, qr
from scipy.sparse import dia_matrix

from agox.models.GPR.GPR import GPR
from agox.utils import candidate_list_comprehension
from agox.utils.filters import AllFilter, NoneFilter
from agox.utils.sparsifiers import CUR, SparsifierBaseClass


class SparseGPR(GPR):
    """
    Sparse Gaussian Process Regression with inducing points.

    Parameters:
    -----------
    sigma : float
        Noise level for both energy and forces data, by default 0.01
    sigma_E : float
        Noise level for energy data is per descriptor center ie. per atom for local
        descriptors and per configuration for global descriptors.
    sigma_F : float
        Noise level for force data.
    sparsifier : SparsifierBaseClass
        Sparsifier object
    force_data_filter : FilterBaseClass
        Filter object for force data. Selection of atoms from which the forces are
        used for training.
    jitter : float
        Jitter level
    train_uncertainty : bool
        If True the matrices needed to predict uncertainty are trained, by default False

    noise : float
        Deprecated. Use sigma instead
    noise_E : float
        Deprecated. Use sigma_E instead
    noise_F : float
        Deprecated. Use sigma_F instead

    """

    name = "SparseGPR"

    supported_descriptor_types = ["global", "local"]

    implemented_properties = ["energy", "forces", "local_energy", "uncertainty"]

    def __init__(
        self,
        sigma: float = 0.01,
        centralize: bool = False,
        jitter: float = 1e-8,
        unc_jitter: float = 1e-5,
        filter=None,
        sparsifier: SparsifierBaseClass = CUR(),
        n_optimize=0,
        force_data_filter=NoneFilter(),
        noise: Optional[float] = None,
        sigma_E: Optional[float] = None,
        sigma_F: Optional[float] = None,
        noise_E: Optional[float] = None,
        noise_F: Optional[float] = None,
        sparsification_schedule=None,
        train_uncertainty: bool = False,
        **kwargs,
    ) -> None:
        """

        Parameters
        ----------
        """
        super().__init__(centralize=centralize, filter=filter, n_optimize=n_optimize, **kwargs)

        for attr in ["X", "Xm", "alpha", "kernel", "mean_energy", "_ready_state"]:
            self.add_dynamic_attribute(attr)

        self.jitter = jitter
        self.unc_jitter = unc_jitter

        # Deprecation warnings:
        if noise is not None:
            warnings.warn(
                "noise is deprecated and will be removed in version 4.0.0. Use sigma instead", DeprecationWarning
            )
            sigma = noise
        if noise_E is not None:
            warnings.warn(
                "noise_E is deprecated and will be removed in version 4.0.0. Use sigma_E instead", DeprecationWarning
            )
            sigma_E = noise_E
        if noise_F is not None:
            warnings.warn(
                "noise_F is deprecated and will be removed in version 4.0.0. Use sigma_F instead", DeprecationWarning
            )
            sigma_F = noise_F

        if sigma_E is None:
            self.sigma_E = sigma
        else:
            self.sigma_E = sigma_E

        if noise_F is None:
            self.sigma_F = sigma
        else:
            self.sigma_F = sigma_F

        self.sparsifier = sparsifier

        self._transfer_data = []
        self._transfer_noise = np.array([])

        if force_data_filter == "all":
            self.force_data_filter = AllFilter()
        elif force_data_filter == "none":
            self.force_data_filter = NoneFilter()
        else:
            self.force_data_filter = force_data_filter

        self.train_uncertainty = train_uncertainty

        if self.train_uncertainty:
            self.add_dynamic_attribute("C_inv")
            self.add_dynamic_attribute("Kmm_inv")

        if self.use_ray:
            self.actor_model_key = self.pool_add_module(self)
            self.self_synchronizing = True  # Defaults to False, inherited from Module.

        if sparsification_schedule is not None:
            self.sparsification_schedule = sparsification_schedule

        self._set_saved_attributes()

    def _set_saved_attributes(self):
        self.reset_save_attributes()
        self.add_save_attributes(
            ["Xm", "X", "alpha", "single_atom_energies", "_ready_state", "kernel.theta", "mean_energy"]
        )
        if self.train_uncertainty:
            self.add_save_attributes(["C_inv", "Kmm_inv"])

    @candidate_list_comprehension
    def predict_local_energy(self, atoms: Atoms, **kwargs) -> np.ndarray:
        """
        Calculate the local energies in the model.

        Parameters
        ----------
        atoms : ase.Atoms
            ase.Atoms object
        X : np.ndarray
            Features for the ase.Atoms object

        Returns
        -------
        np.ndarray
            Local energies

        """
        X = self._get_features(atoms)
        k = self.kernel(self.Xm, X)
        return (k.T @ self.alpha).reshape(
            -1,
        ) + self.single_atom_energies[atoms.get_atomic_numbers()]

    @candidate_list_comprehension
    def predict_uncertainty(self, atoms: Atoms, k: np.ndarray = None, k0: np.ndarray = None, **kwargs) -> float:
        """
        Predict uncertainty for a given atoms object

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object

        Returns
        -------
        float
            Uncertainty

        """
        if "uncertainty" not in self.implemented_properties or not self.ready_state:
            unc = 0
        else:
            cov = self.predict_covariance(atoms, k=k, k0=k0)
            unc = np.sqrt(cov.sum())
        return unc

    def predict_variances(self, atoms: Atoms, k: np.ndarray = None, k0: np.ndarray = None, **kwargs):
        cov = self.predict_covariance(atoms, k=k, k0=k0)
        local_variances = np.diag(cov)
        return local_variances

    @candidate_list_comprehension
    def predict_covariance(self, atoms: Atoms, k: np.ndarray = None, k0: np.ndarray = None, **kwargs):
        """
        Calculate the covariance matrix of local energies for a given atoms object.
        """
        X = self._get_features(atoms)

        if k is None:
            k = self.kernel(self.Xm, X)

        if k0 is None:
            k0 = self.kernel(X, X)

        cov = k0 - k.T @ self.Kmm_inv @ k + k.T @ self.C_inv @ k

        return cov

    @candidate_list_comprehension
    def predict_uncertainty_forces(self, atoms, x=None, k=None, dk_dr=None, dx_dr=None, **kwargs):
        if "uncertainty" not in self.implemented_properties or not self.ready_state:
            return np.zeros((len(atoms), 3))

        # Compute the required things if they are not supplied:
        if k is None:
            if x is None:
                x = self._get_features(atoms)
            k = self.kernel(self.Xm, x)

        if dx_dr is None:
            dx_dr = self.descriptor.get_feature_gradient(atoms)

        if dk_dr is None:
            dk_dr = self._get_kernel_derivative(atoms, x=x, dX_dr=dx_dr)

        dk0_dx = np.array([self.kernel.get_feature_gradient(x, x[i : i + 1]) for i in range(len(x))])

        # Kmm_inv % C_inv part.
        # This is likely the optimal for all realistic cases (unless number of atoms and number of m-points is close)
        # Small optimization my moving subtraction of the to m x m matrices to the
        # training function, but ehh.
        opt_ein_sum_path = ["einsum_path", (1, 2), (0, 1)]
        forces = 2 * np.einsum("ijdm, mn, no -> jd", dk_dr, (self.C_inv - self.Kmm_inv), k, optimize=opt_ein_sum_path)

        # k0-part:
        forces += np.einsum("indf,ijf->nd", dx_dr, dk0_dx) - np.einsum("jndf,ijf->nd", dx_dr, dk0_dx)

        # Total std is required too:
        std = self.predict_uncertainty(atoms, x=x, k=k)

        return -forces / (2 * std)

    @property
    def noise_E(self) -> float:
        """
        Noise level

        Returns
        -------
        float
            Noise level

        """
        return self._noise

    @noise_E.setter
    def noise_E(self, s: float) -> None:
        """
        Noise level

        Parameters
        ----------
        s : float
            Noise level

        """
        self._noise = s

    @property
    def transfer_data(self) -> List[Atoms]:
        """
        List of ase.Atoms objects to transfer to the model

        Returns
        -------
        list of ase.Atoms
            List of ase.Atoms objects to transfer to the model

        """
        return self._transfer_data

    @transfer_data.setter
    def transfer_data(self, l: List[Atoms]) -> None:
        """
        List of ase.Atoms objects to transfer to the model

        Parameters
        ----------
        l : list of ase.Atoms
            ase.Atoms objects to transfer to the model

        """
        warnings.warn("transfer_data should not be used. Use add_transfer_data instead.")
        self.add_transfer_data(l)

    @property
    def transfer_noise(self) -> np.ndarray:
        """
        Noise level for transfer data

        Returns
        -------
        np.ndarray
            Noise level for transfer data

        """
        return self._transfer_noise

    @transfer_noise.setter
    def transfer_noise(self, s: np.ndarray) -> None:
        """
        Noise level for transfer data

        Parameters
        ----------
        s : np.ndarray
            Noise level for transfer data

        """
        warnings.warn("transfer_noise should not be used. Use add_transfer_data instead.")
        self._transfer_noise = s

    def add_transfer_data(self, data: List[Atoms], noise: float = None) -> None:
        """
        Add ase.Atoms objects to the transfer data

        Parameters
        ----------
        data : list of ase.Atoms
            List of ase.Atoms objects to add to the transfer data
        noise : float
            Noise level for the transfer data

        """
        if isinstance(data, list):
            self._transfer_data += data
            if noise is None:
                noise = self.sigma_E

            self._transfer_noise = np.append(self._transfer_noise, np.ones(len(data)) * noise)

        else:
            self.add_transfer_data.append([data])

    def get_all_data(self, data: List[Atoms]) -> List[Atoms]:
        """
        Prepend transfer data to the data for use when training.
        """
        return self.transfer_data + data

    def model_info(self, **kwargs) -> List[str]:
        """
        List of strings with model information
        """
        x = "    "

        filter_name = self.filter.name if self.filter is not None else "None"
        try:
            data_before_filter = self._data_before_filter
            data_after_filter = self._data_after_filter
            filter_removed_data = self._data_before_filter - self._data_after_filter
        except AttributeError:
            filter_removed_data = 0

        sparsifier_name = self.sparsifier.name if self.sparsifier is not None else "None"
        sparsifier_mpoints = self.sparsifier.m_points if self.sparsifier is not None else "None"
        force_data_filter = self.force_data_filter.name if self.force_data_filter else "None"

        out = [
            "------ Model Info ------",
            "Descriptor:",
            x + "{}".format(self.descriptor.name),
            "Kernel:",
            x + "{}".format(self.kernel),
            "Filter:",
            x + "{} removed {} structures".format(filter_name, filter_removed_data),
            x + "- Data before filter: {}".format(data_before_filter),
            x + "- Data after filter: {}".format(data_after_filter),
            "Sparsifier:",
            x + "{} selecting {} inducing points".format(sparsifier_name, sparsifier_mpoints),
            "Force-data filter:",
            x + "{}".format(force_data_filter),
            "Noise:",
            x + "Energy noise: {}".format(self.sigma_E),
            x + "Forces noise: {}".format(self.sigma_F),
            "------ Training Info ------",
            "Total training data: {} energies and {} forces".format(self._N_energies, self._N_forces),
            "Transfer data size: {}".format(len(self.transfer_data)),
            "Number of local environments: {}".format(self.Xn.shape[0]),
            "Number of inducing points: {}".format(self.Xm.shape[0]),
            "Neg. log marginal likelihood.: {:.2f}".format(self._nlml),
        ]

        return out

    def _train_model(self, data: List[Atoms], synchronize=True, train_projected_process=True) -> None:
        """
        Train the model

        """
        assert self.Xn is not None, "self.Xn must be set prior to call"
        assert self.L is not None, "self.L must be set prior to call"
        assert self.Y is not None, "self.Y must be set prior to call"

        t_hyper = dt()
        if self.use_ray:
            self.pool_synchronize(
                attributes=["Xn", "Xm", "Y", "L", "sigma_inv", "Xf", "dXf_dr"],
                writer=self.writer,
            )
            self.hyperparameter_search_parallel(relax=False)
        else:
            self.monte_carlo_hyperparameter_search()
        self.training_timings["hyperparameter_search"] = dt() - t_hyper

        t_train = dt()
        self.K_mm = self.kernel(self.Xm)
        self.K_nm = self.kernel(self.Xn, self.Xm)

        all_data = self.get_all_data(data)

        if len(self.training_force_data_indices) > 0:
            training_force_data = [all_data[i] for i in self.training_force_data_indices]
            K_nm_jac = np.concatenate(
                [self._get_sparse_kernel_derivative(x=x, dX_dr=dX_dr) for x, dX_dr in zip(self.Xf, self.dXf_dr)]
            )
            self.K_nm = np.concatenate([self.K_nm, K_nm_jac], axis=0)
        else:
            training_force_data = []

        LK_nm = self.L @ self.K_nm
        K = self.K_mm + LK_nm.T @ self.sigma_inv @ LK_nm + self.jitter * np.eye(self.K_mm.shape[0])
        K = self._symmetrize(K)

        self.alpha = self._solve(K, LK_nm.T @ self.sigma_inv @ self.Y)

        self.training_timings["training"] = dt() - t_train

        train_uncertainty = self.train_uncertainty and train_projected_process
        if train_uncertainty:
            t_uncertainty = dt()
            self.Kmm_inv = self._solve(self.K_mm + self.unc_jitter * np.eye(self.K_mm.shape[0]))

            local_sigma_inv = self._make_local_sigma(all_data, training_force_data)

            C = self.K_mm + self.K_nm.T @ local_sigma_inv @ self.K_nm + self.unc_jitter * np.eye(self.K_mm.shape[0])
            C = self._symmetrize(C)
            self.C_inv = self._solve(C)

            self.training_timings["uncertainty"] = dt() - t_uncertainty

        self.ready_state = True
        if self.use_ray and synchronize:
            t_sync = dt()
            attributes_to_sync = ["X", "alpha", "kernel", "mean_energy", "_ready_state"]

            if train_uncertainty:
                attributes_to_sync += ["Kmm_inv", "C_inv"]

            self.pool_synchronize(
                attributes=attributes_to_sync,
                writer=self.writer,
            )

            self.training_timings["synchronize"] = dt() - t_sync

    def _get_sparse_kernel_derivative(self, x: np.ndarray, dX_dr: np.ndarray) -> np.ndarray:
        """
        Get the kernel derivative wrt. the Carteisian coordinates r.

        Parameters
        ----------
        x : np.ndarray, optional
            Features, by default None
        dX_dr : np.ndarray, optional
            Derivatives of the features wrt. the Carteisian coordinates r, by default None

        Returns
        -------
        np.ndarray
            Derivatives of the kernel wrt. the Carteisian coordinates r.
        """
        # Get kernel derivatives:
        dk_dX = np.array([self.kernel.get_feature_gradient(self.Xm, x[i : i + 1]) for i in range(len(x))])

        # Convert to derivatives wrt. Carteisian coordinates r.
        dk_dr = np.einsum("nadf,nmf->nadm", dX_dr, dk_dX)  # [centers, atoms, 3, features]

        c, a, t, M = dk_dr.shape
        return dk_dr.sum(axis=0).reshape(a * t, M)

    def _get_forces_features(self, atoms: List[Atoms]) -> Tuple[List[np.ndarray], List[np.ndarray]]:
        """
        Get the features and derivatives of the features for the force data.

        Parameters
        ----------
        atoms : List[ase.Atoms]
            List of Atoms objects.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Features and derivatives of the features.
        """
        x = [self._get_features(a) for a in atoms]
        dX_dr = [self.descriptor.get_feature_gradient(a) for a in atoms]
        return x, dX_dr

    def _log_marginal_likelihood(self, theta: Optional[np.ndarray] = None) -> float:
        """
        Marginal log likelihood

        Parameters
        ----------
        theta : np.ndarray
            Kernel parameters

        Returns
        -------
        float
            log Marginal likelihood

        """
        if theta is not None:
            t = self.kernel.theta.copy()
            self.kernel.theta = theta
            K_nm = self.kernel(self.Xn, self.Xm)

            if len(self.Xf) > 0:
                K_nm_jac = np.concatenate(
                    [self._get_sparse_kernel_derivative(x=x, dX_dr=dX_dr) for x, dX_dr in zip(self.Xf, self.dXf_dr)]
                )
                K_nm = np.concatenate([K_nm, K_nm_jac], axis=0)

            Kmm_inv = self._solve(self.kernel(self.Xm) + self.unc_jitter * np.eye(self.Xm.shape[0]))
            self.kernel.theta = t
        else:
            K_nm = self.K_nm
            Kmm_inv = self.Kmm_inv

        LK_nm = self.L @ K_nm
        Ktilde = LK_nm @ Kmm_inv @ LK_nm.T + np.diag(1 / np.diagonal(self.sigma_inv))

        sign, logdet = np.linalg.slogdet(Ktilde)
        if sign <= 0:
            return np.inf

        lml = -0.5 * logdet
        a = self._solve(Ktilde, self.Y[:, 0])
        lml -= 0.5 * self.Y[:, 0].T @ a
        lml -= 0.5 * self.Y.shape[0] * np.log(2 * np.pi)

        return float(lml)

    def _preprocess(self, data: List[Atoms]) -> None:
        """
        Preprocess the training data for the model

        Parameters
        ----------
        data : list of ase.Atoms
            List of ase.Atoms objects

        Returns
        -------
        np.ndarray
            Features for the ase.Atoms objects
        np.ndarray
            Energies for the ase.Atoms objects

        """
        all_data = self.get_all_data(data)
        X, Y = super()._preprocess(all_data)
        self.Xn = X

        training_force_data, self.training_force_data_indices = self.force_data_filter(all_data)
        self.Xf, self.dXf_dr = self._get_forces_features(training_force_data)

        if len(training_force_data) > 0:
            F = np.concatenate([atoms.get_forces().reshape(-1) for atoms in training_force_data]).reshape(-1, 1)
            self._N_forces = F.shape[0]

            if self.prior is not None:
                F -= np.concatenate(
                    [self.prior.predict_forces(atoms).reshape(-1) for atoms in training_force_data]
                ).reshape(-1, 1)

            Y = np.concatenate([Y, F])
        else:
            self._N_forces = 0

        self.L = self._make_L(all_data, training_force_data, X.shape)
        self.sigma_inv = self._make_sigma(all_data, training_force_data)

        t_sparsify = dt()
        if self.sparsifier is not None:
            if hasattr(self, "num_enviornments_when_sparsified"):
                new_environments = self.Xn.shape[0] - self.num_enviornments_when_sparsified

            if not hasattr(self, "Xm"):
                # First time training we have to do sparsification.
                self.Xm, _ = self.sparsifier(self.Xn)
                self.num_enviornments_when_sparsified = len(self.Xn)
            elif self.get_iteration_counter() is None:
                # If the iteration counter is None, we have to do sparsification,
                # as it is not part of an AGOX run.
                self.Xm, _ = self.sparsifier(self.Xn)
                self.num_enviornments_when_sparsified = len(self.Xn)

            elif self.sparsification_schedule(
                total_environments=self.Xn.shape[0],
                sparse_environments=self.sparsifier.m_points,
                iteration=self.get_iteration_counter(),
                new_environments=new_environments,
            ):
                self.Xm, _ = self.sparsifier(self.Xn)
                self.num_enviornments_when_sparsified = len(self.Xn)
        else:
            self.Xm = self.Xn

        self.training_timings["sparsification"] = dt() - t_sparsify

        return self.Xm, Y

    def _make_L(
        self,
        atoms_list: List[Atoms],
        training_force_data: List[Atoms],
        shape_X: Tuple[int, int],
    ) -> np.ndarray:
        """
        Make the L matrix

        Parameters
        ----------
        atoms_list : list of ase.Atoms
            List of ase.Atoms objects

        Returns
        -------
        np.ndarray
            L matrix

        """
        lengths = [self.descriptor.get_number_of_centers(atoms) for atoms in atoms_list]
        r = len(lengths)
        c = np.sum(lengths)

        col = 0
        L = np.zeros((r, c))
        for i, atoms in enumerate(atoms_list):
            L[i, col : col + self.descriptor.get_number_of_centers(atoms)] = 1.0
            col += self.descriptor.get_number_of_centers(atoms)

        if len(training_force_data) > 0:
            cf = np.sum([len(atoms) for atoms in training_force_data])

            E_pad = np.zeros((r, 3 * cf))
            F_pad = np.zeros((3 * cf, c))
            L_F = np.zeros((3 * cf, 3 * cf))
            col = 0
            for i, atoms in enumerate(training_force_data):
                L_F[col : col + 3 * len(atoms), col : col + 3 * len(atoms)] = np.ones(3 * len(atoms))
                col += 3 * len(atoms)

            L_F[np.diag_indices_from(L_F)] = 0.0
            L = np.block([[L, E_pad], [F_pad, L_F]])

        return L

    def _make_sigma(self, atoms_list: List[Atoms], training_force_data: List[Atoms]) -> np.ndarray:
        """
        Make the sigma matrix

        Parameters
        ----------
        atoms_list : list of ase.Atoms
            List of ase.Atoms objects

        Returns
        -------
        np.ndarray
            Sigma matrix

        """
        sigmas = np.array([self.sigma_E**2 * self.descriptor.get_number_of_centers(atoms) for atoms in atoms_list])
        sigmas[: len(self.transfer_data)] = self.transfer_noise**2 * np.array(
            [self.descriptor.get_number_of_centers(atoms) for atoms in self.transfer_data]
        )
        if len(training_force_data) > 0:
            sigmas_F = self.sigma_F**2 * np.ones((3 * np.sum([len(atoms) for atoms in training_force_data]),))
            sigmas = np.concatenate([sigmas, sigmas_F])

        sigma_inv = np.diag(1 / sigmas)

        return sigma_inv

    def _make_local_sigma(self, atoms_list: List[Atoms], training_force_data: List[Atoms]) -> np.ndarray:
        """
        Make the local sigma matrix. This is the inverse of the local noise
        variance.

        Parameters
        ----------
        atoms_list : list of ase.Atoms

        Returns
        -------
        np.ndarray
            Local sigma matrix
        """
        local_sigmas = self.sigma_E**2 * np.ones(self.K_nm.shape[0])
        if len(self.transfer_data) > 0:
            idx = np.sum([len(atoms) for atoms in self.transfer_data])
            n_repeats = [self.descriptor.get_number_of_centers(atoms) for atoms in self.transfer_data]
            local_sigmas[:idx] = np.repeat(np.array(self.transfer_noise) ** 2, n_repeats)

        if len(training_force_data) > 0:
            sigmas_F = self.sigma_F**2 * np.ones((3 * np.sum([len(atoms) for atoms in training_force_data]),))
            local_sigmas[-len(sigmas_F) :] = sigmas_F

        # local_sigma_inv = np.diag(1 / local_sigmas)
        local_sigma_inv = dia_matrix((1 / local_sigmas, 0), shape=(len(local_sigmas), len(local_sigmas)))
        return local_sigma_inv

    def _solve(self, A: np.ndarray, Y: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Solve the linear system using QR decomposition and least squares

        Parameters
        ----------
        A : np.ndarray
            Matrix A
        Y : np.ndarray
            Matrix Y

        Returns
        -------
        np.ndarray
            Solution X

        """
        Q, R = qr(A)
        if Y is None:
            return lstsq(R, Q.T)[0]
        else:
            return lstsq(R, Q.T @ Y)[0]

    def _symmetrize(self, A: np.ndarray) -> np.ndarray:
        """
        Symmetrize a matrix

        Parameters
        ----------
        A : np.ndarray
            Matrix to symmetrize

        Returns
        -------
        np.ndarray
            Symmetrized matrix

        """
        return (A + A.T) / 2

    @staticmethod
    def sparsification_schedule(total_environments, sparse_environments, iteration, new_environments):
        """
        Schedule for sparsification.
        """
        if total_environments < sparse_environments * 10:
            return True
        elif iteration % 25 == 0:
            return True

        return False
