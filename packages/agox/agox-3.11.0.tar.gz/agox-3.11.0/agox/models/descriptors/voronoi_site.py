from typing import Dict, Tuple, Union

import numpy as np
from ase.atoms import Atoms
from ase.geometry import get_distances
from numpy.typing import NDArray

from agox.candidates.standard import StandardCandidate
from agox.models.descriptors.voronoi import Voronoi

SiteMapping = Dict[Tuple[float, float], str]

fcc111_mapping = {
    (0.0, 0.0): "ontop",
    (0.5, 0.0): "bridge",
    (0.0, 0.5): "bridge",
    (0.5, 0.5): "bridge",
    (1 / 3, 1 / 3): "fcc",
    (2 / 3, 2 / 3): "hcp",
}

site_mappings = {"fcc111": fcc111_mapping}


class VoronoiSite(Voronoi):
    """Adsorption site-aware Voronoi graph descriptor.

    Parameters
    ----------
    site_mapping : Union[SiteMapping, str]
        Mapping from scaled unit cell coordinates (x, y) to special adsorption
        sites, or string representing predefined mappings from `site_mappings`.
    """

    name = "VoronoiSite"

    def __init__(self, *args, site_mapping: Union[SiteMapping, str], **kwargs):
        super().__init__(*args, **kwargs)

        if isinstance(site_mapping, str):
            if site_mapping not in site_mappings:
                raise KeyError(
                    f'{site_mapping} is not a valid site mapping key. ' f'Valid keys: {", ".join(site_mappings.keys())}'
                )
            site_mapping: SiteMapping = site_mappings.get(site_mapping)

        self.site_mapping = site_mapping

    def get_bond_matrix(self, candidate: StandardCandidate) -> NDArray:
        """Calculate the bond matrix for a candidate structure.

        Parameters
        ----------
        candidate : StandardCandidate
            Candidate structure.

        Returns
        -------
        NDArray
            Bond matrix.
        """
        voronoi_bond_matrix = super().get_bond_matrix(candidate)

        adsorbate = Atoms(candidate)[candidate.get_optimize_indices()]
        labels = self._assign_labels(adsorbate)

        diagonal = np.zeros(len(self.indices))
        for label_idx, label in zip(candidate.get_optimize_indices(), labels):
            if label_idx in self.indices:
                diagonal[self.indices.index(label_idx)] = label

        bond_matrix = voronoi_bond_matrix + np.diag(diagonal)
        return bond_matrix

    def _assign_labels(self, adsorbate: Atoms) -> NDArray:
        """Assign adsorption site labels to the adsorbate atoms.

        The adsorption site labels :math:`s_i \in [0, 1)` encode which standard
        adsorption site each adsorbate atom is closest to.

        Parameters
        ----------
        adsorbate : Atoms
            Adsorbate atoms object.

        Returns
        -------
        NDArray
            Adsorption site labels.
        """
        adsorbate_info: Dict = self.template.info.get("adsorbate_info")
        if adsorbate_info is None:
            raise ValueError("Template was not originally created with `ase.build`")

        cell: NDArray = adsorbate_info.get("cell")

        site_positions = np.asarray(list(self.site_mapping.keys()))
        site_types = list(self.site_mapping.values())
        unique_site_types = sorted(set(site_types))

        # convert cell into 3D
        cell = np.array([[cell[0, 0], cell[0, 1], 0.0], [cell[1, 0], cell[1, 1], 0.0], [0.0, 0.0, 1.0]])

        adsorbate = adsorbate.copy()
        adsorbate_positions = adsorbate.get_positions()
        adsorbate_positions[:, 2] = 0.0  # we don't care about the z coordinates

        site_positions = np.hstack((site_positions, np.zeros((site_positions.shape[0], 1))))  # convert into 3D
        site_positions = site_positions @ cell

        _, distances = get_distances(adsorbate_positions, site_positions, cell=cell, pbc=[True, True, False])

        site_indices = np.argmin(distances, axis=1)
        adsorbate_labels = (
            np.asarray([unique_site_types.index(site_types[i]) for i in site_indices], dtype=int) + 1
        ) / (len(unique_site_types) + 1)

        return adsorbate_labels
