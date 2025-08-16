import numpy as np
from scipy.linalg import svd

from agox.utils.sparsifiers.ABC_sparsifier import SparsifierBaseClass


class CUR(SparsifierBaseClass):
    name = "CUR"

    def sparsify(self, X: np.ndarray) -> np.ndarray:
        if X.shape[0] < self.m_points:
            m_indices = np.arange(0, X.shape[0])
            return X, m_indices

        U, _, _ = svd(X)

        fd = np.min(X.shape)
        score = np.sum(U[:, :fd] ** 2, axis=1) / fd

        # Pick probabilisticly according to the score
        indices = np.random.choice(np.arange(0, X.shape[0]), self.m_points, p=score, replace=False)
        Xm = X[indices, :]

        return Xm, indices
