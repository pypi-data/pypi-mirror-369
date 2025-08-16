import random

import numpy as np
from ase.data import covalent_radii
from ase.io import write

from agox.generators.ABC_generator import GeneratorBaseClass
from agox.generators.symmetry_utils.symmetry_enforcer import SymmetryEnforcer


class SymmetryPermutationGenerator(GeneratorBaseClass):
    """
    Swaps atoms in a structure while enforcing symmetry.

    Parameters
    -----------
    max_number_of_swaps : int
        Maximum number of permutations to perform.
    rattle_strength : float
        Maximum distance to permute atoms.
    use_xy_only : bool
        If True, only permute in xy-plane.
    ignore_H : bool
        If True, ignore hydrogen atoms.
    write_candidates_to_disk : bool
        If True, write candidates to disk.
    """

    name = "PermutationGenerator"

    def __init__(
        self,
        max_number_of_swaps=1,
        rattle_strength=0.0,
        use_xy_only=False,
        ignore_H=False,
        write_candidates_to_disk=False,
        replace=True,
        **kwargs,
    ):
        super().__init__(replace=replace, **kwargs)
        self.max_number_of_swaps = max_number_of_swaps
        self.rattle_strength = rattle_strength
        self.ignore_H = ignore_H
        self.use_xy_only = use_xy_only
        self.write_candidates_to_disk = write_candidates_to_disk

    def _get_candidates(self, candidate, parents, environment):
        if candidate is None:
            return []
        num = random.randrange(0, 1001, 2)

        if self.write_candidates_to_disk:
            write(f"candidate_{self.counter}.traj", candidate)
        number_of_atoms = len(candidate)
        number_of_template_atoms = len(candidate.get_template())
        number_of_non_template_atoms = number_of_atoms - number_of_template_atoms
        try:
            template = candidate.get_template()
            self.slab = template
            self.se = SymmetryEnforcer(
                self.slab,
                confinement_cell=self.confinement_cell,
                cell_corner=self.confinement_corner,
            )
            group_met = candidate.get_meta_information("space_group")
            table_mult = list(candidate.get_meta_information("table_mult"))
            not_sym = candidate.get_meta_information("non_sym")
            already_lost = candidate.get_meta_information("lost_sym")
            self.se.force_group = group_met
            group_met = self.se.select_group(mode=mode)
            self.not_sym = not_sym
        except:
            group_met = {
                "name": "p1",
                "system": ["rectangular", "hexagonal", "square", "oblique", "rhombic"],
                "number_max": 1,
                "axes": None,
                "rotations": None,
                "points": None,
            }
            table_mult = [1] * number_of_non_template_atoms
        template = candidate.get_template()
        if table_mult is not None:
            table = np.concatenate(([0], table_mult[:-1]))
            for i in range(len(table)):
                if i > 0:
                    table[i] = table[i] + table[i - 1]
            table += len(template)
            indices_to_permute = table

        symbols = candidate.get_atomic_numbers()[number_of_template_atoms:]
        unique_symbols = np.unique(symbols)
        if self.ignore_H:
            unique_symbols = np.array([s for s in unique_symbols if s != 1])

        number_of_unique_symbols = len(unique_symbols)
        assert number_of_unique_symbols > 1, "Cannot be used for single component systems"
        write("permute.vasp", candidate)

        number_of_swaps = np.random.randint(self.max_number_of_swaps) + 1

        for n in range(number_of_swaps):
            symbol_i = unique_symbols[np.random.randint(number_of_unique_symbols)]
            remaining_symbols = np.delete(
                unique_symbols,
                [idx for idx in range(number_of_unique_symbols) if unique_symbols[idx] == symbol_i],
            )

            symbol_j = remaining_symbols[np.random.randint(number_of_unique_symbols - 1)]

            idx_symbol_i = np.argwhere(symbols == symbol_i).reshape(-1) + number_of_template_atoms
            idx_symbol_j = np.argwhere(symbols == symbol_j).reshape(-1) + number_of_template_atoms

            # can only permute the first index of each table_mult
            idx_symbol_i = intersection = np.intersect1d(indices_to_permute, idx_symbol_i)
            idx_symbol_j = intersection = np.intersect1d(indices_to_permute, idx_symbol_j)

            combinations_ij = np.array(np.meshgrid(idx_symbol_i, idx_symbol_j)).T.reshape(-1, 2)

            for row in np.random.permutation(combinations_ij):
                swap_idx_i = row[0]
                swap_idx_j = row[1]
                # here the combination should only happend if multiplicity is the same for both atoms
                tab1 = int(np.argwhere(indices_to_permute == swap_idx_i))
                tab2 = int(np.argwhere(indices_to_permute == swap_idx_j))

                if table_mult[tab1] != table_mult[tab2]:
                    continue
                new_positions = candidate.get_positions()
                for sym_t in range(table_mult[tab1]):
                    try:
                        new_positions[[swap_idx_i + sym_t, swap_idx_j + sym_t]] = new_positions[
                            [swap_idx_j + sym_t, swap_idx_i + sym_t]
                        ]
                    except:
                        return []
                """
                if self.use_xy_only:
                    new_positions[swap_idx_i] +=self.pos_add_disk(self.rattle_strength)
                    new_positions[swap_idx_j] +=self.pos_add_disk(self.rattle_strength)
                else:
                    new_positions[swap_idx_i] +=self.pos_add_sphere(self.rattle_strength)
                    new_positions[swap_idx_j] +=self.pos_add_sphere(self.rattle_strength)
                """

                swap_successfull = True
                near_enough_to_other_atoms = False
                for i in (swap_idx_i, swap_idx_j):
                    for other_atom_idx in range(len(candidate)):
                        if other_atom_idx in [swap_idx_i, swap_idx_j]:
                            continue
                        other_atom = candidate[other_atom_idx]

                        covalent_dist = covalent_radii[candidate[i].number] + covalent_radii[other_atom.number]

                        rmin = 0.85 * covalent_dist
                        rmax = 1.15 * covalent_dist
                        tmp = np.linalg.norm(other_atom.position - new_positions[i])
                        if np.linalg.norm(other_atom.position - new_positions[i]) < rmin:
                            swap_successfull = False
                            break
                        if np.linalg.norm(other_atom.position - new_positions[i]) < rmax:
                            near_enough_to_other_atoms = True
                    if not swap_successfull or not near_enough_to_other_atoms:
                        break

                if not swap_successfull or not near_enough_to_other_atoms:
                    continue

                candidate.set_positions(new_positions)
                if self.write_candidates_to_disk:
                    write(f"candidate_swap_{n}_{self.counter}.traj", candidate)
                break
            else:
                self.writer("No swaps possible")
                return []

        return [candidate]

    def pos_add_disk(self, rattle_strength):
        """Help function for rattling within a disk"""
        r = rattle_strength * np.random.rand() ** (1 / 2)
        theta = np.random.uniform(low=0, high=2 * np.pi)
        pos_add = r * np.array([np.cos(theta), np.sin(theta), 0])
        return pos_add

    def pos_add_sphere(self, rattle_strength):
        """Help function for rattling within a sphere"""
        r = rattle_strength * np.random.rand() ** (1 / 3)
        theta = np.random.uniform(low=0, high=2 * np.pi)
        phi = np.random.uniform(low=0, high=np.pi)
        pos_add = r * np.array([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)])
        return pos_add

    def get_number_of_parents(self, sampler):
        return 1
