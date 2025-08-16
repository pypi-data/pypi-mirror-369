from typing import Tuple

import numpy as np
from sklearn.gaussian_process.kernels import RBF as sklearn_RBF
from sklearn.gaussian_process.kernels import ConstantKernel as sklearn_ConstantKernel
from sklearn.gaussian_process.kernels import DotProduct as sklearn_DotProduct
from sklearn.gaussian_process.kernels import Product as sklearn_Product
from sklearn.gaussian_process.kernels import Sum as sklearn_Sum
from sklearn.gaussian_process.kernels import WhiteKernel as sklearn_WhiteKernel


class Kernel:
    def __add__(self, b):
        if not isinstance(b, Kernel):
            return Sum(self, Constant(b))
        return Sum(self, b)

    def __radd__(self, b):
        if not isinstance(b, Kernel):
            return Sum(Constant(b), self)
        return Sum(b, self)

    def __mul__(self, b):
        if not isinstance(b, Kernel):
            return Product(self, Constant(b))
        return Product(self, b)

    def __rmul__(self, b):
        if not isinstance(b, Kernel):
            return Product(Constant(b), self)
        return Product(b, self)

    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        dk_dy = np.zeros((X.shape[0], Y.shape[1]))

        Y0 = Y.copy()

        for i in range(Y.shape[1]):
            Yp = Y0.copy()
            Yp[:, i] += 1e-5
            Ym = Y0.copy()
            Ym[:, i] -= 1e-5
            dk_dy[:, i] = ((self(X, Yp) - self(X, Ym)) / (2 * 1e-5)).squeeze()

        return dk_dy


class RBF(Kernel, sklearn_RBF):
    def __init__(
        self,
        length_scale: float = 1.0,
        length_scale_bounds: Tuple[float, float] = (1e-1, 1e3),
    ) -> None:
        sklearn_RBF.__init__(self, length_scale=length_scale, length_scale_bounds=length_scale_bounds)

    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        if np.ndim(Y) == 1:
            Y = Y[np.newaxis, :]

        K = self(X, Y)
        dK_dd = -1 / (2 * self.length_scale**2) * K
        dd_df = -2 * (X - Y)
        dk_df = np.multiply(dK_dd, dd_df)

        return dk_df


class Constant(Kernel, sklearn_ConstantKernel):
    def __init__(
        self,
        constant_value: float = 1.0,
        constant_value_bounds: Tuple[float, float] = (1e-1, 1e5),
    ) -> None:
        sklearn_ConstantKernel.__init__(
            self,
            constant_value=constant_value,
            constant_value_bounds=constant_value_bounds,
        )

    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return 0


class Noise(Kernel, sklearn_WhiteKernel):
    def __init__(
        self,
        noise_level: float = 0.01,
        noise_level_bounds: Tuple[float, float] = (0.01, 0.01),
    ) -> None:
        sklearn_WhiteKernel.__init__(self, noise_level=noise_level, noise_level_bounds=noise_level_bounds)

    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return 0


class Sum(Kernel, sklearn_Sum):
    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return self.k1.get_feature_gradient(X, Y) + self.k2.get_feature_gradient(X, Y)


class Product(Kernel, sklearn_Product):
    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        K1 = self.k1(X, Y)
        K2 = self.k2(X, Y)
        grad_K1 = self.k1.get_feature_gradient(X, Y)
        grad_K2 = self.k2.get_feature_gradient(X, Y)

        return K1 * grad_K2 + grad_K1 * K2


class DotProduct(Kernel, sklearn_DotProduct):
    # def __init__(self, normalize=False, **kwargs):
    #     super().__init__(**kwargs)
    #     self.normalize = normalize

    def __call__(self, X, Y=None, eval_gradient=False):
        return super().__call__(X, Y)

    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return super().get_feature_gradient(X, Y)


from sklearn.gaussian_process.kernels import RationalQuadratic as sklearn_RationalQuadratic


class RationalQuadratic(Kernel, sklearn_RationalQuadratic):
    def get_feature_gradient(self, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
        return super().get_feature_gradient(X, Y)

        # from scipy.spatial.distance import cdist

        # if np.ndim(Y) == 1:
        #     Y = Y[np.newaxis, :]

        # distance_squared = cdist(X, Y, metric='sqeuclidean')

        # A = 1 + distance_squared / (2 * self.alpha * self.length_scale ** 2)

        # derivative = 2 * self.alpha * A ** (-self.alpha - 1) * (Y - X)

        # return derivative
