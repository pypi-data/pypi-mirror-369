import numpy as np
from ase import Atoms

from agox.generators.ABC_generator import GeneratorBaseClass


class RandomGenerator(GeneratorBaseClass):
    """
    Creates structures without a seed and with minimal bias.

    Parameters
    -----------
    contiguous : bool
        If False, the generator may place atoms at several places on a template. If True,
        any placed atom must be placed close to an already placed atom.
        Replaces 'may_nucleate_at_several_places' which is deprecated.
    replace : bool
        ?
    """

    name = "RandomGenerator"

    def __init__(self, contiguous=True, attempts=100, may_nucleate_at_several_places=None, replace=True, **kwargs):
        super().__init__(replace=replace, **kwargs)
        self.contiguous = contiguous
        self.attempts = attempts
        if may_nucleate_at_several_places is not None:
            DeprecationWarning(f"""'may_nucleate_at_several_places' is deprecated and will be removed. Use 'contiguous' instead.
                               Setting 'contiguous' to {not may_nucleate_at_several_places} which is the inverse of the 
                               supplied value for 'may_nucleate_at_several_places'.""")
            self.contiguous = not may_nucleate_at_several_places

    def _get_candidates(self, candidate, parents, environment):
        template = environment.get_template()
        numbers_list = environment.get_numbers()
        len_of_template = len(template)

        while len(numbers_list) > 0:
            np.random.shuffle(numbers_list)
            atomic_number = numbers_list[0]
            numbers_list = numbers_list[1:]

            placing_first_atom = len(candidate) == len_of_template

            for _ in range(self.attempts):
                if placing_first_atom or not self.contiguous: # If the template is completely empty. 
                    suggested_position = self.get_box_vector()
                else:  # Pick only among atoms placed by the generator.
                    placed_atom = candidate[np.random.randint(len_of_template, len(candidate))]
                    suggested_position = placed_atom.position.copy()
                    # Get a vector at an appropriate radius from the picked atom.
                    vec = self.get_sphere_vector(atomic_number, placed_atom.number)
                    suggested_position += vec

                if not self.check_confinement(suggested_position).all():
                    build_succesful = False
                    continue

                # Check that suggested_position is not too close/far to/from other atoms
                if self.check_new_position(candidate, suggested_position, atomic_number) or len(candidate) == 0:
                    build_succesful = True
                    candidate.extend(Atoms(numbers=[atomic_number], positions=[suggested_position]))
                    break
                else:
                    build_succesful = False

            if not build_succesful:
                self.writer("RandomGenerator failing at producing valid structure")
                return []

        return [candidate]

    def get_number_of_parents(self, sampler):
        return 0
