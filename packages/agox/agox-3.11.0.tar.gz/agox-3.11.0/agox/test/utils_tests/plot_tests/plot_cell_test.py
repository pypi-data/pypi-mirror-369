from typing import List

import matplotlib
import matplotlib.pyplot as plt
import pytest
from ase.cell import Cell
from matplotlib.collections import PolyCollection
from matplotlib.path import Path

from agox.utils.plot.plot_cell import plot_cell


@pytest.mark.parametrize("plane", ["xy", "xz", "yz"])
def test_plot_cell(environment_and_dataset, plane):
    matplotlib.use("Agg")

    _, dataset = environment_and_dataset
    cell: Cell = dataset[0].cell

    fig, ax = plt.subplots()
    plot_cell(ax, cell, plane=plane)

    assert len(ax.collections) == 1
    assert isinstance(ax.collections[0], PolyCollection)
    p: PolyCollection = ax.collections[0]

    paths: List[Path] = p.get_paths()
    assert len(paths) == 6

    plt.close(fig)
