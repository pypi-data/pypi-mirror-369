from typing import List

import numpy as np

from agox.candidates import Candidate
from agox.environments import Environment
from agox.generators.ABC_generator import GeneratorBaseClass
from agox.samplers import Sampler


class RattleGenerator(GeneratorBaseClass):
    """
    Rattles atoms in a seed structure, e.g. perturbs atoms in random directions.

    Parameters
    -----------
    n_rattle : int
        Medium number of atoms to rattle.
    rattle_amplitude : float
        Maximum distance to rattle atoms.
    """

    name = "RattleGenerator"

    def __init__(self, n_rattle: int = 3, rattle_amplitude: int = 3, replace: bool = True, attempts=100, **kwargs) -> None:
        super().__init__(replace=replace, **kwargs)
        self.n_rattle = n_rattle
        self.attempts = attempts
        self.rattle_amplitude = rattle_amplitude

    def _get_candidates(self, candidate: Candidate, parents: List[Candidate], environment: Environment):
        indices_to_rattle = self.get_indices_to_rattle(candidate)

        for i in indices_to_rattle:
            for _ in range(self.attempts):  # For atom i attempt to rattle up to 100 times.
                radius = self.rattle_amplitude * np.random.rand() ** (1 / self.get_dimensionality())
                displacement = self.get_displacement_vector(radius)
                suggested_position = candidate.positions[i] + displacement

                # Check confinement limits:
                if not self.check_confinement(suggested_position).all():
                    continue

                # Check that suggested_position is not too close/far to/from other atoms
                # Skips the atom it self.
                if self.check_new_position(
                    candidate,
                    suggested_position,
                    candidate[i].number,
                    skipped_indices=[i],
                ):
                    candidate[i].position = suggested_position
                    break

        return [candidate]

    def get_indices_to_rattle(self, candidate: Candidate) -> np.ndarray:
        template = candidate.get_template()
        n_template = len(template)
        n_total = len(candidate)
        n_non_template = n_total - n_template
        probability = self.n_rattle / n_non_template
        indices_to_rattle = np.arange(n_template, n_total)[np.random.rand(n_non_template) < probability]
        indices_to_rattle = np.random.permutation(indices_to_rattle)
        if len(indices_to_rattle) == 0:
            indices_to_rattle = [np.random.randint(n_template, n_total)]
        return indices_to_rattle

    def get_number_of_parents(self, sampler: Sampler) -> int:
        return 1
