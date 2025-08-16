import numpy as np
from ase.geometry import wrap_positions

from agox.generators.symmetry import SymmetryGenerator
from agox.generators.symmetry_utils.symmetry_enforcer import SymmetryEnforcer


class SymmetryRattleGenerator(SymmetryGenerator):
    """
    Rattles atoms in a seed structure while preserving symmetry or systematically
    reducing symmetry.

    Parameters
    -----------
    n_rattle : int
        Medium number of atoms to rattle.
    rattle_amplitude : float
        Maximum distance to rattle atoms.
    let_lose_sym : float
        Probability of losing symmetry.
    let_switch : float
        Probability of switching points.
    write_strucs : bool
        If True, write structures to disk.
    """

    name = "RattleGeneratorSym"

    def __init__(
        self,
        n_rattle=1,
        rattle_amplitude=3,
        let_lose_sym=0,
        let_switch=1.0,
        write_strucs=True,
        replace=True,
        **kwargs,
    ):
        super().__init__(replace=replace, **kwargs)
        self.n_rattle = n_rattle
        self.write_strucs = write_strucs
        self.rattle_amplitude = rattle_amplitude
        # probability of losing symmetry : float between 0 and 1 it is advised to set it considering the difficulty of the problem. The more diffuclt the lower
        self.let_lose_sym = let_lose_sym
        # activates the switch points algorithm
        self.not_sym = []
        self.let_switch = let_switch
        self.move_on_point = True

    def _get_candidates(self, candidate, parents, environment):
        rang = 50
        already_lost = None
        keep_sym = True
        not_sym = []
        # Happens if no candidates are part of the sample yet.
        if candidate is None:
            return []
        template = candidate.get_template()
        self.slab = template

        meta_required = ["space_group", "table_mult", "non_sym", "center"]
        for meta in meta_required:
            candidate.add_meta_information(meta, parents[0].get_meta_information(meta))

        try:
            group_met = candidate.get_meta_information("space_group")
            if group_met is None:
                self.se = SymmetryEnforcer(self.slab)
                group_met = self.se.determine_plane_group(candidate.positions[len(template) :])

                num = candidate.numbers[len(template) :]
                table = []
                table_mult = []
                counter = 0
                num_ = None
                for j, elem in enumerate(num):
                    if j == 0 or elem == num_:
                        counter += 1
                        num_ = elem
                        continue
                    else:
                        table.append(counter)
                        num_ = elem
                        counter = 1
                table.append(counter)
                for ta in table:
                    num_f = ta // group_met["number_max"]
                    table_mult += [group_met["number_max"]] * num_f
                    if ta % group_met["number_max"] != 0:
                        table_mult += [ta % group_met["number_max"]]
                already_lost = 0
                center = None
                group_met = group_met["name"]
                if group_met != "p1":
                    print("symmetry found!")
            else:
                table_mult = list(candidate.get_meta_information("table_mult"))
                not_sym = candidate.get_meta_information("non_sym")
                center = candidate.get_meta_information("center")

            if group_met.__contains__("p") == False:
                mode = "cluster"
                rang = 20
            else:
                mode = "slab"

            self.se = SymmetryEnforcer(
                self.slab,
                confinement_cell=self.confinement.cell,
                cell_corner=self.confinement.corner,
                mode=mode,
            )
            if len(template) == 0:
                self.se.cell = candidate.get_cell()
            self.se.cluster_center = center
            gr = group_met
            self.se.force_group = group_met
            group_met = self.se.select_group(mode=mode)
            self.not_sym = not_sym
            already_lost = candidate.get_meta_information("lost_sym")
        except Exception as e:
            print(e)
            group_met = {
                "name": "p1",
                "system": ["rectangular", "hexagonal", "square", "oblique", "rhombic"],
                "number_max": 1,
                "axes": None,
                "rotations": None,
                "points": None,
            }
            table_mult = [1] * len(environment.get_numbers())
            not_sym = []
            mode = None
            already_lost = 0
        if already_lost is None:
            already_lost = 0
        let_lose_sym = self.let_lose_sym ** (already_lost + 1)
        group = group_met
        if let_lose_sym > np.random.random():
            keep_sym = False
            sumtoreach = sum(table_mult)
            table_multcop = table_mult.copy()
            if mode == "cluster":
                su = np.sum(table_mult)
                group, table_mult = self.se.select_group_desym_cluster(group_met, table_mult)
                assert su == np.sum(table_mult), str(table_multcop) + " " + str(table_mult)
            else:
                group, table_mult = self.se.select_group_desym(group_met, table_mult)
                if group["name"] == "p2cmmg" and group_met["name"] == "p4g":
                    candidate.positions[len(template) :] -= [
                        0,
                        -candidate.cell[1][1] / 2,
                        0,
                    ]
                    candidate.positions = wrap_positions(candidate.positions, candidate.get_cell(), candidate.pbc)
                    print("translated")
        self.se.group = group
        rattled = False
        if self.se.group is not None:
            if self.let_switch >= np.random.random() and table_mult is not None and group["name"] not in ["C1", "p1"]:
                candiswitch = candidate.copy()
                candidate, table_mult2 = self.se.swap_some_points(candidate, environment, table_mult)
                if candidate is None:
                    candidate = candiswitch
                else:
                    # write('resym_s.vasp', candidate,  format='vasp')
                    rattled = True
                    table_mult = table_mult2
        else:
            self.se.group = {
                "name": "p1",
                "system": ["rectangular", "hexagonal", "square", "oblique", "rhombic"],
                "number_max": 1,
                "axes": None,
                "rotations": None,
                "points": None,
            }
        indices_to_rattle = self.get_indices_to_rattle(candidate, table_mult, keep_sym)
        print(group["name"] + " " + str(indices_to_rattle) + " " + str(let_lose_sym) + " ")
        for i in indices_to_rattle:
            i = int(i)
            vector_displac = None
            self.se.atomic_number = candidate.numbers[i]
            for _ in range(rang):  # For atom i attempt to rattle up to 30 times.
                candicopy = candidate.copy()
                if group is None or group["number_max"] == 1 or candidate[i].number in not_sym or already_lost > 1:
                    # it is recommended to rattle gently symmetryc structures but no longer relevant for P1
                    radius = 2.5 * np.random.rand() ** (1 / self.get_dimensionality())
                else:
                    radius = self.rattle_amplitude * np.random.rand() ** (1 / self.get_dimensionality())
                displacement = self.get_displacement_vector(radius)
                posit = candidate.get_scaled_positions()
                if group is None or group["number_max"] == 1 or candidate[i].number in not_sym:
                    if not self.check_confinement(candidate[i].position + displacement):
                        continue
                    if self.check_new_position(
                        candidate,
                        candidate[i].position + displacement,
                        candidate[i].number,
                        skipped_indices=[i],
                    ):
                        candidate[i].position += displacement
                        rattled = True
                        break
                    continue
                if mode == "cluster":
                    vector_displac = self.se.identify_mult_point_cluster_new(
                        candidate, table_mult, i, displacement, keep_sym
                    )
                    if vector_displac is not False and np.linalg.norm(vector_displac) > 1e-6:
                        displacement = (
                            np.array(vector_displac) * ((-1) ** np.random.randint(1, 6)) * np.linalg.norm(displacement)
                        )
                    if vector_displac is False:
                        break
                else:
                    if vector_displac is None:
                        vector_displac = self.se.identify_mult_point_fast(
                            candidate, table_mult, i, displacement, keep_sym
                        )
                    if vector_displac is not False and np.linalg.norm(vector_displac) > 1e-6:
                        vector_displac[2] = displacement[2] / np.linalg.norm(displacement)
                        displacement = (
                            np.array(vector_displac) * ((-1) ** np.random.randint(1, 6)) * np.linalg.norm(displacement)
                        )
                    if vector_displac is False:
                        (
                            sug_pos,
                            vector_displac,
                            scal_pos,
                            vector_scaled,
                        ) = self.se.replace_on_ax(candidate.positions[i])
                        candidate[i].position = sug_pos[0]

                        print(
                            "unidentifed axis leads to "
                            + str(group["name"])
                            + " "
                            + str(posit[i])
                            + " ->"
                            + str(scal_pos)
                            + " with vect "
                            + str(vector_scaled)
                            )
                        displacement = (
                            np.array(vector_displac) * ((-1) ** np.random.randint(1, 6)) * np.linalg.norm(displacement)
                        )
                sug_pos = [np.copy(candidate.positions[i]) + displacement]
                sug_pos = wrap_positions(sug_pos, candidate.cell, candidate.pbc)
                sug_pos = sug_pos[0]
                if not self.check_confinement(sug_pos).all():
                    continue
                candicopy[i].position = sug_pos
                # This part handles the merging algorithm and is probably the most not stable not well coded part of the rattle
                ind = self.se.get_position_in_table(candidate, i, table_mult)

                if self.check_new_position(
                    candidate,
                    sug_pos,
                    candidate[i].number,
                    skipped_indices=list(range(i, i + table_mult[ind])),
                    mic=False,
                    rmax=False,
                ):
                    merge, table_mult_new, new_t = self.se.merger(
                        candicopy, i, group, table_mult, cutoff=0.6, disp=displacement
                    )

                    if merge is None:
                        continue
                    # print(str(i)+ ' ' + ' '+str(resym.shape[0])+ ' '+str(table_mult)+' '+str(table_mult_new))
                    if len(merge) == len(candicopy.positions[i : i + merge.shape[0]]):
                        candicopy.positions[i : i + merge.shape[0]] = merge
                    else:
                        continue
                    if self.se.system == "cluster":
                        mic = False
                    else:
                        mic = True
                    if mode == "cluster" and self.check_new_position(candicopy, mic=mic, rmax=False):
                        candidate.positions = candicopy.positions
                        table_mult = table_mult_new
                        assert np.sum(table_mult) == len(candidate)
                        rattled = True
                        break
                    elif mode != "cluster" and self.check_new_position(candicopy, mic=mic, rmax=False):
                        candidate.positions[i] = sug_pos
                        ret_t = 0
                        # dirty implementation yet to improve
                        if len(new_t) > 1:
                            table_mult = table_mult_new
                            candidate.positions[i + new_t[0]] = merge[new_t[0]]
                        if len(new_t) > 2:
                            candidate.positions[i + new_t[0] + new_t[1]] = merge[new_t[0] + new_t[1]]
                        if len(new_t) > 3:
                            candidate.positions[i + new_t[0] + new_t[1] + new_t[2]] = merge[
                                new_t[0] + new_t[1] + new_t[2]
                            ]
                        posit2 = candidate.get_scaled_positions()
                        """
                             try:
                                resym, table_mult_2=self.se.resymmetrize(candidate, group, table_mult, cutoff=0.5,keep_sym=keep_sym,indices_to_rattle=indices_to_rattle,not_sym=not_sym)
                             except:
                                continue
                             if resym is None or resym.shape[0]!=len( list(environment.get_numbers())) :
                                continue
                             candidate.positions[len(template):] =  resym
                             table_mult=table_mult_2
                             """
                        rattled = True
                        break
        if rattled:
            # if mode!='cluster' or keep_sym==False:
            if self.se.group["name"] not in ["C1", "p1"] and len(table_mult) > 1:
                copytabl = table_mult.copy()
                try:
                    resym, table_mult = self.se.resymmetrize(
                        candidate,
                        group,
                        table_mult,
                        cutoff=0.5,
                        keep_sym=keep_sym,
                        indices_to_rattle=indices_to_rattle,
                        not_sym=not_sym,
                    )
                except:
                    raise
                    return []
                if (
                    resym is None
                    or np.sum(table_mult) != (len(candidate) - len(template))
                    or resym.shape[0] != len(list(environment.get_numbers()))
                ):
                    print(str(table_mult) + " " + str(self.se.group["name"]) + " " + str(copytabl))
                    return []
                candidate.positions[len(template) :] = resym
            candidate.add_meta_information("space_group", group["name"])
            candidate.add_meta_information("table_mult", np.array(table_mult))
            if keep_sym == False and (group["number_max"] < 8 or mode != "cluster"):
                already_lost += 1
            candidate.add_write_key("space_group")
            return [candidate]
        else:
            return []

    def get_indices_to_rattle(self, candidate, table_mult=None, keep_sym=True):
        # Establish indices_to_rattle as the indices of the atoms that should be rattled
        n_rattle = self.n_rattle
        if keep_sym:
            if self.n_rattle < 2 and len(table_mult) >= 12:
                n_rattle = 2
            if self.n_rattle < 3 and len(table_mult) > 20 or max(table_mult) == 1:
                n_rattle = 6
        template = candidate.get_template()
        n_template = len(template)
        n_total = len(candidate)
        n_non_template = n_total - n_template
        probability = n_rattle / n_non_template
        indices_to_rattle = np.arange(n_template, n_total)[np.random.rand(n_non_template) < probability]
        if len(self.not_sym) > 0:
            n_rattle += len(self.not_sym)
        if table_mult is not None:
            if max(table_mult) > 1:
                scale = abs(((len(table_mult) * n_rattle - n_rattle**2) / len(table_mult))) ** 0.5
                size = min(len(table_mult), int(np.random.normal(loc=n_rattle, scale=scale)))
                if size < 1:
                    size = 1
                table = np.concatenate(([0], table_mult[:-1]))
                for i in range(len(table)):
                    if i > 0:
                        table[i] = table[i] + table[i - 1]
                table += len(template)
                indices_to_pick = table
                prob = np.array(table_mult) / n_non_template
                if np.sum(prob) != 1:
                    prob /= np.sum(prob)
                indices_to_rattle = np.random.choice(indices_to_pick, p=prob, replace=False, size=size)
                np.sort(indices_to_rattle)

        if len(indices_to_rattle) == 0:
            indices_to_rattle = [np.random.randint(n_template, n_total)]
        # now indices_to_rattle is ready to use
        return indices_to_rattle

    def get_number_of_parents(self, sampler):
        return 1
