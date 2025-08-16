from agox.generators.ABC_generator import GeneratorBaseClass
from agox.candidates.standard import StandardCandidate

from ase import Atoms, Atom
import numpy as np

from copy import deepcopy as dcpy


class AddRemoveGenerator(GeneratorBaseClass):
    name = "AdditionRemovalGenerator"

    def __init__(self, max_diff=0, **kwargs):
        super().__init__(**kwargs)
        """Maximum difference of additions and removals from the initial stoichiometry and the final one, 
        <1 means any.
        """
        self.max_diff = max_diff

    def get_composition_delta(self, a1: Atoms, a2: Atoms) -> np.array:
        u_elements = np.unique(np.append(a1.numbers, a2.numbers))
        differences = [
            int((a2.numbers == u).sum() - (a1.numbers == u).sum()) for u in u_elements
        ]

        add_rm = []
        for e, d in zip(u_elements, differences):
            add_rm.extend([e * np.sign(d)] * abs(d))
        return add_rm

    def _get_candidates(self, candidate, parents, environment):
        template = environment.get_template()

        numbers_list_array = environment.get_numbers_list()
        numbers_list = numbers_list_array[np.random.randint(0, len(numbers_list_array))]
            
        a1 = parents[0][len(template) :] # Get the non-template atoms.
        a2 = Atoms(numbers=numbers_list) # Get a random composition.

        # Get the difference in composition.
        delta = self.get_composition_delta(a1, a2)

        t = 0
        while t < 100:
            t + 1
            new_atoms = dcpy(template + a1)

            delta_rand = np.random.permutation(delta)


            success = True
            for d in delta_rand:
                if d > 0:
                    new_atoms, s = self.add_atom(new_atoms, d)
                    if not s:
                        success = False
                        break
                if d < 0:
                    new_atoms, s = self.remove_atom(template, new_atoms, -d)
                    if not s:
                        success = False
                        break
            if success:
                return [StandardCandidate.from_atoms(template, new_atoms)]

        self.writer("AddRemoveGenarator failing at producing valid structure")
        return []

    def add_atom(
        self,
        atoms: Atoms,
        element: int,
    ) -> tuple:  # [Atoms,bool]:
        if len(atoms) == 0:
            p = self.get_box_vector()

            return Atoms(numbers=[element], positions=[p], cell=atoms.cell), True
        t = 0
        new_atoms = dcpy(atoms)
        while t < 100:
            idx = np.random.randint(len(atoms))
            placed_atom = atoms[idx]
            suggested_position = placed_atom.position.copy()
            # Get a vector at an appropriate radius from the picked atom.
            vec = self.get_sphere_vector(element, placed_atom.number)
            suggested_position += vec

            if not self.check_confinement(suggested_position).all():
                continue
            if (
                self.check_new_position(atoms, suggested_position, element)
                or len(atoms) == 0
            ):
                new_atoms.extend(
                    Atoms(numbers=[element], positions=[suggested_position])
                )
                return new_atoms, True

        return new_atoms, False

    def remove_atom(
        self,
        template: Atoms,
        atoms: Atoms,
        element: int,
    ) -> tuple:  # [Atoms,bool]:


        remove_pos = np.flatnonzero(atoms[len(template) :].numbers == element) + len(
            template
        )

        if len(remove_pos) == 0:
            return atoms, False

        rm = np.random.permutation(remove_pos)
        del atoms[rm[0]]
        return atoms, True

    def get_number_of_parents(self, sampler):
        return 1
