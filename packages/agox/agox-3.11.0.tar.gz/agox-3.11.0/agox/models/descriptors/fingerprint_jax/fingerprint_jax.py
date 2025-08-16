from itertools import combinations_with_replacement, product
from typing import Dict

import jax
import jax.numpy as jnp
import numpy as np
from ase import Atoms

from agox.candidates import StandardCandidate
from agox.models.descriptors import DescriptorBaseClass
from agox.models.descriptors.fingerprint_jax.utils import (
    AtomsConverter,
    AtomsData,
    compute_angular_feature_grad,
    compute_angular_features,
    compute_radial_feature_grad,
    compute_radial_features,
    get_pair_index,
    get_triplet_index,
)


class JaxFingerprint(DescriptorBaseClass):
    """
    Fingerprint descriptor

    Parameters:
    -----------
    r_cut_radial: float
        Cutoff for radial features.
    r_cut_angular: float
        Cutoff for angular features.
    n_bins_radial: int
        Number of bins for radial features.
    n_bins_angular: int
        Number of bins for angular features.
    sigma_radial: float
        Gaussian width for radial features.
    sigma_angular: float
        Gaussian width for angular features.
    gamma: int
        Parameter in angular cutoff function.
    eta: float
        Ratio of angular/radial features.
    n_max_neighbors: int
        Maxinum number of neighbors (to keep a constant shape of neighbor_list)
            Use len(atoms) for molecules
            Default 30 should work for periodic systems
            Increase this value when there is a zero padding error
            Set to -1 to turn this off
    use_angular: bool
        Whether angular features are calculated.
    """

    descriptor_type = "global"
    name = "JaxFingerprint"

    def __init__(
        self,
        r_cut_radial: float = 6.0,
        r_cut_angular: float = 6.0,
        n_bins_radial: int = 30,
        n_bins_angular: int = 30,
        sigma_radial: float = 0.2,
        sigma_angular: float = 0.2,
        gamma: int = 2,
        eta: float = 20,
        pad=True,
        n_max_neighbors: int = 30,
        use_angular: bool = True,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)

        self.r_cut_radial = r_cut_radial
        self.n_bins_radial = n_bins_radial
        self.sigma_radial = sigma_radial

        self.r_cut_angular = r_cut_angular
        self.n_bins_angular = n_bins_angular
        self.sigma_angular = sigma_angular

        self.gamma = gamma
        self.eta = eta
        self.n_max_neighbors = n_max_neighbors
        self.use_angular = use_angular

        self.max_pair = 0
        self.max_triplet = 0

        self.initialize_features(self.environment.get_template())

        self.atoms_converter = AtomsConverter(
            r_cut=r_cut_radial, collect_triplet=use_angular, r_cut_angular=r_cut_angular, pad=pad
        )

    def get_number_of_centers(self, atoms: Atoms) -> int:
        return 1

    def initialize_features(self, template: Atoms) -> None:
        """Compute unique pairs, triples and feature dimensions
        (called when the stoichiometry changes, no jax here)

        Parameters:
            template: an ASE Atoms object contains information about atomic_numbers, pbc, ...
        """

        periodic = template.get_pbc().any()
        numbers = template.get_atomic_numbers()
        unique, counts = np.unique(numbers, return_counts=True)

        # pairs, the center atom i does not matter
        if periodic:
            pairs = np.array(list(combinations_with_replacement(unique, 2)))
        else:
            pairs = []
            for z_ij in combinations_with_replacement(unique, 2):
                n_valid_number = 0
                for z, c in zip(unique, counts):
                    if z_ij.count(z) <= c:
                        n_valid_number += 1
                if n_valid_number == len(unique):
                    pairs.append(z_ij)
            pairs = np.array(pairs)
        self.pairs = np.sum(pairs * [10, 1], axis=1)

        # triplets, the center atom i matters
        if self.use_angular:
            if periodic:
                triplets = np.array(list(product(unique, repeat=3)))
                triplets = triplets[triplets[:, 1] <= triplets[:, 2]]  # i,j,k is identical to i,k,j
            else:
                triplets = []
                for z_ijk in product(unique, repeat=3):
                    if z_ijk[1] <= z_ijk[2]:
                        n_valid_number = 0
                        for z, c in zip(unique, counts):
                            if z_ijk.count(z) <= c:
                                n_valid_number += 1
                        if n_valid_number == len(unique):
                            triplets.append(z_ijk)
                triplets = np.array(triplets)
                print(triplets)
            self.triplets = np.sum(triplets * [100, 10, 1], axis=1)

    def create_features(self, atoms: Atoms, inputs: Dict = None) -> jax.Array:
        if inputs is None:
            inputs = self.converter(atoms)

        features = self._create_radial_features(inputs)

        if self.use_angular:
            angular_features = self._create_angular_features(inputs)
            features = jnp.concatenate((features, angular_features))

        # Reshape to [n_centers, n_features]
        features = features.reshape((self.get_number_of_centers(atoms), -1))

        return features

    def create_feature_gradient(self, atoms: Atoms, inputs: Dict = None) -> jax.Array:
        if inputs is None:
            inputs = self.converter(atoms)

        features_grad = self._create_radial_feature_gradients(inputs)

        if self.use_angular:
            angular_features_grad = self._create_angular_feature_gradients(inputs)
            features_grad = jnp.concatenate((features_grad, angular_features_grad))

        # Reshape to [n_centers, n_atoms, 3, n_features]
        features_grad = features_grad.reshape((self.get_number_of_centers(atoms), len(atoms), 3, -1))

        return features_grad

    @StandardCandidate.cache("inputs")
    def converter(self, atoms: Atoms) -> Dict:
        inputs = self.atoms_converter.convert(atoms)

        prefactor_radial = atoms.get_volume() / (4 * np.pi * len(atoms) ** 2 * self.r_cut_radial / self.n_bins_radial)
        inputs.prefactor_radial = prefactor_radial
        prefactor_angular = self.eta * atoms.get_volume() / len(atoms) ** 3
        inputs.prefactor_angular = prefactor_angular

        return inputs

    @classmethod
    def from_atoms(cls, atoms, **kwargs):
        """
        Create a descriptor from an atoms object.

        Parameters
        ----------
        atoms : Atoms object
            The atoms object used to setup the descriptor.
        kwargs : dict
            Any keyword arguments to pass to the descriptor.
        """
        from agox.environments import Environment

        environment = Environment(
            template=atoms,
            symbols="",
            use_box_constraint=False,
            print_report=False,
            confinement_cell=atoms.get_cell(),
        )
        return cls(environment=environment, **kwargs)

    def _create_radial_features(self, inputs: AtomsData) -> jax.Array:
        idx_pair = get_pair_index(self.pairs, inputs.Z[inputs.idx_i], inputs.Z[inputs.idx_j])

        radical_features = compute_radial_features(
            inputs.R,
            inputs.idx_i,
            inputs.idx_j,
            idx_pair,
            inputs.cell_shift,
            inputs.cell,
            len(self.pairs),
            self.r_cut_radial,
            self.n_bins_radial,
            self.sigma_radial,
            inputs.prefactor_radial,
        )

        return radical_features

    def _create_radial_feature_gradients(self, inputs: AtomsData) -> jax.Array:
        idx_pair = get_pair_index(self.pairs, inputs.Z[inputs.idx_i], inputs.Z[inputs.idx_j])

        radical_features_grad = compute_radial_feature_grad(
            inputs.R,
            inputs.idx_i,
            inputs.idx_j,
            idx_pair,
            inputs.cell_shift,
            inputs.cell,
            len(self.pairs),
            self.r_cut_radial,
            self.n_bins_radial,
            self.sigma_radial,
            inputs.prefactor_radial,
        )

        return radical_features_grad

    def _create_angular_features(self, inputs: AtomsData) -> jax.Array:
        idx_triplet_i = inputs.idx_i[inputs.idx_triplet_ij]
        idx_triplet_j = inputs.idx_j[inputs.idx_triplet_ij]
        idx_triplet_k = inputs.idx_j[inputs.idx_triplet_ik]

        idx_triplet = get_triplet_index(
            self.triplets,
            inputs.Z[idx_triplet_i],
            inputs.Z[idx_triplet_j],
            inputs.Z[idx_triplet_k],
        )

        angular_features = compute_angular_features(
            inputs.R,
            inputs.idx_i,
            inputs.idx_j,
            inputs.idx_triplet_ij,
            inputs.idx_triplet_ik,
            idx_triplet,
            inputs.cell_shift,
            inputs.cell,
            len(self.triplets),
            self.r_cut_angular,
            self.n_bins_angular,
            self.sigma_angular,
            self.gamma,
            inputs.prefactor_angular,
        )

        return angular_features

    def _create_angular_feature_gradients(self, inputs: AtomsData) -> jax.Array:
        idx_triplet_i = inputs.idx_i[inputs.idx_triplet_ij]
        idx_triplet_j = inputs.idx_j[inputs.idx_triplet_ij]
        idx_triplet_k = inputs.idx_j[inputs.idx_triplet_ik]

        idx_triplet = get_triplet_index(
            self.triplets,
            inputs.Z[idx_triplet_i],
            inputs.Z[idx_triplet_j],
            inputs.Z[idx_triplet_k],
        )

        angular_features_grad = compute_angular_feature_grad(
            inputs.R,
            inputs.idx_i,
            inputs.idx_j,
            inputs.idx_triplet_ij,
            inputs.idx_triplet_ik,
            idx_triplet,
            inputs.cell_shift,
            inputs.cell,
            len(self.triplets),
            self.r_cut_angular,
            self.n_bins_angular,
            self.sigma_angular,
            self.gamma,
            inputs.prefactor_angular,
        )

        return angular_features_grad


if __name__ == "__main__":
    # from ase.build import molecule

    from ase import Atoms
    from ase.io import read

    all_atoms = read("/home/machri/PythonPackages/agox-v2/agox/test/datasets/B12-dataset.traj", ":")
    use_angular = True
    eta = 5
    r_cut_all = 5.0
    n_bins = 30
    descriptor = JaxFingerprint.from_atoms(
        all_atoms[0],
        r_cut_radial=r_cut_all,
        r_cut_angular=r_cut_all,
        n_bins_radial=n_bins,
        use_angular=use_angular,
        eta=eta,
        n_max_neighbors=100,
    )

    # for atoms in tqdm(all_atoms):
    #     features = descriptor.get_features(atoms)
    #     # gradients = descriptor.get_feature_gradient(atoms)

    from agox.models.GPR import GPR
    from agox.models.GPR.kernels import RBF, Noise
    from agox.models.GPR.kernels import Constant as C

    kernel = C(1) * RBF(1) + Noise()
    model = GPR(descriptor=descriptor, kernel=kernel, use_ray=False, n_optimize=0)

    model.train(all_atoms[:5])

    E = model.predict_energy(all_atoms[5])
    print(E)
