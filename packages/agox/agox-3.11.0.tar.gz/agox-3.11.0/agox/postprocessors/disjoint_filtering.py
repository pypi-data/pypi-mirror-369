from typing import Any, Dict, List, Optional

import numpy as np

from agox.candidates.standard import StandardCandidate
from agox.models.descriptors.spectral_graph_descriptor import SpectralGraphDescriptor
from agox.postprocessors.ABC_postprocess import PostprocessBaseClass


class DisjointFilteringPostprocess(PostprocessBaseClass):
    """
    Filters away disjont structures.

    Filter structures that are disjoint (i.e., have atoms in two or more
    separate groups, as determined by an adjacency graph). Internally, this
    postprocessor uses the `SpectralGraphDescriptor` class to evaluate
    eigenvalues of the Laplacian matrix.

    Parameters
    ----------
    graph_kwargs : Optional[Dict[str, Any]], optional
        Custom keyword arguments to pass to the `SpectralGraphDescriptor`
        class, by default None.
    """

    name = "DisjointFilteringPostprocess"

    def __init__(self, graph_kwargs: Optional[Dict[str, Any]] = None, **kwargs):
        super().__init__(**kwargs)
        if graph_kwargs is None:
            graph_kwargs = {}

        self.descriptor = SpectralGraphDescriptor(
            environment=None, mode="laplacian", diagonal_mode="zero", **graph_kwargs
        )

    def process_list(self, list_of_candidates: List[StandardCandidate]) -> List[Optional[StandardCandidate]]:
        """Process a list of candidates.

        Parameters
        ----------
        list_of_candidates : List[StandardCandidate]
            List of candidates.

        Returns
        -------
        List[Optional[StandardCandidate]]
            List of candidates, with disjoint candidates replaced by `None`.
        """
        processed_candidates = [self.postprocess(candidate) for candidate in list_of_candidates]

        filtered_count = processed_candidates.count(None)
        s = "s" if filtered_count != 1 else ""
        self.writer(f"Filtered {filtered_count} disjoint candidate{s}")

        return processed_candidates

    def postprocess(self, candidate: StandardCandidate) -> Optional[StandardCandidate]:
        """Check if a candidate should be filtered.

        Parameters
        ----------
        candidate : StandardCandidate
            The candidate object to check.

        Returns
        -------
        Optional[StandardCandidate]
            The unchanged candidate object if its structure is non-disjoint,
            otherwise `None`.
        """
        # doi:10.1016/j.patcog.2008.03.011:
        # "The Laplacian has at least one zero eigenvalue, and the number of
        # such eigenvalues is equal to the number of disjoint parts in the
        # graph."
        eigenvalues = self.descriptor.create_features(candidate)
        disjoint = np.count_nonzero(np.isclose(eigenvalues, 0)) > 1

        if disjoint:
            return None
        else:
            return candidate
