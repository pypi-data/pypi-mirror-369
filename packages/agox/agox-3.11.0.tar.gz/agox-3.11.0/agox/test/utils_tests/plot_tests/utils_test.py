import pytest

from agox.utils.plot.utils import plane_to_indices


@pytest.mark.parametrize(
    "plane,expected",
    [
        ("xy", (0, 1, 2, 1)),
        ("xy+", (0, 1, 2, 1)),
        ("xy-", (0, 1, 2, -1)),
        ("xz", (0, 2, 1, -1)),
        ("xz-", (0, 2, 1, 1)),
        ("yz+", (1, 2, 0, 1)),
        ("yx", (1, 0, 2, -1)),
    ],
)
def test_plane_to_indices(plane, expected):
    indices = plane_to_indices(plane)
    assert indices == expected


@pytest.mark.parametrize("plane", [None, "", "ab", "abc", "xx", "xyz"])
def test_invalid_plane_to_indices(plane):
    with pytest.raises(ValueError, match="Invalid plane specification"):
        plane_to_indices(plane)
