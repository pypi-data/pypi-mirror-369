from typing import List, Optional, Union

import numpy as np


class Confinement:
    def __init__(
        self,
        cell: np.ndarray = None,
        corner: np.ndarray = None,
        indices: np.ndarray = None,
        pbc: Optional[Union[bool, List[bool]]] = None,
    ) -> None:
        self.cell = np.array(cell)
        self.corner = np.array(corner)

        if indices is None:
            indices = np.array([])
        self.indices = np.array(indices).flatten()

        self.periodicity_setup(pbc)
        self.confined = self.cell is not None and self.corner is not None

    def periodicity_setup(self, pbc: Optional[Union[bool, List[bool]]]) -> None:
        if pbc is None:
            pbc = False
        if isinstance(pbc, bool):
            self.pbc = [pbc] * 3
        elif len(pbc) == 3:
            self.pbc = list(pbc)
        else:
            print("pbc should be list or bool! Setting pbc=False.")
            self.pbc = [False] * 3

        self.hard_boundaries = [not p for p in self.pbc]

        if np.any(self.pbc):
            periodic_cell_vectors = self.cell[:, self.pbc]
            non_periodic_cell_vectors = self.cell[:, self.hard_boundaries]
            if np.any(np.abs(np.matmul(periodic_cell_vectors.T, non_periodic_cell_vectors)) > 0):
                print("---- BOX CONSTRAINT ----")
                print("Periodicity does not work for non-square non-periodic directions!")
                print("------------------------")

        if np.all(self.cell[:, 2] == 0):
            self.dimensionality = 2
            self.effective_cell = self.cell[0:2, 0:2]
            if np.all(self.cell[:, 1] == 0):
                self.effective_cell = self.cell[0:1, 0:1]
                self.dimensionality = 1
        else:
            self.effective_cell = self.cell
            self.dimensionality = 3

    def get_projection_coefficients(self, positions: np.ndarray) -> np.ndarray:
        positions = positions.reshape(-1, 3)
        return np.linalg.solve(
            self.effective_cell.T, (positions - self.corner)[:, 0 : self.dimensionality].T
        ).T.reshape(-1, self.dimensionality)

    def check_confinement(self, positions: np.ndarray) -> np.ndarray:
        """
        Finds the fractional coordinates of the atomic positions in terms of the box defined by the constraint.
        """
        if self.confined:
            C = self.get_projection_coefficients(positions)
            inside = np.all((C > 0) * (C < 1), axis=1)
            return inside
        else:
            return np.ones(positions.shape[0]).astype(bool)

    def get_confinement_limits(self) -> List[np.ndarray]:
        """
        This returns the confinement-limit lists which always assumes a square box.
        """
        conf = [self.corner, self.cell @ np.array([1, 1, 1]) + self.corner]
        return conf

    def _get_box_vector(self) -> np.ndarray:
        return self.cell.T @ np.random.rand(3) + self.corner

    def set_cell(self, cell: np.ndarray, corner: np.ndarray) -> None:
        self.cell = cell
        self.corner = corner
        self.confined = True
        self.confined = self.cell is not None and self.corner is not None

    def set_dimensionality(self, dimensionality: int) -> None:
        self.dimensionality = dimensionality

    def copy(self) -> "Confinement":
        return Confinement(self.cell, self.corner, self.indices, self.pbc)