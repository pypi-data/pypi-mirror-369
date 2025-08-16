from typing import List

import numpy as np
from ase import Atoms

from agox.utils.filters.ABC_filter import FilterBaseClass


class NoneFilter(FilterBaseClass):
    """
    Filter that removes all structures.

    """

    name = "NoneFilter"

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        """
        super().__init__(**kwargs)

    def _filter(self, atoms: List[Atoms]) -> np.ndarray:
        return np.array([])
