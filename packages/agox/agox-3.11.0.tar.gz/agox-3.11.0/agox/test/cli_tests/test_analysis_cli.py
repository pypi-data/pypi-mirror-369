from pathlib import Path
from typing import List

import pytest
from click.testing import CliRunner

from agox.cli.main import main


def test_analysis_cli_help() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["analysis", "--help"])
    assert result.exit_code == 0


def test_analysis_cli_basic(database_directories: List[Path]) -> None:
    runner = CliRunner()
    command = ["analysis"]
    for database_directory in database_directories:
        command.append(str(database_directory))

    command.append("--backend")
    command.append("agg")

    result = runner.invoke(main, command)
    assert result.exit_code == 0


@pytest.mark.parametrize("property_name", ["Energy", "energy"])
def test_analysis_cli_energy_property(property_name: str, database_directories: List[Path]) -> None:
    runner = CliRunner()
    command = ["analysis"]
    for database_directory in database_directories:
        command.append(str(database_directory))

    command.append("--backend")
    command.append("agg")

    command.append("--property-name")
    command.append(property_name)

    result = runner.invoke(main, command)
    assert result.exit_code == 0


@pytest.mark.parametrize("flag", ["--success", "--configuration", "--energy", "--distribution"])
def test_analysis_cli_plotting_flags(flag: str, database_directories: List[Path]) -> None:
    runner = CliRunner()
    command = ["analysis"]
    for database_directory in database_directories:
        command.append(str(database_directory))

    command.append("--backend")
    command.append("agg")
    command.append(flag)

    result = runner.invoke(main, command)
    assert result.exit_code == 0


def test_analysis_cli_graph_criteria(database_directories: List[Path]) -> None:
    runner = CliRunner()
    command = ["analysis"]
    for database_directory in database_directories:
        command.append(str(database_directory))

    command.append("--backend")
    command.append("agg")

    command.append("--criterion")
    command.append("graph")

    result = runner.invoke(main, command)
    assert result.exit_code == 0


def test_analysis_cli_eventhandler(mocker, search_collection) -> None:  # noqa
    import matplotlib.pyplot as plt
    import numpy as np

    from agox.analysis.criterion import ThresholdCriterion
    from agox.analysis.property import EnergyProperty
    from agox.analysis.search_analysis import SearchAnalysis
    from agox.cli.cli_analysis import EventHandler

    plt.switch_backend("agg")

    plotting_dict = {
        "configuration": True,
        "energy": True,
        "success": True,
        "distribution": True,
    }

    n_plots = 4
    fig, axes = plt.subplots(1, n_plots, figsize=(5 * n_plots, 5))
    axes = np.atleast_1d(axes)
    axes_dict = {}

    for ax, (label, plot_bool) in zip(axes, plotting_dict.items()):
        if plot_bool:
            axes_dict[label] = ax

    energy_property = EnergyProperty()
    search_analysis = SearchAnalysis(search_collection, energy_property)

    search_analysis.plot_configuration(ax=axes_dict["configuration"], image=0)
    search_analysis.plot_energy(ax=axes_dict["energy"])
    search_analysis.plot_cdf(ax=axes_dict["success"], criterion=ThresholdCriterion(0.1))
    search_analysis.plot_histogram(ax=axes_dict["distribution"], bin_size=0.1, image=0)

    event_handler = EventHandler(search_analysis, axes_dict, fig)

    for key in ["right", "left", "x", "y", "z"]:
        event = mocker.MagicMock()
        event.key = key
        event_handler.on_press(event)
