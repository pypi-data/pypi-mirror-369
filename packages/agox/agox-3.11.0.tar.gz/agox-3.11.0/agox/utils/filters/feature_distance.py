from typing import List

import numpy as np
from ase import Atoms

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass
from agox.utils.filters.ABC_filter import FilterBaseClass


class Cluster:
    def __init__(self, representative: str):
        self.representative = representative
        self.structures = []
        self.energies = []
        self.features = []
        self.indices = []

    def add_member(self, atoms: Atoms, index: int, feature: np.ndarray):
        self.indices.append(index)
        self.structures.append(atoms)
        self.features.append(feature)

        try:
            energy = atoms.get_potential_energy()
        except:
            energy = 0
        self.energies.append(energy)

        if self.representative == "energy":
            self.rep_index = np.argmin(self.energies)
        elif self.reepresentative == "first":
            self.rep_index = 0

    def get_representative_member(self) -> Atoms:
        return self.structures[self.rep_index]

    def get_representative_feature(self) -> np.ndarray:
        return self.features[self.rep_index]

    def get_representative_index(self) -> int:
        return self.indices[self.rep_index]


class FeatureDistanceFilter(FilterBaseClass):
    name = "FeatureDistanceFilter"

    """
    Filter that removes duplicates structures based on the distance between their features.

    Parameters
    ----------
    descriptor: DescriptorBaseClass
        Descriptor used to calculate the features.
    threshold: float
        Maximum distance between features.
    representative: str
        Method used to select the representative structure.
        Options: "energy", "first"
    """

    def __init__(
        self,
        descriptor: DescriptorBaseClass,
        threshold: float,
        representative: str = "energy",
    ):
        super().__init__()
        self.descriptor = descriptor
        self.threshold = threshold

        assert representative in ["energy", "first"]
        self.representative = representative

    def _filter(self, atoms: List[Atoms]) -> np.ndarray:
        # Sum over atoms, converts local descriptors to global descriptors
        # Doesnt change global descriptors.
        F = np.array(self.descriptor.get_features(atoms)).sum(axis=1)

        clusters = []
        for i, atoms in enumerate(atoms):
            added_to_cluster = False
            for cluster in clusters:
                cluster_feature = cluster.get_representative_feature()
                if np.linalg.norm(F[i] - cluster_feature) < self.threshold:
                    cluster.add_member(atoms, i, F[i])
                    added_to_cluster = True
                    break

            if not added_to_cluster:
                new_cluster = Cluster(representative=self.representative)
                new_cluster.add_member(atoms, i, F[i])
                clusters.append(new_cluster)

        indices = [c.get_representative_index() for c in clusters]
        return indices
