from timeit import default_timer as dt
from typing import Dict, List, Tuple, Union

import numpy as np
from ase import Atoms
from ase.calculators.calculator import all_changes
from scipy.linalg import cho_factor, cho_solve
from scipy.optimize import fmin_l_bfgs_b

from agox.models.ABC_model import ModelBaseClass
from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass
from agox.models.GPR.kernels import Kernel
from agox.utils import candidate_list_comprehension
from agox.utils.filters import EnergyFilter, FilterBaseClass
from agox.utils.ray import RayPoolUser


class GPR(ModelBaseClass, RayPoolUser):
    """
    Gaussian Process Regression model without any approximations.

    Parameters
    ----------

    descriptor : DescriptorBaseClass
        Descriptor object, has to be a global descriptor.
    kernel : Kernel
        Kernel object to use.
    prior : ModelBaseClass
        Prior model object.
    single_atom_energies : dict
        Dictionary of single atom energies.
    n_optimize : int
        Number of LML optimization restarts.
    optimizer_maxiter : int
        Maximum number of iterations for the optimizer.
    centralize : bool
        Whether to centralize the energy.
    filter : FilterBaseClass
        Filter object to choose which structures to include in the training set.
    use_ray : bool
        Whether to use ray for parallelization of hyperparameter optimization.
    """

    name = "GPR"

    supported_descriptor_types = ["global"]
    implemented_properties = ["energy", "forces", "uncertainty", "forces_uncertainty"]

    def __init__(
        self,
        descriptor: DescriptorBaseClass,
        kernel: Kernel,
        prior: ModelBaseClass = None,
        single_atom_energies: Union[List[float], Dict[str, float]] = None,
        n_optimize: int = None,
        optimizer_maxiter: int = 100,
        centralize: bool = True,
        filter: FilterBaseClass = EnergyFilter(),
        use_ray=True,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        descriptor : DescriptorBaseClass
            Descriptor object.
        kernel : KernelBaseClass
            Kernel object.
        feature_method : function
            Feature method.
        prior : ModelBaseClass
            Prior model object.
        single_atom_energies : dict
            Dictionary of single atom energies.
        centralize : bool
            Whether to centralize the energy.
        """
        ModelBaseClass.__init__(self, filter=filter, **kwargs)
        RayPoolUser.__init__(self)
        assert (
            descriptor.descriptor_type in self.supported_descriptor_types
        ), "Only global descriptors are supported, use SparseGPR for local descriptors instead."

        for attr in ["alpha", "K_inv", "X", "K", "kernel", "Y", "mean_energy", "_ready_state"]:
            self.add_dynamic_attribute(attr)

        self.descriptor = descriptor
        self.kernel = kernel
        self.prior = prior
        self.single_atom_energies = single_atom_energies

        self.n_optimize = n_optimize
        self.optimizer_maxiter = optimizer_maxiter
        self.centralize = centralize

        self.add_save_attributes(["X", "Y", "mean_energy", "K", "K_inv", "alpha", "kernel.theta"])

        # We add self to the pool, it will keep an updated copy of the model on the pool
        self.n_optimize = n_optimize
        self.use_ray = use_ray
        if self.use_ray:
            self.actor_model_key = self.pool_add_module(self)
            self.self_synchronizing = True  # Defaults to False, inherited from Module.
            if n_optimize is None:
                self.n_optimize = int(self.cpu_count)
        else:
            if n_optimize is None:
                self.n_optimize = 1

    def train(self, training_data: List[Atoms], **kwargs) -> None:
        """
        Train the model.

        Parameters
        ----------
        training_data : list
            List of Atoms objects.

        """

        self.training_timings = {}
        t_total = dt()

        self._data_before_filter = len(training_data)
        if self.filter is not None:
            training_data, _ = self.filter(training_data)
        self._data_after_filter = len(training_data)

        self.X, self.Y = self._preprocess(training_data)

        self._training_record(training_data)

        self._train_model(training_data)

        validation = self.validate()

        self.print_model_info(validation=validation)
        self.atoms = None

        self.training_timings["total"] = dt() - t_total

    @candidate_list_comprehension
    def predict_energy(self, atoms: Atoms, k: np.ndarray = None, x: np.ndarray = None, **kwargs) -> float:
        if not self.ready_state:
            e_pred = 0
            return self._postprocess_energy(atoms, e_pred)

        k = self._get_kernel_vector(k, x, atoms)

        e_pred = np.sum(k.T @ self.alpha)

        return self._postprocess_energy(atoms, e_pred)

    @candidate_list_comprehension
    def predict_uncertainty(
        self, atoms: Atoms, k: np.ndarray = None, k0: np.ndarray = None, x: np.ndarray = None, **kwargs
    ) -> float:
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
            return 0

        if x is None:
            x = self._get_features(atoms)

        k = self._get_kernel_vector(k, x, atoms)

        if k0 is None:
            k0 = self.kernel(x, x)
        var = k0 - k.T @ self.K_inv @ k
        var = float(var.squeeze())
        return np.sqrt(max(var, 0))

    @candidate_list_comprehension
    def predict_forces(self, atoms: Atoms, dk_dr: np.ndarray = None, **kwargs) -> np.ndarray:
        """
        Predict forces for a given atoms object

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object

        Returns
        -------
        np.ndarray
            Forces
        """
        if not self.ready_state:
            forces = np.zeros((len(atoms), 3))
            return self._postprocess_forces(atoms, forces)

        if dk_dr is None:
            dk_dr = self._get_kernel_derivative(atoms)

        # Predict the forces:
        forces = (-dk_dr.sum(axis=0) @ self.alpha).squeeze()

        return self._postprocess_forces(atoms, forces)

    @candidate_list_comprehension
    def predict_uncertainty_forces(
        self,
        atoms: Atoms,
        x: np.ndarray = None,
        k: np.ndarray = None,
        k0: np.ndarray = None,
        dk_dr: np.ndarray = None,
        **kwargs,
    ) -> np.ndarray:
        """
        Predict forces uncertainty for a given atoms object

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object

        Returns
        -------
        np.ndarray
            Forces uncertainty

        """

        if "forces_uncertainty" not in self.implemented_properties or not self.ready_state:
            return np.zeros((len(atoms), 3))

        if x is None:
            x = self._get_features(atoms)

        k = self._get_kernel_vector(k, x, atoms)

        if dk_dr is None:
            dk_dr = self._get_kernel_derivative(atoms).sum(axis=0)

        if k0 is None:
            k0 = self.kernel(x, x)

        var = k0 - k.T @ self.K_inv @ k
        if var < 0:
            std_force = np.zeros((len(atoms), 3))
        else:
            std_force = (1 / np.sqrt(var) * dk_dr @ self.K_inv @ k).squeeze()

        return std_force

    @candidate_list_comprehension
    def predict_energy_and_uncertainty(self, atoms, x=None, k=None, k0=None, **kwargs):
        if x is None:
            x = self._get_features(atoms)

        k = self._get_kernel_vector(k, x, atoms)

        energy = self.predict_energy(atoms, k=k, **kwargs)
        uncertainty = self.predict_uncertainty(atoms, k=k, k0=k0, x=x, **kwargs)

        return energy, uncertainty

    def converter(self, atoms: Atoms, derivatives=True, reduced: bool = False, **kwargs) -> Dict[str, np.ndarray]:
        """
        Precompute all necessary quantities for the model

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object

        Returns
        -------
        dict
            Dictionary with all necessary quantities

        """
        x = self._get_features(atoms)
        k = self.kernel(self.X, x)
        k0 = self.kernel(x, x)

        d = {"x": x, "k": k, "k0": k0}
        if derivatives:
            dx_dr = self.descriptor.get_feature_gradient(atoms)
            dk_dr = self._get_kernel_derivative(atoms, x=x, dX_dr=dx_dr)
            d["dk_dr"] = dk_dr
            d["dx_dr"] = dx_dr

        return d

    @property
    def single_atom_energies(self) -> np.ndarray:
        """
        Get the single atom energies.

        Returns
        -------
        np.ndarray

        """
        return self._single_atom_energies

    @single_atom_energies.setter
    def single_atom_energies(self, s: Union[Dict, np.ndarray]) -> None:
        """
        Set the single atom energies.
        Index number corresponds to the atomic number ie. 1 = H, 2 = He, etc.

        Parameters
        ----------
        s : dict or np.ndarray
            Dictionary/array of single atom energies.

        """
        if isinstance(s, np.ndarray):
            self._single_atom_energies = s
        elif isinstance(s, dict):
            self._single_atom_energies = np.zeros(100)
            for i, val in s.items():
                self._single_atom_energies[i] = val
        elif s is None:
            self._single_atom_energies = np.zeros(100)

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
            "------ Training Info ------",
            "Training data size: {}".format(self.X.shape[0]),
            "Neg. log marginal likelihood.: {:.2f}".format(self._nlml),
            "Hyperparameter optimizations: {}".format(self._nlml_opts),
        ]

        return out

    def calculate(
        self,
        atoms: Atoms = None,
        properties: List[str] = ["energy"],
        system_changes=all_changes,
    ) -> None:
        super().calculate(atoms=atoms, properties=properties, system_changes=system_changes)
        if "uncertainty" in properties:
            self.results["uncertainty"] = self.predict_uncertainty(atoms)
        if "force_uncertainty" in properties:
            self.results["force_uncertainty"] = self.predict_forces_uncertainty(atoms)

    def hyperparameter_search(self) -> None:
        """
        Hyperparameter search

        """
        initial_parameters = []
        initial_parameters.append(self.kernel.theta.copy())
        if self.n_optimize > 0:
            for _ in range(self.n_optimize - 1):
                init_theta = np.random.uniform(
                    size=(len(self.kernel.bounds),),
                    low=self.kernel.bounds[:, 0],
                    high=self.kernel.bounds[:, 1],
                )
                initial_parameters.append(init_theta)

            fmins = []
            thetas = []
            for init_theta in initial_parameters:
                theta_min, nll_min = self._hyperparameter_optimize(init_theta=init_theta)
                fmins.append(nll_min)
                thetas.append(theta_min)

            self.kernel.theta = thetas[np.argmin(np.array(fmins))]
            self._nlml = np.min(fmins)
            self._nlml_opts = len(fmins)
        else:
            self._nlml = np.inf
            self._nlml_opts = 0

    def hyperparameter_search_parallel(self, relax=True) -> None:
        if self.n_optimize == 0:
            self._nlml = np.inf
            self._nlml_opts = 0
            return

        bounds = self.kernel.bounds
        initial = np.random.uniform(size=(self.n_optimize, len(bounds)), low=bounds[:, 0], high=bounds[:, 1])
        initial[0, :] = self.kernel.theta

        modules = [
            [self.actor_model_key]
        ] * self.n_optimize  # All jobs use the same model that is already on the actor.

        # Create a list of all the arguments that should be passed to the function.
        args = [[init_theta] for init_theta in initial]
        kwargs = [{"relax": relax} for _ in range(self.n_optimize)]

        # Submit the jobs.
        outputs = self.pool_map(ray_hyperparameter_optimize, modules, args, kwargs)

        # Get the best theta
        likelihood = [output[1] for output in outputs]
        best_theta = outputs[np.argmin(likelihood)][0]

        self._nlml_opts = len(likelihood)

        # Set the best theta
        self.kernel.theta = best_theta
        self._nlml = np.min(likelihood)

    def monte_carlo_hyperparameter_search(self) -> None:
        """
        Hyperparameter search using Monte Carlo sampling

        """
        initial_parameters = []
        initial_parameters.append(self.kernel.theta.copy())
        if self.n_optimize > 0:
            for _ in range(self.n_optimize - 1):
                init_theta = np.random.uniform(
                    size=(len(self.kernel.bounds),),
                    low=self.kernel.bounds[:, 0],
                    high=self.kernel.bounds[:, 1],
                )
                initial_parameters.append(init_theta)

            fmins = []
            thetas = []
            for theta in initial_parameters:
                nlml = -self._log_marginal_likelihood(theta)
                fmins.append(nlml)
                thetas.append(theta)

            self.kernel.theta = thetas[np.argmin(np.array(fmins))]
            self._nlml = np.min(fmins)
        else:
            self._nlml = np.inf

    def _get_features(self, atoms: Atoms) -> np.ndarray:
        """
        Get features for a given atoms object

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object

        Returns
        -------
        np.ndarray
            Features

        """
        f = self.descriptor.get_features(atoms)

        if isinstance(f, np.ndarray) and len(f.shape) == 1:
            f = f.reshape(1, -1)

        f = np.vstack(f)
        return f

    def _get_kernel_vector(self, k: np.ndarray = None, x: np.ndarray = None, atoms: Atoms = None) -> np.ndarray:
        """
        Get the kernel vector for a given atoms object

        Parameters
        ----------
        k : np.ndarray, optional
            Kernel vector, by default None
        x : np.ndarray, optional
            Features, by default None
        atoms : ase.Atoms, optional
            Atoms object, by default None

        Returns
        -------
        np.ndarray
            Kernel vector
        """

        if k is not None:
            return k

        if x is None:
            x = self._get_features(atoms)

        return self.kernel(self.X, x)

    def _get_kernel_derivative(
        self, atoms: Atoms, x: np.ndarray = None, dX_dr: np.ndarray = None, dk_dX: np.ndarray = None
    ) -> np.ndarray:
        """
        Get the kernel derivative wrt. the Carteisian coordinates r.

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object
        x : np.ndarray, optional
            Features, by default None
        dX_dr : np.ndarray, optional
            Derivatives of the features wrt. the Carteisian coordinates r, by default None
        dk_dX : np.ndarray, optional
            Derivatives of the kernel wrt. the features, by default None

        Returns
        -------
        np.ndarray
            Derivatives of the kernel wrt. the Carteisian coordinates r.
        """
        # Get features and derivatives:
        if x is None:
            x = self._get_features(atoms)  # [centers, features]

        if dX_dr is None:
            dX_dr = self.descriptor.get_feature_gradient(atoms)  # [centers, atoms, 3, features]

        # Get kernel derivatives:
        if dk_dX is None:
            dk_dX = np.array([self.kernel.get_feature_gradient(self.X, x[i : i + 1]) for i in range(len(x))])

        # Convert to derivatives wrt. Carteisian coordinates r.
        dk_dr = np.einsum("nadf,nmf->nadm", dX_dr, dk_dX)  # [centers, atoms, 3, features]

        return dk_dr

    def _train_model(self, training_data: List[Atoms], synchronize=True) -> None:
        """
        Train the model

        """
        if self.use_ray:
            self.pool_synchronize(attributes=["X", "Y"], writer=self.writer)
            self.hyperparameter_search_parallel()
        else:
            self.hyperparameter_search()

        self.K = self.kernel(self.X)
        self.alpha, self.K_inv, _ = self._solve(self.K, self.Y)
        self.ready_state = True

        if self.use_ray and synchronize:
            self.pool_synchronize(
                attributes=["alpha", "K_inv", "kernel", "K", "mean_energy", "_ready_state"], writer=self.writer
            )

    def _preprocess(self, data: List[Atoms]) -> None:
        """
        Preprocess the training data.

        Parameters
        ----------
        data : list
            List of Atoms objects.

        Returns
        -------
        np.ndarray
            Features.
        np.ndarray
            Targets.

        """
        self._N_energies = len(data)
        Y = np.expand_dims(
            np.array([d.get_potential_energy() - sum(self.single_atom_energies[d.get_atomic_numbers()]) for d in data]),
            axis=1,
        )

        # Calculate the prior:
        if self.prior is None:
            self.prior_energy = np.zeros(Y.shape)
        else:
            self.prior_energy = np.expand_dims(np.array([self.prior.predict_energy(d) for d in data]), axis=1)

        Y -= self.prior_energy

        # Energy centralization:
        if self.centralize:
            self.mean_energy = np.mean(Y)
        else:
            self.mean_energy = 0

        Y -= self.mean_energy

        # Calculate features:
        t_feature = dt()
        X = self._get_features(data)
        self.training_timings["feature"] = dt() - t_feature

        return X, Y

    def _postprocess_energy(self, atoms: Atoms, e_pred: float) -> float:
        """
        Postprocess the energy.

        Parameters
        ----------
        atoms : Atoms
            Atoms object.
        e_pred : float
            Predicted energy.

        Returns
        -------
        float
            Postprocessed energy.
        """
        if self.prior is None:
            prior = 0
        else:
            prior = self.prior.predict_energy(atoms)

        sae = sum(self.single_atom_energies[atoms.get_atomic_numbers()])

        total = e_pred + prior + sae

        if hasattr(self, "mean_energy"):
            total += self.mean_energy

        return total

    def _postprocess_forces(self, atoms: Atoms, f_pred: np.ndarray) -> np.ndarray:
        """
        Postprocess the forces.

        Parameters
        ----------
        atoms : Atoms
            Atoms object.
        f_pred : np.ndarray
            Predicted forces.

        Returns
        -------
        np.ndarray
            Postprocessed forces.
        """
        if self.prior is None:
            prior = 0
        else:
            prior = self.prior.predict_forces(atoms)

        return f_pred + prior

    def _hyperparameter_optimize(self, init_theta: np.ndarray = None) -> Tuple[np.ndarray, float]:
        """
        Hyperparameter optimization

        Parameters
        ----------
        init_theta : np.ndarray
            Initial theta

        Returns
        -------
        np.ndarray
            Optimal theta

        """

        def f(theta):
            P, grad_P = self._log_marginal_likelihood_gradient(theta)
            if np.isnan(P):
                return np.inf, np.zeros_like(theta, dtype="float64")
            P, grad_P = -float(P), -np.asarray(grad_P, dtype="float64")
            return P, grad_P

        bounds = self.kernel.bounds

        if init_theta is None:
            self.key, key = np.random.split(self.key)
            init_theta = np.random.uniform(key, shape=(len(bounds),), minval=bounds[:, 0], maxval=bounds[:, 1])

        theta_min, fmin, conv = fmin_l_bfgs_b(
            f,
            np.asarray(init_theta, dtype="float64"),
            bounds=np.asarray(bounds, dtype="float64"),
            maxiter=self.optimizer_maxiter,
        )

        return theta_min, fmin

    def _solve(self, K: np.ndarray, Y: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Solve the linear system

        Parameters
        ----------
        K : np.ndarray
            Kernel matrix
        Y : np.ndarray
            Target values

        Returns
        -------
        np.ndarray
            Alpha
        np.ndarray
            Inverse of kernel matrix
        np.ndarray
            Cholesky decomposition of kernel matrix

        """
        L, lower = cho_factor(K)
        alpha = cho_solve((L, lower), Y)
        K_inv = cho_solve((L, lower), np.eye(K.shape[0]))
        return alpha, K_inv, (L, lower)

    def _log_marginal_likelihood(self, theta: np.ndarray) -> float:
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
        t = self.kernel.theta.copy()
        self.kernel.theta = theta
        K = self.kernel(self.X)
        self.kernel.theta = t

        alpha, K_inv, (L, lower) = self._solve(K, self.Y)

        log_P = (
            -0.5 * np.einsum("ik,ik->k", self.Y, alpha)
            - np.sum(np.log(np.diag(L)))
            - K.shape[0] / 2 * np.log(2 * np.pi)
        )

        return np.sum(log_P)

    def _log_marginal_likelihood_gradient(self, theta: np.ndarray) -> Tuple[float, np.ndarray]:
        """
        Marginal log likelihood gradient

        Parameters
        ----------
        theta : np.ndarray
            Kernel parameters

        Returns
        -------
        float
            Marginal log likelihood
        np.ndarray
            Marginal log likelihood gradient

        """
        t = self.kernel.theta.copy()
        self.kernel.theta = theta
        K, K_hp_gradient = self.kernel(self.X, eval_gradient=True)
        self.kernel.theta = t

        alpha, K_inv, (L, lower) = self._solve(K, self.Y)

        log_P = (
            -0.5 * np.einsum("ik,ik->k", self.Y, alpha)
            - np.sum(np.log(np.diag(L)))
            - K.shape[0] / 2 * np.log(2 * np.pi)
        )

        inner = np.squeeze(np.einsum("ik,jk->ijk", alpha, alpha), axis=2) - K_inv
        inner = inner[:, :, np.newaxis]

        grad_log_P = np.sum(0.5 * np.einsum("ijl,ijk->kl", inner, K_hp_gradient), axis=-1)
        return log_P, grad_log_P


def ray_hyperparameter_optimize(model, init_theta, relax=True):
    """
    Hyperparameter optimization

    Parameters
    ----------
    model : Model
        GPR model
    n_opt : int
        Number of optimization steps
    use_current_theta : bool
        Use current theta as initial theta

    Returns
    -------
    np.ndarray
        Optimal theta
    float
        Optimal log marginal likelihoodg

    """

    bounds = model.kernel.bounds

    def f(theta):
        P, grad_P = model._log_marginal_likelihood_gradient(theta)
        if np.isnan(P):
            return np.inf, np.zeros_like(theta, dtype="float64")
        P, grad_P = -float(P), -np.asarray(grad_P, dtype="float64")
        return P, grad_P

    if relax:
        theta_min, fmin, conv = fmin_l_bfgs_b(
            f,
            np.asarray(init_theta, dtype="float64"),
            bounds=np.asarray(bounds, dtype="float64"),
            maxiter=model.optimizer_maxiter,
        )
    else:
        theta_min = init_theta
        fmin = -model._log_marginal_likelihood(init_theta)

    return theta_min, fmin
