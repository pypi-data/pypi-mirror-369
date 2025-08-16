import time

import numpy as np
from ase import Atoms
from ase.data import covalent_radii
from ase.geometry import get_distances

from agox.generators.ABC_generator import GeneratorBaseClass
from agox.generators.symmetry_utils.symmetry_enforcer import SymmetryEnforcer


def upper_tri_masking(A):
    m = A.shape[0]
    r = np.arange(m)
    mask = r[:, None] < r
    return A[mask]


class SymmetryGenerator(GeneratorBaseClass):
    """
    Creates random symmetric structures without a seed.

    Parameters:
    -----------
    may_nucleate_at_several_places : bool
        If True, the generator may nucleate at several places in the template,
        meaning that atoms can independently be put at different places on
        the template.
    check_fragmented : bool
        If True, the generator will check if the structure is fragmented.
    sym_type : str
        The symmetry type, either 'slab' or 'cluster'.
    force_group : Symmetry group name or None.
        If not None, the generator will force the symmetry group to be the
        given group.
    equal_element_list : list
        No idea.
    not_sym_list : list
        No idea.
    """

    name = "SymmetryGenerator"

    def __init__(
        self,
        may_nucleate_at_several_places=False,
        check_fragmented=False,
        sym_type="slab",
        force_group=None,
        equal_element_list=[],
        not_sym_list=[],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.may_nucleate_at_several_places = may_nucleate_at_several_places
        self.sym_type = sym_type
        self.check_fragmented = check_fragmented
        # equal element list offers the possibility to switch off element wise deposition for a list of element useful for putting B or N in C60 for instance
        self.equal_element_list = equal_element_list
        self.not_sym_list = not_sym_list
        self.force_group = force_group

    def check_new_position(
        self,
        candidate,
        new_position=None,
        number=None,
        skipped_indices=[],
        mic=True,
        rmax=True,
    ):
        """
        Programing of checking all together
        """
        candi_to_analyse = [candidate.positions[i] for i in range(len(candidate)) if i not in skipped_indices]
        numbers = [covalent_radii[candidate.numbers[i]] for i in range(len(candidate)) if i not in skipped_indices]
        pos = np.array(candi_to_analyse)
        pos = np.reshape(pos, (-1, 3))
        if new_position is not None:
            new_position = np.array(new_position)
            if new_position.ndim == 2:
                if new_position.shape[0] > 1:
                    number = [number] * new_position.shape[0]
            else:
                new_position = np.reshape(new_position, (-1, 3))
            if isinstance(number, list):
                cov = [covalent_radii[num] for num in number]
                numbers.extend(cov)
            else:
                numbers.append(covalent_radii[number])
            if pos.shape[1] == new_position.shape[1]:
                pos = np.vstack((pos, new_position))
            else:
                return False
        if mic == False:
            pbc = [0, 0, 0]
        else:
            pbc = candidate.pbc
        if np.reshape(pos, (-1, 3)).shape[0] > 1:
            pos = np.reshape(pos, (-1, 3))
            vector, dMat = get_distances(pos, pos, cell=candidate.cell, pbc=pbc)
        else:
            return True
            # return False
            # raise
        dist = upper_tri_masking(dMat)
        dist1 = np.tile(numbers, (len(numbers), 1))
        dist2 = dist1.T
        dist_tot_min = self.c1 * (dist1 + dist2)
        dist_tot_max = self.c2 * (dist1 + dist2)
        vect_dist_min = upper_tri_masking(dist_tot_min)
        vect_dist_max = upper_tri_masking(dist_tot_max)

        # print(vect_dist_max-dist)
        if dist.shape[0] == vect_dist_min.shape[0]:
            new_vec = dist - vect_dist_min
        else:
            return False
        if any(new_vec < 0):
            return False
        if rmax == True:
            if np.any(np.all(dist_tot_max - dMat < 0, axis=0)):
                return False
        return True

    def get_number_of_parents(self, sampler):
        return 0

    def _get_candidates(self, sampler, parents, environment):
        template = environment.get_template()
        self.slab = template
        numbers_list = list(environment.get_numbers())
        len_of_template = len(template)
        candidate = template.copy()
        group = None
        table_mult = []
        self.se = SymmetryEnforcer(
            self.slab,
            group=group,
            mode=self.sym_type,
            confinement_cell=self.confinement.cell,
            cell_corner=self.confinement.corner,
            dimensionality=self.get_dimensionality(),
        )
        tries = 0
        t0 = time.time()
        stop = False

        while len(numbers_list) > 0 and tries < 12 and not stop:
            # one can shuffle the atomic deposition but it is not recommended
            # np.random.shuffle(numbers_list)
            atomic_number = numbers_list[0]
            placing_first_atom = len(candidate) == len_of_template
            for _ in range(30):
                at_in_list = 0
                # the deposition is element wise but it could be switched off with the following part
                for num in numbers_list:
                    if num == atomic_number:
                        at_in_list += 1
                    elif num in [self.equal_element_list] and atomic_number in [self.equal_element_list]:
                        at_in_list += 1
                self.se.max_at = at_in_list
                if self.force_group is not None:
                    if isinstance(self.force_group, list):
                        self.force_group = np.random.choice(self.force_group)
                    self.se.force_group = self.force_group
                if self.se.group is None:
                    self.se.group = self.se.select_group(mode=self.sym_type)
                suggested_position = None
                if placing_first_atom or self.may_nucleate_at_several_places:  # If the template is completely empty.
                    suggest = self.get_box_vector()
                    if atomic_number not in self.not_sym_list:
                        if len(candidate) > 0:
                            psym = self.se.get_symmetry_points(
                                suggest,
                                atomic_number=atomic_number,
                                sym_type=self.sym_type,
                                candi=candidate,
                            )
                        else:
                            psym = self.se.get_symmetry_points(
                                suggest,
                                atomic_number=atomic_number,
                                sym_type=self.sym_type,
                            )
                    else:
                        psym = np.array([suggest])
                    if psym is None:
                        tries += 1
                        build_succesful = False
                        if self.se.group["name"].__contains__("C"):
                            stop = True
                            break
                        continue
                    Nadd = psym.shape[0]
                    # > atomic numbers in number_list
                    for p in psym:
                        if suggested_position is None:
                            suggested_position = np.array([p])
                        else:
                            suggested_position = np.vstack((suggested_position, p))
                else:  # Pick only among atoms placed by the generator.
                    placed_atom = candidate[np.random.randint(len_of_template, len(candidate))]
                    suggest = placed_atom.position.copy()
                    # Get a vector at an appropriate radius from the picked atom.
                    vec = self.get_sphere_vector(atomic_number, placed_atom.number)
                    suggest += vec
                    if atomic_number not in self.not_sym_list:
                        psym = self.se.get_symmetry_points(
                            suggest,
                            atomic_number=atomic_number,
                            sym_type=self.sym_type,
                            candi=candidate,
                        )
                    else:
                        psym = np.array([suggest])
                    if psym is None:
                        tries += 1
                        build_succesful = False
                        if self.se.group["name"].__contains__("C"):
                            break
                        continue
                    Nadd = psym.shape[0]
                    for p in psym:
                        if suggested_position is None:
                            suggested_position = np.array([p])
                        else:
                            suggested_position = np.vstack((suggested_position, p))
                if Nadd > at_in_list or suggested_position is None:
                    tries += 1
                    continue
                check = self.check_confinement(suggested_position)
                if not check.all():
                    tries += 1
                    build_succesful = False
                    continue
                # C2 is not really useful when mapping a slab
                if self.sym_type == "cluster":
                    pos = np.vstack((candidate.positions, suggested_position))
                    vector, distances = get_distances(pos, pos)
                    num = candidate.numbers
                    num = np.concatenate((num, [atomic_number] * psym.shape[0]))
                    cov_dist = np.array([covalent_radii[n] for n in num])
                    relative_dist = distances / np.add.outer(cov_dist, cov_dist)
                    L = self.se.get_laplacian_matrix(relative_dist)
                    w, _ = np.linalg.eig(L)
                if len(candidate) > 0:
                    check_pos = self.check_new_position(candidate, suggested_position, atomic_number, rmax=False)
                if len(candidate) > 0 and self.sym_type == "cluster":
                    check_pos = self.check_new_position(candidate, suggested_position, atomic_number)
                    if (
                        self.check_fragmented
                        and np.sum(np.abs(w) < 1e-12) > 1
                        and (len(candidate) + len(suggested_position)) > len(list(environment.get_numbers())) / 2
                        and self.se.system == "cluster"
                    ):
                        tries += 1
                        build_succesful = False
                        continue
                # print(check_pos)
                if len(candidate) == 0 or check_pos:
                    if self.sym_type == "cluster":
                        if (
                            self.check_fragmented
                            and np.sum(np.abs(w) < 1e-12) > 1
                            and len(suggested_position) == len(list(environment.get_numbers()))
                        ):
                            build_succesful = False
                            tries += 1
                            continue
                    build_succesful = True
                    table_mult.append(int(len(suggested_position)))
                    for sugg in suggested_position:
                        numbers_list.remove(atomic_number)
                        candidate.extend(Atoms(numbers=[atomic_number], positions=[sugg]))
                    # tries=0
                    break
                build_succesful = False
        if not build_succesful or len(candidate) != len(template) + len(list(environment.get_numbers())):
            # print('Symmetry generator failing at producing valid structure')
            return []
        if self.sym_type == "cluster":
            table_mult = self.se.table_cluster_desym(self.se.group, table_mult)
        # candidate = self.convert_to_candidate_object(candidate, template)

        candidate.add_meta_information("description", self.name)
        candidate.add_meta_information("space_group", self.se.group["name"])
        candidate.add_meta_information("table_mult", np.array(table_mult))
        candidate.add_meta_information("non_sym", self.not_sym_list)

        if self.se.group["name"].__contains__("C") is True:
            candidate.add_meta_information("lost_sym", 2)
        if self.se.group["name"].__contains__("D") is True and len(self.se.group["name"]) == 2:
            candidate.add_meta_information("lost_sym", 1)
        if self.se.cluster_center is not None:
            candidate.add_meta_information("center", self.se.cluster_center)

        candidate.add_write_key("space_group")

        return [candidate]

        # write('sym.vasp', candidate, format='vasp')
