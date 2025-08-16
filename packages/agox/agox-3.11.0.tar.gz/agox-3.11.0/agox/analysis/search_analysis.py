from typing import Dict, List, Optional, Union

import numpy as np
from ase import Atoms
from matplotlib.axes import Axes

from agox.analysis.criterion import BaseCriterion
from agox.analysis.plot import PropertyPlotter, SuccessPlotter
from agox.analysis.property import Property
from agox.analysis.search_data import SearchCollection
from agox.candidates import StandardCandidate
from agox.utils.plot import plot_atoms, plot_cell
from agox.utils.plot.plot_atoms import plane_to_indices


def align(atoms: Union[Atoms, StandardCandidate]) -> Atoms:
    from sklearn.decomposition import PCA

    pca = PCA(n_components=3)
    pca.fit(atoms.get_positions())
    atoms.positions = pca.transform(atoms.get_positions())
    atoms.center()
    return atoms


class SearchAnalysis:
    def __init__(
        self, search_collection: Optional[SearchCollection] = None, analysis_property: Optional[Property] = None
    ) -> None:
        """
        Helper class for analyzing search results. Mainly used in the CLI.
        Functionality should be placed in different modules, this just collects
        them and joins them together for the CLI.

        Parameters:
        -----------
        search_collection: SearchCollection
            The search collection to analyze.
        analysis_property: Property
            The property to analyze.
        """

        self.search_collection = search_collection
        self.analysis_property = analysis_property

    def get_property(self, recalculate: bool = False) -> List:
        if not hasattr(self, "properties") or recalculate:
            properties = []
            for search in self.search_collection:
                # Gather the properties for all searches:
                properties.append(self.analysis_property(search))
            self.properties = properties

        return self.properties

    def get_identifiers(self, recalculate: bool = False) -> Dict:
        if not hasattr(self, "identifiers") or recalculate:
            identifiers = {}
            for search in self.search_collection:
                restart_identifiers = search.get_all_identifiers()
                search_label = search.get_label()
                search_labels = [f"{search_label}/{identifier}" for identifier in restart_identifiers]
                identifiers[search.get_uuid()] = search_labels

            self.identifiers = identifiers
        return self.identifiers

    def get_best_indices(self, recalculate: bool = False) -> Dict[str, int]:
        if not hasattr(self, "best_indices") or recalculate:
            properties = self.get_property(recalculate=recalculate)
            property_values = [prop.data for prop in properties]
            best_indices = {search.get_uuid(): [] for search in self.search_collection}
            for prop_array, search in zip(property_values, self.search_collection):
                for restart in range(search.get_number_of_restarts()):
                    min_index = np.nanargmin(prop_array[restart])
                    best_indices[search.get_uuid()].append(min_index)
            self.best_indices = best_indices
        return self.best_indices

    def get_best_property(self, recalculate: bool = False) -> Dict:
        indices = self.get_best_indices(recalculate=recalculate)
        properties = self.get_property(recalculate=recalculate)
        property_arrays = [prop.data for prop in properties]

        best_properties = {search.get_uuid(): [] for search in self.search_collection}
        for prop_array, search in zip(property_arrays, self.search_collection):
            for restart, min_index in enumerate(indices[search.get_uuid()]):
                best_properties[search.get_uuid()].append(prop_array[restart][min_index])
        return best_properties

    def get_candidates(self, recalculate: bool = False) -> Dict:
        if not hasattr(self, "candidates") or recalculate:
            candidates = []
            for search in self.search_collection:
                for restart, index in self.get_best_indices()[search.get_uuid()]:
                    candidates.append(search.get_candidate(restart, index))
            self.candidates = candidates
        return self.candidates

    def get_best_candidates(self, recalculate: bool = False) -> Dict:
        if not hasattr(self, "best_candidates") or recalculate:
            best_candidates = {search.get_uuid(): [] for search in self.search_collection}
            indices = self.get_best_indices()
            for search in self.search_collection:
                for restart, index in enumerate(indices[search.get_uuid()]):
                    best_candidates[search.get_uuid()].append(search.get_candidate(restart, index))
            self.best_candidates = best_candidates

        return self.best_candidates

    def get_number_of_best_candidates(self) -> int:
        return sum([len(candidates) for candidates in self.get_best_candidates().values()])

    def get_flat_candidates(self, recalculate: bool = False) -> List:
        if not hasattr(self, "flat_candidates") or recalculate:
            identifiers = self.get_identifiers()
            properties = self.get_best_property()
            candidates = self.get_best_candidates()

            flat_properties = []
            flat_identifiers = []
            flat_candidates = []

            for label, prop in properties.items():
                flat_properties.extend(prop)
                flat_identifiers.extend(identifiers[label])
                flat_candidates.extend(candidates[label])

            indices = np.argsort(flat_properties)
            flat_properties = [flat_properties[i] for i in indices]
            flat_identifiers = [flat_identifiers[i] for i in indices]
            flat_candidates = [flat_candidates[i] for i in indices]

            self.flat_candidates = flat_candidates
            self.flat_identifiers = flat_identifiers
            self.flat_properties = flat_properties
        return self.flat_candidates, self.flat_identifiers, self.flat_properties

    def plot_configuration(
        self,
        ax: Axes,
        candidate: Union[Atoms, StandardCandidate] = None,
        image: Optional[int] = None,
        plane: str = "xy",
        name: Optional[str] = None,
    ) -> None:
        """
        Plot the candidates of the search.

        Parameters:
        -----------
        ax: Axes
            The axis to plot on.
        candidate: Atoms
            The candidate to plot.
        image: int
            The index of the candidate to plot.
        plane: str
            The plane to plot.
        """

        name = name or ""

        if candidate is None:
            flat_candidates, flat_identifiers, flat_properties = self.get_flat_candidates()
            candidate = flat_candidates[image]
            if not candidate.pbc.any():
                candidate = align(candidate)
            name = f"{name} {flat_identifiers[image]}"
            energy = flat_properties[image]
        else:
            energy = candidate.get_potential_energy()

        plot_atoms(ax, candidate, repeat=int(candidate.pbc.any()), plane=plane)
        plot_cell(ax, candidate.get_cell(), plane=plane)
        ax.set_title(f"{name} \n Energy: {energy:.2f} eV")

        # Plot coordinate system:
        ax.arrow(0.1, 0.1, 0.1, 0, transform=ax.transAxes, color='black', linewidth=1.5, head_width=0.01, head_length=0.01)
        ax.arrow(0.1, 0.1, 0.0, 0.1, transform=ax.transAxes, color='black', linewidth=1.5, head_width=0.01, head_length=0.01)
        a, b, c, d = plane_to_indices(plane)
        indices_to_text = {0: 'x', 1: 'y', 2: 'z'}
        ax.text(0.22, 0.1, indices_to_text[a], transform=ax.transAxes, color='black', fontsize=10, verticalalignment='center', horizontalalignment='left')
        ax.text(0.1, 0.22, indices_to_text[b], transform=ax.transAxes, color='black', fontsize=10, verticalalignment='bottom', horizontalalignment='center')


    def plot_energy(self, ax: Axes, window=5) -> None:
        """
        Plot the energy versus time.
        """
        # This recalculates - so thats annoying atm.
        property_time = PropertyPlotter(self.search_collection, self.analysis_property, window=window)
        property_time.plot(ax)

    def plot_cdf(self, ax: Axes, criterion: BaseCriterion, search_property: Optional[Property] = None) -> None:
        """
        Plot the CDF of the energy.
        """
        if search_property is None:
            search_property = self.analysis_property

        plotter = SuccessPlotter(self.search_collection, search_property, criterion)
        plotter.plot(ax)

    def plot_histogram(self, ax: Axes, bin_size: float, image: int = 0) -> None:
        best_properties = self.get_best_property()

        _, _, flat_best_properties = self.get_flat_candidates()
        bins = np.arange(np.min(flat_best_properties), np.max(flat_best_properties) + bin_size, bin_size)

        for label, values in best_properties.items():
            ax.hist(values, label=label, bins=bins, alpha=0.5, edgecolor="black")

        self.hist_line = ax.axvline(flat_best_properties[image], label="_no_legend_", color="black")

        ax.legend()
        ax.set_title("Histogram of energies")

    def update_hist_line(self, image: int = 0) -> None:
        line = self.hist_line
        _, _, flat_best_properties = self.get_flat_candidates()
        line.set_xdata([flat_best_properties[image]])
