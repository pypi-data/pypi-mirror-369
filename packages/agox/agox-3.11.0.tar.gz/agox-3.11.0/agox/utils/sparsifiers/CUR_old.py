import numpy as np
from scipy.linalg import svd

from agox.utils.sparsifiers.ABC_sparsifier import SparsifierBaseClass


class OldCUR(SparsifierBaseClass):
    name = "OldCUR"

    def __init__(self, m_points: int = 1000, **kwargs) -> None:
        super().__init__(m_points, **kwargs)
        DeprecationWarning(
            "This is an older incorrect implementation of CUR, only kept for comparison purposes. Use CUR instead."
        )

    def sparsify(self, X: np.ndarray) -> np.ndarray:
        if X.shape[0] < self.m_points:
            m_indices = np.arange(0, X.shape[0])
            return X, m_indices

        U, _, _ = svd(X)
        score = np.sum(U[:, : self.m_points] ** 2, axis=1) / self.m_points
        sorter = np.argsort(score)[::-1]
        Xm = X[sorter, :][: self.m_points, :]

        return Xm, sorter[: self.m_points]
