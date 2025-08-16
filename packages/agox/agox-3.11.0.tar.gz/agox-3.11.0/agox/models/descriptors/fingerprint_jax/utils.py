from dataclasses import dataclass
from functools import partial
from typing import Dict, Optional

import jax
import jax.numpy as jnp
import numpy as np
from ase import Atoms
from matscipy.ffi import first_neighbours
from matscipy.neighbours import neighbour_list, triplet_list


@dataclass
class AtomsData:
    R: jnp.ndarray
    Z: jnp.ndarray
    idx_i: jnp.ndarray
    idx_j: jnp.ndarray
    cell_shift: jnp.ndarray
    cell: jnp.ndarray
    idx_triplet_ij: Optional[jnp.ndarray] = None
    idx_triplet_ik: Optional[jnp.ndarray] = None


class AtomsConverter:
    def __init__(
        self,
        r_cut: float = 5.0,
        collect_triplet: bool = True,
        r_cut_angular: float = 5.0,
        volume_min: float = 1e-5,
        max_pair_size: int = 0,
        max_triplet_size: int = 0,
        pad: bool = False,
    ):
        self.r_cut = r_cut
        self.collect_triplet = collect_triplet
        self.r_cut_angular = r_cut_angular
        self.volume_min = volume_min
        self.max_pair_size = max_pair_size
        self.max_triplet_size = max_triplet_size
        self.pad = pad

    def convert(self, atoms: Atoms) -> Dict[str, np.ndarray]:
        """
        Convert an ASE Atoms object to ML inputs

        Parameters:
            atoms: an ASE Atoms object
            r_cut: float, radius cutoff for determining neighbors
            collect_triplet: boolean, whether indices of triplets are collected
            r_cut_angular: float, angular cutoff for determining triplets
            n_max_neighbors: int, maintain a constant shape of neighbour_list
            volume_min: float, minimum volume of atoms (matscipy needs volume in neighbour_list)
        """

        R = atoms.get_positions()
        Z = atoms.get_atomic_numbers()

        # avoid too small cell in matscipy neighborlist calculation
        # useful for non-periodic structure and when atoms.cell is None
        if atoms.cell.volume < self.volume_min:
            atoms = atoms.copy()
            cell_buffer = 2 * self.r_cut
            new_cell = np.ptp(atoms.get_positions(), axis=0) + cell_buffer
            atoms.set_cell(new_cell)

        # each pair will be generated twice
        idx_i, idx_j, r_ij, cell_shift = neighbour_list("ijdS", atoms, cutoff=self.r_cut)
        n_pair_raw = len(idx_i)
        if self.pad:
            max_pair_size = np.max([self.max_pair_size, len(idx_i)])
            n_pair_pad = max_pair_size - len(idx_i)
            pad_mode = "constant"

            idx_i = np.pad(idx_i, (0, n_pair_pad), pad_mode)
            idx_j = np.pad(idx_j, (0, n_pair_pad), pad_mode)

            # this makes sure that r_ij at padded indices are larger than the set cutoff
            #   therefore zero contribution to feature values
            cell_shift = np.pad(cell_shift, ((0, n_pair_pad), (0, 0)), pad_mode, constant_values=10)

        inputs = {
            "R": R,
            "Z": Z,
            "idx_i": idx_i,
            "idx_j": idx_j,
            "cell_shift": cell_shift,
            "cell": atoms.get_cell()[:],  # do not store ASE Cell object
        }

        if self.collect_triplet:
            first_n = first_neighbours(len(atoms), idx_i[:n_pair_raw])
            ij_triplet, ik_triplet = triplet_list(first_n, r_ij, self.r_cut_angular)

            if self.pad:
                max_triplet_size = np.max([self.max_triplet_size, len(ij_triplet)])
                n_triplet_pad = max_triplet_size - len(ij_triplet)
                ij_triplet = np.pad(ij_triplet, (0, n_triplet_pad), pad_mode)
                ik_triplet = np.pad(ik_triplet, (0, n_triplet_pad), pad_mode)

            inputs["idx_triplet_ij"] = ij_triplet
            inputs["idx_triplet_ik"] = ik_triplet

        data = AtomsData(**inputs)
        self.max_pair_size = max_pair_size
        self.max_triplet_size = max_triplet_size

        return data


def radial_cutoff(r: float, r_cut: float) -> float:
    """
    A hard cutoff function
    """
    return r * (r < r_cut)


def angular_cutoff(r: float, r_cut: float, gamma: int = 2) -> float:
    """
    A cutoff function for angular features
    """
    value = 1 + gamma * (r / r_cut) ** (gamma + 1) - (gamma + 1) * (r / r_cut) ** gamma
    value += gamma == 0
    value *= r < r_cut
    return value


def angle_between(v1, v2):
    """Returns the angle in radians between two unit vectors 'v1' and 'v2'
    https://stackoverflow.com/questions/2827393/angles-between-two-n-dimensional-vectors-in-python
    """
    return jnp.arccos(jnp.clip(jnp.dot(v1, v2), -1.0, 1.0))


@partial(jax.vmap, in_axes=(0, 0))
def element_wise_angle_between(*args):
    return angle_between(*args)


def gaussian_cdf(x: float, mu: float, sigma: float) -> float:
    """
    Calculate gaussian cumulative distribution function (cdf) from lower bound -inf to upper bound `x`

    Parameters:
        x: upper bound of the cdf
        mu: center of the gaussian
        sigma: standard deviation of the gaussian
    """
    cdf_x = 0.5 * (1 + jax.scipy.special.erf((x - mu) / sigma / jnp.sqrt(2)))
    return cdf_x


@partial(jax.vmap, in_axes=(None, 0, None), out_axes=0)
def gaussian_cdf_matrix(*args):
    """
    return: shape (n_mu, n_x)
    """
    return gaussian_cdf(*args)


@partial(jax.jit, static_argnums=[6, 7, 8, 9, 10])
def compute_radial_features(
    R: jax.Array,
    idx_i: jax.Array,
    idx_j: jax.Array,
    idx_pair: jax.Array,
    cell_shift: jax.Array,
    cell: jax.Array,
    n_unique_pair: int,  # static_arg from here
    r_cut: float,
    n_bins: int,
    sigma: float,
    prefactor: float,
) -> jax.Array:
    """
    Compute radial features

    Parameters:
        R: atomic positions (n_atoms, 3)
        idx_i: atomic index of atom 'i' in the pair (n_pair, )
        idx_j: atomic index of atom 'j' in the pair (n_pair, )
        idx_pair: pair index (n_pair, )
        cell_shift: cell_shift
        cell: cell
        n_unique_pair: number of unique pair
        r_cut: radial cutoff
        n_bins: number of bins
        sigma: gaussian width
        prefactor: prefactor on feature values

    Return:
        Radial features, (n_unique_pair*n_bins, )
    """
    R_ij = R[idx_i] - R[idx_j] + cell_shift.dot(cell)
    r_ij = jnp.linalg.norm(R_ij, axis=1, keepdims=True)

    x = jnp.linspace(0, r_cut, n_bins + 1)

    cdf = gaussian_cdf_matrix(x, r_ij, sigma)

    # AGOX's Cython implementation does not have this prefactor
    cdf *= sigma * jnp.sqrt(2 * jnp.pi)
    cdf *= 1 / r_ij**2

    integral_in_bins = cdf[:, 1:] - cdf[:, :-1]

    radial_features = jnp.zeros((n_unique_pair, n_bins))
    radial_features = radial_features.at[idx_pair].add(integral_in_bins)
    radial_features = 1 * radial_features.flatten()  # avoid double sum i,j and j,i

    radial_features *= prefactor

    return radial_features


@partial(jax.jit, static_argnums=[6, 7, 8, 9, 10])
@jax.jacfwd
def compute_radial_feature_grad(*args):
    """
    Compute the derivative of radial features w.r.t the first argument (atomic positions)

    Parameters are similar with compute_radial_features()

    Return:
        Rarial feature gradients, (n_unique_pair*n_bins, n_atoms, 3)
    """
    # print('radial grad')
    return compute_radial_features(*args)


@partial(jax.jit, static_argnums=[8, 9, 10, 11, 12, 13])
def compute_angular_features(
    R: jax.Array,
    idx_i: jax.Array,
    idx_j: jax.Array,
    idx_triplet_ij: jax.Array,
    idx_triplet_jk: jax.Array,
    idx_triplet: jax.Array,
    cell_shift: jax.Array,
    cell: jax.Array,
    n_unique_triplet: int,  # static_arg from here
    r_cut: float,
    n_bins: int,
    sigma: float,
    gamma: int,
    prefactor: float,
) -> jax.Array:
    """
    Compute angular features

    Parameters are similar with compute_radial_features()

    Return:
        Angular features, (n_unique_triplet*n_bins, )
    """
    R_ij = R[idx_i] - R[idx_j] + cell_shift.dot(cell)
    r_ij = jnp.linalg.norm(R_ij, axis=1, keepdims=True)

    R_ij_triplet = R_ij[idx_triplet_ij]
    R_ik_triplet = R_ij[idx_triplet_jk]

    r_ij_triplet = r_ij[idx_triplet_ij]
    r_ik_triplet = r_ij[idx_triplet_jk]

    # angles centered at atom 'i' for all angles
    angle_ijk = element_wise_angle_between(R_ij_triplet / r_ij_triplet, R_ik_triplet / r_ik_triplet)

    x = jnp.linspace(0, jnp.pi, n_bins + 1)
    cdf = gaussian_cdf_matrix(x, angle_ijk, sigma)
    integral_in_bins = cdf[:, 1:] - cdf[:, :-1]

    integral_in_bins *= sigma * jnp.sqrt(2 * jnp.pi)
    integral_in_bins *= angular_cutoff(r_ij_triplet, r_cut, gamma) * angular_cutoff(r_ik_triplet, r_cut, gamma)
    # make sure padded triplets have zero contributions to angular features
    integral_in_bins *= jnp.where(idx_triplet_ij == idx_triplet_jk, 0, 1)[:, None]

    angular_features = jnp.zeros((n_unique_triplet, n_bins))
    angular_features = angular_features.at[idx_triplet].add(integral_in_bins)
    angular_features = 0.5 * angular_features.flatten()  # avoid double sum i,j,k and i,k,j

    angular_features *= prefactor

    return angular_features


@partial(jax.jit, static_argnums=[8, 9, 10, 11, 12, 13, 14])
@jax.jacfwd
def compute_angular_feature_grad(*args):
    """
    Compute the derivative of angular features w.r.t the first argument (atomic positions)

    Parameters are similar with compute_angular_features()

    Return:
        Angular feature gradients, (n_unique_triplet*n_bins, n_atoms, 3)
    """
    # print('angular grad')
    return compute_angular_features(*args)


@jax.jit
def get_pair_index(unique_pairs: jax.Array, z_i: jax.Array, z_j: jax.Array) -> jax.Array:
    """
    Get the sorted index of a given pair

    Parameters:
        unique_pairs: jax.Array, atomic numbers of unique pairs
        z_i: jax.Array, atomic number of atom 'i' in the pair
        z_j: jax.Array, atomic number of atom 'j' in the pair

    Return:
        jax.Array, shape: (n_pair, )
    """
    z_ij = jnp.sum(jnp.stack((z_i, z_j), axis=1).sort(axis=1) * jnp.array([10, 1]), axis=1)
    idx_pair = unique_pairs.searchsorted(z_ij)
    return idx_pair


@jax.jit
def get_triplet_index(unique_triplets: jax.Array, z_i: jax.Array, z_j: jax.Array, z_k: jax.Array) -> jax.Array:
    """
    Get the sorted index of a given triplet

    Parameters:
        unique_triplets: jax.Array, atomic numbers of unique triplets
        z_i: jax.Array, atomic number of atom 'i' in the triplet
        z_j: jax.Array, atomic number of atom 'j' in the triplet
        z_k: jax.Array, atomic number of atom 'k' in the triplet
    Return:
        jax.Array, shape: (n_triplet, )
    """
    # assert len(z_i) == len(z_j) == len(z_k)
    z_jk_sorted = jnp.sum(jnp.stack((z_j, z_k), axis=1).sort(axis=1) * jnp.array([10, 1]), axis=1)
    z_ijk = 100 * z_i + z_jk_sorted
    idx_triplet = unique_triplets.searchsorted(z_ijk)
    return idx_triplet
