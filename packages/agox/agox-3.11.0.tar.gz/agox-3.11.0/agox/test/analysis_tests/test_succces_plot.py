from pathlib import Path

import matplotlib.pyplot as plt

from agox.analysis.criterion import ThresholdCriterion
from agox.analysis.plot.success_plot import SuccessPlotter
from agox.analysis.property import EnergyProperty
from agox.analysis.search_data import SearchCollection
from agox.test.test_utils import TemporaryFolder


def test_propert_plotter(tmpdir: Path, search_collection: SearchCollection, energy_property: EnergyProperty) -> None:
    plt.switch_backend("agg")

    with TemporaryFolder(tmpdir):
        criterion = ThresholdCriterion(0.5)
        plotter = SuccessPlotter(search_collection, energy_property, criterion)
        fig, ax = plt.subplots()
        plotter.plot(ax)

        plt.savefig("test.png")
