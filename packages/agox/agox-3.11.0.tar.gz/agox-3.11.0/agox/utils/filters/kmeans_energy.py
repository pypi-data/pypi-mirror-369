from typing import List

import numpy as np
from ase import Atoms

from agox.utils.filters.ABC_filter import FilterBaseClass


class KMeansEnergyFilter(FilterBaseClass):
    name = "KMeansEnergyFilter"

    """
    Filter that removes all structures with energy above a certain threshold.
    
    Parameters
    ----------
    sample_size: int
        Number of structures to sample.
    max_energy: float
        Maximum energy above minimum energy.
    """

    def __init__(self, sample_size: int = 10, max_energy: float = 5, **kwargs):
        super().__init__(**kwargs)
        self.sample_size = sample_size
        self.max_energy = max_energy

    def _filter(self, atoms: List[Atoms]) -> np.ndarray:
        """
        Filter out structures with energies higher than e_min + max_energy

        Parameters
        ----------
        all_structures : list of ase.Atoms or agox.candidates.candidate.Candidate

        Returns
        -------
        indices: np.ndarray
            Array of indices for structures to keep.
        """
        # Get energies of all structures:
        e_all = np.array([s.get_potential_energy() for s in atoms])
        e_min = min(e_all)

        for i in range(5):
            filt = e_all <= e_min + self.max_energy * 2**i
            if np.sum(filt) >= 2 * self.sample_size:
                break
        else:
            filt = np.ones(len(e_all), dtype=bool)
            index_sort = np.argsort(e_all)
            filt[index_sort[2 * self.sample_size :]] = False

        # The final set of structures to consider:
        indices = np.array([i for i in range(len(atoms)) if filt[i]])

        return indices
