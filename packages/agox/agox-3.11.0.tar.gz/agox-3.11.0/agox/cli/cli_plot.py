from pathlib import Path
from typing import Dict, List, Union

import matplotlib
import matplotlib.backend_bases
import matplotlib.pyplot as plt
import rich_click as click
from ase import Atoms
from ase.io import read
from ase.visualize import view
from matplotlib.axes import Axes
from matplotlib.figure import Figure
from rich import print

from agox.analysis.search_analysis import SearchAnalysis


class EventHandler:
    def __init__(
        self,
        search_analysis: SearchAnalysis,
        axis_dict: Dict[str, Axes],
        figure: Figure,
        configurations: List[Atoms],
        energy_plot: "EnergyPlot" = None,
    ) -> None:
        self.search_analysis = search_analysis
        self.axis_dict = axis_dict
        self.fig = figure

        self.energy_plot = energy_plot

        self.image = 0
        self.total_images = len(configurations)
        self.configurations = configurations
        self.plane = "xy"
        self.timer = self.fig.canvas.new_timer(interval=50)
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

        if event.key in ["right", "left"]:
            if event.key == "right":
                self.direction = 1
            else:
                self.direction = -1
            self.timer.start()

    def on_release(self, event: matplotlib.backend_bases.KeyEvent) -> None:
        if event.key in ["right", "left"]:
            self.timer.stop()
        self.image_update()

    def image_update_arrow_key(self) -> None:
        self.image += self.direction
        self.image = self.image % self.total_images
        self.image_update()

    def image_update(self) -> None:
        self.axis_dict["configuration"].clear()
        self.search_analysis.plot_configuration(
            ax=self.axis_dict["configuration"],
            candidate=self.configurations[self.image],
            plane=self.plane,
            name=self.image,
        )

        if self.energy_plot is not None:
            self.energy_plot.update(self.image)

        self.fig.canvas.draw()


class EnergyPlot:
    def __init__(self, energies: List[float], ax: Axes) -> None:
        self.energies = energies
        self.ax = ax
        self.set_pretty()

    def update(self, image: int) -> None:
        self.vline.set_xdata([image, image])
        ymax = self.vline.get_ydata()[1]
        self.vline.set_ydata([self.energies[image], ymax])

    def plot(self) -> None:
        self.ax.plot(self.energies)

        ylims = self.ax.get_ylim()
        self.vline = self.ax.plot([0, 0], [self.energies[0], ylims[1]], "r--")[0]
        self.ax.set_ylim(ylims)

    def set_pretty(self) -> None:
        self.ax.set_xlabel("Image")
        self.ax.set_ylabel("Energy [eV]")
        self.ax.set_title("Energy plot")


@click.command(name="plot")
@click.argument("file", nargs=1, type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file", default=None)
@click.option("--backend", "-b", type=str, help="Matplotlib backend.", default="TkAgg")
@click.option("--ase", "-a", is_flag=True, help="Use ASE to plot the structures.", default=False)
def cli_plot(file: str, output: Union[str, None], backend: str, ase: bool) -> None:
    """
    Plot structures from database or trajectory files.
    """
    from agox.analysis.search_analysis import SearchAnalysis
    from agox.databases.database_utilities import convert_database_to_traj

    matplotlib.use(backend)

    # Read the file:
    file = Path(file)
    if file.suffix == ".db":
        configurations = convert_database_to_traj(file)
    elif file.suffix == ".traj":
        configurations = read(file, ":")
    else:
        print("File type not")

    # # Create figure:
    if not ase:
        fig, axes = plt.subplots(1, 2, figsize=(10, 5))
        search_analysis = SearchAnalysis()
        search_analysis.plot_configuration(axes[0], candidate=configurations[0])

        energies = [config.get_potential_energy() for config in configurations]
        energy_plot = EnergyPlot(energies, axes[1])
        energy_plot.plot()

        # Create event handler:
        event_handler = EventHandler(search_analysis, {"configuration": axes[0]}, fig, configurations, energy_plot)
        fig.canvas.mpl_connect("key_press_event", event_handler.on_press)
        fig.canvas.mpl_connect("key_release_event", event_handler.on_release)

        if output is not None:
            plt.savefig(output)

        plt.show()
    else:
        view(configurations)
