from typing import List

import numpy as np
from ase import Atoms

from agox.utils.filters.ABC_filter import FilterBaseClass


class RandomFilter(FilterBaseClass):
    """
    Filter that removes all structures.

    """

    name = "RandomFilter"

    def __init__(self, N, **kwargs):
        """
        Parameters
        ----------
        """
        super().__init__(**kwargs)
        self.N = N

    def _filter(self, atoms: List[Atoms]) -> np.ndarray:
        if len(atoms) < self.N:
            return np.arange(len(atoms))
        else:
            return np.random.choice(np.arange(len(atoms)), self.N, replace=False)
