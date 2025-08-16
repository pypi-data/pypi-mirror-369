from collections import Counter
from collections.abc import Hashable
from typing import List

import numpy as np
from numpy.typing import NDArray

from agox.acquisitors.LCB import LowerConfidenceBoundAcquisitor
from agox.candidates.standard import StandardCandidate
from agox.databases.ABC_database import DatabaseBaseClass
from agox.main import State
from agox.models.ABC_model import ModelBaseClass
from agox.models.descriptors import SpectralGraphDescriptor, Voronoi
from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass
from agox.observer import Observer


class LCBPenaltyAcquisitor(LowerConfidenceBoundAcquisitor):
    """Lower confidence bound acquisitor with a penalty term for repeated
    descriptor values.

    The acquisition function for selecting candidates is given by

    .. math::

        F(x) = E(x) - \kappa \sigma(x) + \alpha n_D(x),

    where :math:`n_D` is the number of times the descriptor value already
    exists for the candidates in the database, and :math:`\alpha` is the
    penalty scale value.

    The acquisition function for relaxing candidates is equivalent to that of
    regular LCB, as the :math:`\alpha n_D(x)` term is discontinuous.

    Parameters
    ----------
    model : ModelBaseClass
        Model to obtain energy and uncertainty predictions from.
    descriptor : DescriptorBaseClass
        Descriptor to evaluate descriptor values from.
    penalty_scale : float, optional
        Scale value for penalty (in eV), by default 1.0
    """

    def __init__(self, model: ModelBaseClass, descriptor: DescriptorBaseClass, penalty_scale: float = 1.0, **kwargs):
        super().__init__(model, **kwargs)

        if not isinstance(descriptor, (SpectralGraphDescriptor, Voronoi)):
            raise ValueError("Descriptor can currently only be graph-type descriptor")

        self.descriptor = descriptor
        self.penalty_scale = penalty_scale

        self.descriptor_value_counts = Counter()

        self.add_observer_method(
            self.update_descriptor_values, gets={}, sets={}, order=self.order[0], handler_identifier="database"
        )

    def calculate_acquisition_function(self, candidates: List[StandardCandidate]) -> NDArray:
        fitness = np.zeros(len(candidates))

        for i, candidate in enumerate(candidates):
            E, sigma = self.model.predict_energy_and_uncertainty(candidate)

            descriptor_value = self._get_descriptor_value(candidate)
            count = self.descriptor_value_counts[descriptor_value]
            penalty = count * self.penalty_scale

            fitness[i] = self.acquisition_function(E, sigma) + penalty

            candidate.add_meta_information("model_energy", E)
            candidate.add_meta_information("uncertainty", sigma)
            candidate.add_meta_information("penalty", penalty)

        return fitness

    def print_information(self, candidates: List[StandardCandidate], acquisition_values: List[float]) -> None:
        if self.model.ready_state:
            for i, candidate in enumerate(candidates):
                fitness = acquisition_values[i]
                Emodel = candidate.get_meta_information("model_energy")
                sigma = candidate.get_meta_information("uncertainty")
                penalty = candidate.get_meta_information("penalty")
                self.writer(
                    "Candidate: E={:8.3f}, s={:8.3f}, p={:7.2f}, F={:8.3f}".format(Emodel, sigma, penalty, fitness)
                )

    def attach_to_database(self, database: DatabaseBaseClass) -> None:
        if not isinstance(database, DatabaseBaseClass):
            raise TypeError(f"{database} is not a DatabaseBaseClass object")

        print(f"{self.name}: Attaching to database: {database}")
        self.attach(database)

    @Observer.observer_method
    def update_descriptor_values(self, database: DatabaseBaseClass, state: State) -> None:
        """Update the internal counter of descriptor values present in the
        database.
        """
        candidates = database.get_all_candidates()
        new_candidates = candidates[sum(self.descriptor_value_counts.values()):]

        for candidate in new_candidates:
            descriptor_value = self._get_descriptor_value(candidate)
            self.descriptor_value_counts[descriptor_value] += 1

        s = "s" if len(new_candidates) != 1 else ""
        self.writer(f"Added {len(new_candidates)} structure{s} to the descriptor list")

    def _get_descriptor_value(self, candidate: StandardCandidate) -> Hashable:
        """Obtain a hashable descriptor value to store in the internal counter.

        Parameters
        ----------
        candidate : StandardCandidate
            Candidate to evaluate the descriptor for.

        Returns
        -------
        Hashable
            Hashable descriptor value.
        """
        descriptor_value = self.descriptor.get_features(candidate)

        # convert to hashable object
        if isinstance(descriptor_value, np.ndarray):
            descriptor_value = descriptor_value.data.tobytes()

        return descriptor_value
