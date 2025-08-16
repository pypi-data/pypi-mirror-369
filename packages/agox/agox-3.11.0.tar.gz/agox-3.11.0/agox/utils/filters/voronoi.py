from typing import List

import numpy as np
from ase import Atoms

from agox.models.descriptors.voronoi import Voronoi
from agox.utils.filters.ABC_filter import FilterBaseClass


class VoronoiFilter(FilterBaseClass):
    """
    Filther that removes structures if their graph has produced
    a given number of children.

    """

    name = "VoronoiGraphFilter"

    def __init__(self, max_number_of_children=5, descriptor=None, **kwargs):
        """
        Parameters
        ----------
        max_number_of_children: int
            Maximum number of children.
        voronoi: VoronoiSampler
            VoronoiSampler object to calculate graphs.
        remove_tree: bool
            If True, the tree will be removed.
        """

        super().__init__(**kwargs)
        self.max_number_of_children = max_number_of_children

        if descriptor is None:
            self.descriptor = Voronoi(covalent_bond_scale_factor=1.3, n_points=8, angle_from_central_atom=20)
        else:
            self.descriptor = descriptor

        # Tree stuff
        self.number_of_structures_in_last_iteration = 0
        self.number_of_children = {}
        self.graph_to_uuid = {}
        self.uuid_to_graph = {}

        self.uuids_to_remove = []
        self.removed_graphs = []

    def _filter(self, atoms: List[Atoms]) -> np.ndarray:
        """
        Filter the atoms object.

        Parameters
        ----------
        atoms
            The atoms object to be filtered.

        Returns
        -------
        indexes: array-like
            The indexes of the atoms that are kept.
        """

        if self.descriptor.template is None:
            self.descriptor.template = atoms[0].template

        graphs_to_remove = []
        new_uuids = []

        for i, structure in enumerate(atoms[self.number_of_structures_in_last_iteration :]):
            my_uuid = structure.get_meta_information("uuid")
            new_uuids.append(my_uuid)

            if structure.get_meta_information("final") is not True:
                continue

            my_graph = self.descriptor.create_features(structure, False)

            for uuid in new_uuids:
                self.uuid_to_graph[uuid] = my_graph

            self.graph_to_uuid[my_graph] = self.graph_to_uuid.get(my_graph, []) + new_uuids

            if my_graph in self.removed_graphs:
                self.uuids_to_remove += new_uuids

                if structure.has_meta_information("parent_uuids"):
                    parent_uuids = structure.get_meta_information("parent_uuids")
                    for parent_uuid in parent_uuids:
                        parent_graph = self.uuid_to_graph[parent_uuid]
                        graphs_to_remove.append(parent_graph)
                        if parent_graph not in self.removed_graphs:
                            self.removed_graphs.append(parent_graph)
                        self.uuids_to_remove.append(parent_uuid)

            if structure.has_meta_information("parent_uuids"):
                parent_uuids = structure.get_meta_information("parent_uuids")
                parent_search_iterations = structure.get_meta_information("parent_search_iterations")
                for parent_uuid, parent_search_iteration in zip(parent_uuids, parent_search_iterations):
                    parent_graph = self.uuid_to_graph[parent_uuid]

                    self.number_of_children[parent_graph] = self.number_of_children.get(parent_graph, 0) + 1

                    if self.number_of_children[parent_graph] >= self.max_number_of_children:
                        graphs_to_remove += [parent_graph]

            new_uuids = []

        for g in graphs_to_remove:
            if g not in self.removed_graphs:
                self.removed_graphs.append(g)
            self.uuids_to_remove += self.graph_to_uuid[g]

        self.uuids_to_remove = list(set(self.uuids_to_remove))

        indexes = [i for i in range(len(atoms)) if atoms[i].get_meta_information("uuid") not in self.uuids_to_remove]

        self.number_of_structures_in_last_iteration = len(atoms)
        return np.array(indexes)
