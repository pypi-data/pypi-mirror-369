import numpy as np
import pytest

from agox.utils.sparsifiers import CUR, MBkmeans, RandomSparsifier


@pytest.mark.parametrize(
    "sparsifier_dict",
    [
        {"sparsifier": RandomSparsifier, "kwargs": {}},
        {"sparsifier": CUR, "kwargs": {}},
        {"sparsifier": MBkmeans, "kwargs": {"exact_points": True}},
    ],
)
def test_sparsifier(sparsifier_dict):
    # Random feautre matix:
    X = np.random.rand(1000, 20)

    # Setup a sparsifier
    sparsifier = sparsifier_dict["sparsifier"](m_points=10, **sparsifier_dict["kwargs"])

    # Sparsify the structures
    Xm, indices = sparsifier.sparsify(X)

    print("Before sparsification: ", X.shape)
    print("After sparsification: ", Xm.shape)

    # Assert that the shapes make sense.
    assert Xm.shape[0] == 10
    assert Xm.shape[1] == 20
    assert len(indices) == 10

    # Assert that using the indices to select rows from X gives the same result as Xm
    assert np.allclose(Xm, X[indices, :])
