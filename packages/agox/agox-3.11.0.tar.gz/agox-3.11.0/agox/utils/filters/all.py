from typing import List

import numpy as np
from ase import Atoms

from agox.utils.filters.ABC_filter import FilterBaseClass


class AllFilter(FilterBaseClass):
    """
    Filter that removes no structures.

    """

    name = "AllFilter"

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        """
        super().__init__(**kwargs)

    def _filter(self, atoms: List[Atoms]) -> np.ndarray:
        return np.arange(len(atoms), dtype=int)
