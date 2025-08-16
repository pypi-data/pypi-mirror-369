import numpy as np

from agox.generators.ABC_generator import GeneratorBaseClass


class SteepestDescentGenerator(GeneratorBaseClass):
    """
    Performs a steepest descent step on a seed structure.

    TODO: Clean-up this code. Its bad.

    Parameters
    -----------

    use_xy_only : bool
        If True, only move atoms in xy-plane.
    replace : bool
        ?
    """

    name = "SteepestDescentGenerator"

    def __init__(self, use_xy_only=False, replace=True, **kwargs):
        super().__init__(replace=replace, **kwargs)
        self.use_xy_only = use_xy_only

    def _get_candidates(self, candidate, parents, environment):
        parents[0].copy_calculator_to(candidate)

        # If the Sampler is not able to give a structure with forces
        if candidate is None or candidate.calc is None or "forces" not in candidate.calc.results:
            return []

        template = candidate.get_template()
        len_of_template = len(template)

        delta = np.random.uniform(0, 0.1)

        self.writer(self.name, ": got a candidate with a force. will take step:", delta)

        candidate.positions[len_of_template:] += delta * candidate.get_forces()[len_of_template:]

        return [candidate]

    def get_number_of_parents(self, sampler):
        return 1
