from collections import OrderedDict
from typing import Dict

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import rich_click as click
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from rich import print

from agox.analysis.search_analysis import SearchAnalysis


class EventHandler:
    def __init__(self, search_analysis: SearchAnalysis, axis_dict: Dict[str, Axes], fig: Figure) -> None:
        self.search_analysis = search_analysis
        self.axis_dict = axis_dict
        self.fig = fig

        self.total_images = search_analysis.get_number_of_best_candidates()
        self.image = 0
        self.plane = "xy"
        self.timer = self.fig.canvas.new_timer(interval=100)
        self.timer.add_callback(self.image_update_arrow_key)


    def on_press(self, event: matplotlib.backend_bases.KeyEvent) -> None:
        if event.key == "z":
            self.plane = "xy"
        elif event.key == "x":
            self.plane = "yz"
        elif event.key == "y":
            self.plane = "xz"
        elif event.key == "right":
            self.image += 1
        elif event.key == "left":
            self.image -= 1

        self.image = self.image % self.total_images

        if event.key in ["right", "left", "shift+right", "shift+left"]:
            if "right" in event.key:
                self.direction = 1
            else:
                self.direction = -1
            if "shift" in event.key:
                self.timer.start()
        else:
            self.image_update()

    def on_release(self, event: matplotlib.backend_bases.KeyEvent) -> None:
        if event.key in ["shift+right", "shift+left"]:
            self.timer.stop()
        self.image_update()

    def image_update_arrow_key(self) -> None:
        self.image += self.direction
        self.image = self.image % self.total_images
        self.image_update()

    def image_update(self) -> None:
        self.axis_dict["configuration"].clear()
        self.search_analysis.plot_configuration(ax=self.axis_dict["configuration"], image=self.image, plane=self.plane, 
                                                name= f"Candidate {self.image + 1}/{self.total_images}")

        if "distribution" in self.axis_dict:
            self.search_analysis.update_hist_line(image=self.image)

        self.fig.canvas.draw()


option_groups = {"agox analysis": []}
option_groups["agox analysis"].append({"name": "File options", "options": ["--reload"]})
option_groups["agox analysis"].append(
    {
        "name": "Plot options",
        "options": [
            "--backend",
            "--success",
            "--configuration",
            "--energy",
            "--distribution",
        ],
    }
)
option_groups["agox analysis"].append(
    {
        "name": "Analysis options",
        "options": ["--delta-total", "--delta-atom", "--property-name", "--thermodynamics-file", "--criterion"],
    }
)
click.rich_click.OPTION_GROUPS.update(option_groups)


@click.command("analysis")  # fmt: skip
@click.argument("directories", nargs=-1, type=click.Path(exists=True))  # fmt: skip
@click.option("--reload", "-r", is_flag=True, help="Reload the searches", default=False, show_default=True)  # fmt: skip
@click.option("--backend", "-b", type=str, help="Matplotlib backend", default="TkAgg", show_default=True)  # fmt: skip
@click.option("--success", "-s",help="Plot CDF (success curve).", is_flag=True, default=True, show_default=True, type=bool)  # fmt: skip
@click.option("--configuration", "-c", help="Plot the structures.", is_flag=True, default=True, show_default=True, type=bool)  # fmt: skip
@click.option("--energy", "-e", help="Plot the energies.", is_flag=True, default=True, show_default=True, type=bool)  # fmt: skip
@click.option("--distribution", "-d",help="Plot the distribution.", is_flag=True, default=False, show_default=True, type=bool)  # fmt: skip
@click.option("--delta-total", "-dE", help="Threshold for success in eV. Used if criteria is 'energy'.", type=float, default=1.0, show_default=True)  # fmt: skip
@click.option("--delta-atom", "-de", help="Threshold for success in eV/atom, overwrites delta-total if given", type=float, default=np.nan, show_default=True)  # fmt: skip
@click.option("--property-name", "-p", type=click.Choice(["Energy", "FreeEnergy"], case_sensitive=False), default="Energy", show_default=True, help="Property to consider")  # fmt: skip
@click.option("--criterion", "-C", type=click.Choice(["energy", "graph"], case_sensitive=False), default="energy", show_default=True, help="Criterion used to calculate success curve.")  # fmt: skip
@click.option("--thermodynamics-file", "-t", type=click.Path(exists=True), help="The thermodynamics json file that specifies references and chemical potentials to use for free energy", default=None)  # fmt: skip
@click.option("--window", "-w", type=int, help="Window for rolling average", default=5, show_default=True)  # fmt: skip
@click.option("--iteration-time", "-it", is_flag=True, help="Plot as the time axis being iterations", default=False, show_default=True)  # fmt: skip
@click.option("--time-time", '-tt', is_flag=True, help="Plot as the time axis being time", default=False, show_default=True)  # fmt: skip
@click.option('--time-unit', '-tu', type=click.Choice(['s', 'm', 'h', 'd', 'y'], case_sensitive=False), default='s', show_default=True, help='Time axis unit')  # fmt: skip
@click.option('--n_cores', '-nc', type=int, default=1, show_default=True, help='Number of cores to account for')  # fmt: skip
def cli_analysis(
    directories: str,
    reload: bool,
    backend: str,
    success: bool,
    configuration: bool,
    energy: bool,
    distribution: bool,
    delta_total: float,
    delta_atom: float,
    property_name: str,
    criterion: str,
    thermodynamics_file: str,
    window: int,
    iteration_time: bool,
    time_time: bool,
    time_unit: str,
    n_cores: int,
) -> None:
    """
    Perform basic analysis of searches.
    """
    from timeit import default_timer as dt

    from agox.analysis import DistanceCriterion, SearchCollection, ThresholdCriterion
    from agox.analysis.property import DescriptorProperty, EnergyProperty, FreeEnergyProperty
    from agox.analysis.search_analysis import SearchAnalysis
    from agox.models.descriptors import SpectralGraphDescriptor

    t0 = dt()
    matplotlib.use(backend)

    # Setup the search collection
    search_collection = SearchCollection(directories, reload=reload, progress_bar=True)
    print("Time taken to load: ", dt() - t0)

    for search in search_collection:
        print(search)

    # Check if we have anything to plot:
    plot_labels = ["configuration", "success", "energy", "distribution"]
    plot_bools = [configuration, success, energy, distribution]
    plotting_dict = OrderedDict()
    for label, plot_bool in zip(plot_labels, plot_bools):
        if plot_bool:
            plotting_dict[label] = plot_bool

    if len(plotting_dict) == 0:
        print("Nothing to plot.")
        return

    # Setup the figure:
    n_plots = len(plotting_dict)
    fig, axes = plt.subplots(1, n_plots, figsize=(4 * n_plots, 4), layout="constrained")
    axes = np.atleast_1d(axes)
    axes_dict = {}

    for ax, (label, plot_bool) in zip(axes, plotting_dict.items()):
        if plot_bool:
            axes_dict[label] = ax

    # Property:
    if iteration_time:
        time_axis = 'iterations'
    elif time_time:
        time_axis = 'time'
    else:
        time_axis = 'indices'

    if thermodynamics_file is not None:
        property_name = "FreeEnergy"  # If thermodynamics file is given, we assume we want to plot free energy.

    if property_name == "Energy":
        energy_property = EnergyProperty(time_axis=time_axis, time_unit=time_unit, cost_factor=n_cores)
        delta = delta_total if np.isnan(delta_atom) else delta_atom * len(search_collection[0].get_candidate(0, 0))
    elif property_name == "FreeEnergy":
        from agox.utils.thermodynamics import ThermodynamicsData
        thermo_data = ThermodynamicsData.load(thermodynamics_file)
        energy_property = FreeEnergyProperty(thermo_data=thermo_data, time_axis=time_axis)
        delta = delta_total

    search_analysis = SearchAnalysis(search_collection, energy_property)

    if configuration:
        search_analysis.plot_configuration(ax=axes_dict["configuration"], image=0)

    if energy:
        search_analysis.plot_energy(ax=axes_dict["energy"], window=window)

    if success:
        if criterion == "energy":
            _, _, min_props = search_analysis.get_flat_candidates()
            e_min = np.nanmin(min_props)
            criterion = ThresholdCriterion(e_min + delta)
            search_property = energy_property
        elif criterion == "graph":
            best_candidate = search_analysis.get_flat_candidates()[0][0]
            descriptor = SpectralGraphDescriptor.from_atoms(best_candidate)
            comparate = descriptor.get_features(best_candidate)
            search_property = DescriptorProperty(descriptor)
            criterion = DistanceCriterion(threshold=1e-7, comparate=comparate)  # Graphs should match.

        search_analysis.plot_cdf(ax=axes_dict["success"], criterion=criterion, search_property=search_property)

    if distribution:
        search_analysis.plot_histogram(ax=axes_dict["distribution"], bin_size=delta, image=0)

    # Setup the event handler:
    event_handler = EventHandler(search_analysis, axes_dict, fig)
    fig.canvas.mpl_connect("key_press_event", event_handler.on_press)
    fig.canvas.mpl_connect("key_release_event", event_handler.on_release)

    plt.show()
