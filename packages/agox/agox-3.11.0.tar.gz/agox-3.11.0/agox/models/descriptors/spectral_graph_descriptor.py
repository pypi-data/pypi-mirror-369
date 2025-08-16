import numpy as np
from ase.data import covalent_radii
from scipy.linalg import eigvalsh

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass


class SpectralGraphDescriptor(DescriptorBaseClass):
    name = "SpectralGraphDescriptor"
    descriptor_type = "global"

    def __init__(
        self,
        mode="adjacency",
        diagonal_mode="atomic_number",
        number_to_compare="all",
        descending=False,
        scale_factor=1.3,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.covalent_bond_scale_factor = scale_factor
        assert mode in ["adjacency", "laplacian"]
        self.mode = mode
        self.number_to_compare = number_to_compare

        assert diagonal_mode in ["atomic_number", "zero"]
        self.diagonal_mode = diagonal_mode

        # Ordering of eigenvalues:
        self.descending = descending

    def get_distances(self, candidate):
        distances_abs = candidate.get_all_distances(mic=True)
        numbers = candidate.get_atomic_numbers()
        r = [covalent_radii[number] for number in numbers]
        x, y = np.meshgrid(r, r)
        optimal_distances = x + y
        distances_rel = distances_abs / optimal_distances
        return distances_rel

    def get_adjacency_matrix(self, candidate):
        dist = self.get_distances(candidate)
        matrix = np.logical_and(dist > 1e-3, dist < self.covalent_bond_scale_factor).astype(int)
        if self.diagonal_mode == "atomic_number":
            matrix += np.diag(candidate.get_atomic_numbers())
        return matrix

    def get_laplacian_matrix(self, candidate):
        A = self.get_adjacency_matrix(candidate)
        D = np.diag(np.sum(A, axis=1))
        return D - A

    def get_graph(self, candidate):
        if self.mode == "adjacency":
            return self.get_adjacency_matrix(candidate)
        elif self.mode == "laplacian":
            return self.get_laplacian_matrix(candidate)

    def create_features(self, candidate):
        graph = self.get_graph(candidate)

        if self.number_to_compare == "all":
            number_to_compare = graph.shape[0] - 1
        else:
            number_to_compare = self.number_to_compare
        values = eigvalsh(graph, subset_by_index=(0, number_to_compare))

        if self.descending:
            values = np.flip(values)

        return values.reshape(1, -1)

    def get_number_of_centers(self, atoms):
        return len(atoms)

    @classmethod
    def from_atoms(cls, atoms, **kwargs):
        from agox.environments import Environment

        environment = Environment(template=atoms, symbols="", use_box_constraint=False, print_report=False)
        return cls(environment=environment, **kwargs)
