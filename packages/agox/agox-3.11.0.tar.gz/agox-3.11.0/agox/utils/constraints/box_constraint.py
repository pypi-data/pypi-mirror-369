from typing import List

import numpy as np
from ase import Atoms
from ase.constraints import IndexedConstraint, slice2enlist
from ase.geometry import wrap_positions
from numpy.typing import NDArray

from agox.helpers.confinement import Confinement


class BoxConstraint(Confinement, IndexedConstraint):
    def __init__(
        self,
        confinement_cell: NDArray = None,
        confinement_corner: NDArray = None,
        indices: NDArray = None,
        pbc: List[bool] = [False] * 3,
        wrap: bool = False,
        **kwargs,
    ):
        """
        Confinement constraint for atoms. This constraint will keep the atoms within a box defined by the cell and corner.

        Parameters
        ----------
        confinement_cell : np.ndarray
            The cell defining the box.
        confinement_corner : np.ndarray
            The corner of the box.
        indices : np.ndarray
            The indices of the atoms that are confined.
        pbc : list[bool]
            The periodic boundary conditions.
        wrap : bool
            If True, the atoms will be wrapped back into the box if they escape in directions
            with PBC.
        """
        IndexedConstraint.__init__(self, indices=indices)
        Confinement.__init__(self, 
            cell=confinement_cell,
            corner=confinement_corner,
            indices=indices,
            pbc=pbc,
        )

        # Soft boundary & force decay.
        self.lower_soft_boundary = 0.05
        self.lower_hard_boundary = 0.001
        self.al, self.bl = np.polyfit([self.lower_soft_boundary, self.lower_hard_boundary], [1, 0], 1)
        self.upper_soft_boundary = 0.95
        self.upper_hard_boundary = 0.999
        self.au, self.bu = np.polyfit([self.upper_soft_boundary, self.upper_hard_boundary], [1, 0], 1)

        self.wrap = wrap

    @property
    def index(self):
        return self.indices

    @index.setter
    def index(self, value):
        self.indices = value

    def linear_boundary(self, x, a, b):
        return a * x + b

    def adjust_positions(self, atoms: Atoms, newpositions: NDArray):
        inside = self.check_confinement(newpositions[self.indices])
        # newpositions[not inside, :] = atoms.positions[not inside]
        # New positions of those atoms that are not inside (so outside) the box are set inside the box.

        if np.invert(inside).any():
            if self.wrap:
                newpositions[self.indices[np.invert(inside)], :] = wrap_positions(
                    newpositions[self.indices[np.invert(inside)], :],
                    cell=self.confinement_cell,
                    pbc=self.pbc,
                )
            for idx in self.indices[np.invert(inside)]:
                newpositions[idx, self.hard_boundaries] = atoms.positions[idx, self.hard_boundaries]

    def adjust_forces(self, atoms: Atoms, forces: NDArray):
        C = self.get_projection_coefficients(atoms.positions[self.indices])
        # Because adjust positions does not allow the atoms to escape the box we know that all atoms are witihn the box.
        # Want to set the forces to zero if atoms are close to the box, this happens if any component of C is close to 0 or 1.
        for coeff, idx in zip(C, self.indices):
            coeff = np.array([0.5 if p else c for c, p in zip(coeff, self.pbc)])
            if ((coeff < 0) * (coeff > 1)).any():
                forces[idx] = 0  # Somehow the atom is outside, so it is just locked.
            if (coeff > self.upper_soft_boundary).any():
                forces[idx, self.hard_boundaries] = (
                    self.linear_boundary(np.max(coeff), self.au, self.bu) * forces[idx, self.hard_boundaries]
                )
            elif (coeff < self.lower_soft_boundary).any():
                forces[idx, self.hard_boundaries] = (
                    self.linear_boundary(np.min(coeff), self.al, self.bl) * forces[idx, self.hard_boundaries]
                )

    def adjust_momenta(self, atoms: Atoms, momenta: NDArray):
        self.adjust_forces(atoms, momenta)

    def get_removed_dof(self, atoms: Atoms):
        return 0

    def index_shuffle(self, atoms: Atoms, ind: NDArray):
        # See docstring of superclass
        index = []

        # Resolve negative indices:
        actual_indices = set(np.arange(len(atoms))[self.index])

        for new, old in slice2enlist(ind, len(atoms)):
            if old in actual_indices:
                index.append(new)
        if len(index) == 0:
            raise IndexError("All indices in FixAtoms not part of slice")
        self.index = np.asarray(index, int)

    def get_indices(self):
        return self.index.copy()
    
    def __repr__(self) -> str:
        return f'BoxConstraint(indices={self.indices}, pbc={self.pbc}, wrap={self.wrap})'

    def todict(self):
        return {
            "name": "BoxConstraint",
            "kwargs": {
                "confinement_cell": self.cell.tolist(),
                "confinement_corner": self.corner.tolist(),
                "indices": self.indices.tolist(),
            },
        }


# To work with ASE read/write we need to do some jank shit.
from ase import constraints

constraints.__all__.append("BoxConstraint")
constraints.BoxConstraint = BoxConstraint