from pathlib import Path

import matplotlib.pyplot as plt

from agox.analysis.plot.property_plot import PropertyPlotter
from agox.analysis.property import EnergyProperty
from agox.analysis.search_data import SearchCollection
from agox.test.test_utils import TemporaryFolder


def test_property_plotter(tmpdir: Path, search_collection: SearchCollection, energy_property: EnergyProperty) -> None:
    plt.switch_backend("agg")

    with TemporaryFolder(tmpdir):
        plotter = PropertyPlotter(search_collection, energy_property)
        fig, ax = plt.subplots()
        plotter.plot(ax)

        plt.savefig("test.png")
