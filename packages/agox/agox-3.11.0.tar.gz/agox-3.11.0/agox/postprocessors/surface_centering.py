from typing import Optional, Tuple, Union

import numpy as np
from ase.atoms import Atoms
from numpy.typing import NDArray

from agox.candidates.standard import StandardCandidate
from agox.postprocessors.ABC_postprocess import PostprocessBaseClass


class SurfaceCenteringPostprocess(PostprocessBaseClass):
    """Centers a candidate object to the middle of the cell, taking into
    account adsorption on top of a periodic surface on the xy plane.

    Parameters
    ----------
    template_size : Union[Tuple[int, int], Tuple[int, int, int], NDArray]
        The size of the template given in units of the minimal unit cell. This
        is equivalent to the `size` parameter provided to surface building
        methods from `ase.build`.
    desired_location : Optional[Union[Tuple[int, int], NDArray]], optional
        The desired location of the searched structure in units of the minimal
        unit cell, by default None. If None, take half of `template_size`
        (rounded down).
    """

    name = "SurfaceCenteringPostprocess"

    def __init__(
        self,
        template_size: Union[Tuple[int, int], Tuple[int, int, int], NDArray],
        desired_location: Optional[Union[Tuple[int, int], NDArray]] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        template_size = np.array(template_size, dtype=int)

        if template_size.shape not in [(2,), (3,)]:
            raise ValueError(f"Invalid shape for template_size; is {template_size.shape}, must be (2,) or (3,).")

        self.template_size = template_size[:2]  # we only care about xy

        if desired_location is not None:
            self.desired_location = np.array(desired_location, dtype=int)
        else:
            self.desired_location = self.template_size // 2

        if self.desired_location.shape != (2,):
            raise ValueError(f"Invalid shape for desired_location; if {self.desired_location.shape}, must be (2,).")

        if np.any((self.desired_location < 0) | (self.desired_location >= self.template_size)):
            raise ValueError(
                f"Invalid desired_location: {list(self.desired_location)}. "
                f"Must be between [0, 0] and {list(self.template_size - 1)}."
            )

    def postprocess(self, candidate: StandardCandidate) -> StandardCandidate:
        """Move the searched structure on the surface if necessary.

        Parameters
        ----------
        candidate : StandardCandidate
            The candidate object containing a surface-supported set of atoms.

        Returns
        -------
        StandardCandidate
            A copy of the candidate, with the searched structure translated to
            the desired position.
        """
        original_candidate = candidate
        candidate = candidate.copy()

        atoms = Atoms(candidate)

        cell_xy = candidate.get_cell()[:2, :2]
        uc_xy = cell_xy / self.template_size[:, np.newaxis]

        optimize_indices = candidate.get_optimize_indices()

        com_xy = atoms[optimize_indices].get_center_of_mass()[:2]
        com_uc = np.linalg.solve(uc_xy.T, com_xy)

        offset_uc = np.floor(com_uc + 0.5) - self.desired_location
        offset_xy = np.dot(offset_uc, uc_xy)

        candidate.positions[optimize_indices, :2] -= offset_xy

        original_candidate.copy_calculator_to(candidate)

        return candidate
