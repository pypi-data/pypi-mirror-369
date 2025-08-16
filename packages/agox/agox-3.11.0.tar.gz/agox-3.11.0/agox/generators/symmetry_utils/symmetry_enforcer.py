from math import cos, sin

import numpy as np
import scipy.spatial.distance as ssd
from ase import Atoms
from ase.build.tools import sort
from ase.data import covalent_radii
from ase.geometry import get_distances, wrap_positions
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import cdist, pdist

from agox.generators.symmetry_utils.symmetry_groups import (
    cluster_sym_dict,
    default_sym_dict,
)


def upper_tri_masking(A):
    m = A.shape[0]
    r = np.arange(m)
    mask = r[:, None] < r
    return A[mask]


class SymmetryEnforcer:
    def __init__(
        self,
        slab,
        max_at=12,
        mode="cluster",
        group=None,
        confinement_cell=None,
        cell_corner=None,
        dimensionality=3,
    ):
        self.slab = slab
        self.group = group
        self.dimensionality = 3
        self.cell = self.slab.get_cell()
        self.pbc = slab.get_pbc()
        self.max_at = max_at
        # get cell vectors
        x = np.random.uniform(0, 1)
        self.radius = 1.5
        self.sym_type = None
        self.confinement_cell = confinement_cell
        self.cell_corner = cell_corner
        self.force_group = None
        self.cluster_center = None
        self.construction = np.random.choice(["outer", "inner"])
        self.mode = mode
        self.older_max_at = 0
        self.tries_max = 0
        # determine the geometry of the cell
        if not self.pbc.any():
            self.system = "cluster"
        elif round(self.cell.angles()[2], 2) == 60 or round(self.cell.angles()[2], 2) == 120:
            self.system = "hexagonal"
        elif 88.5 < self.cell.angles()[2] < 91:
            if abs(self.cell.cellpar()[0] - self.cell.cellpar()[1]) < 1e-3:
                self.system = "square"
            else:
                self.system = "rectangular"
        elif abs(self.cell.cellpar()[0] - self.cell.cellpar()[1]) < 1e-3:
            self.system = "rhombic"
        else:
            self.system = "oblique"
        if self.pbc.all() and self.mode == "cluster":
            if self.system == "square":
                if abs(self.cell.cellpar()[0] - self.cell.cellpar()[2]) < 1e-3:
                    self.system = "cubic"
                else:
                    self.system = "tetragonal"
            elif self.system == "rectangular":
                self.system = "orthorombique"
        # axes :[[[[1,1,0],[1/2,1/2,0]]]] is an exemple of glide of 0.5x 0.5y after symmetry on axe 1,1,0
        # rotations:[[0,0,0],6] is a rotation aroud 0 0 1 on the center 0 0 0 of order 6
        # for cluster rotations defines de vector and the center is the center of the confinement cell
        # plane: defines a plane of symmetry and [-1,-1,-,1] is the inversion center
        self.dimensionality_angles = {
            3: {"theta": [0, 2 * np.pi], "phi": [0, np.pi]},
            2: {"theta": [0, 2 * np.pi], "phi": [np.pi / 2, np.pi / 2]},
            1: {"theta": [0, 0], "phi": [np.pi / 2, np.pi / 2]},
        }

        self.defaut_sym_dict = default_sym_dict
        self.cluster_sym_dict = cluster_sym_dict

    def get_box_vector(self):
        return self.confinement_cell.T @ np.random.rand(3) + self.cell_corner

    def get_displacement_vector(self, radius):        
        theta = np.random.uniform(*self.dimensionality_angles[self.dimensionality]["theta"])
        phi = np.random.uniform(*self.dimensionality_angles[self.dimensionality]["phi"])
        displacement = radius * np.array([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)])
        return displacement

    def get_laplacian_matrix(self, relative_dist):
        A = np.logical_and(relative_dist > 0.75, relative_dist < 1.5).astype(int)
        D = np.diag(np.sum(A, axis=1))
        return D - A

    def get_cluster_center(self):
        center_of_conf = self.confinement_cell.T @ [0.5, 0.5, 0.5] + self.cell_corner
        if self.slab is None or len(self.slab) == 0:
            self.cluster_center = center_of_conf
            return center_of_conf
        else:
            at = self.return_three_closest(self.slab, center_of_conf)
            table = [
                self.slab[at[0]].position,
                1 / 2 * (self.slab[at[0]].position + self.slab[at[1]].position),
                1 / 3 * (self.slab[at[0]].position + self.slab[at[1]].position + self.slab[at[2]].position),
            ]
            self.cluster_center = np.random.choice(table)
            return self.cluster_center

    def get_mid_conf(self):
        len_clu = self.confinement_cell.T @ [1, 1, 1] + self.cell_corner - self.cluster_center
        return len_clu[0]

    def return_three_closest(self, candidate, position):
        # cov=0.7*(covalent_radii[self.atomic_number] + covalent_radii[self.atomic_number])
        p_new = np.copy(candidate.positions)
        dist = cdist(p_new, [position])
        dist = dist[dist > 0.05]
        idx = np.argpartition(dist, 3)
        return idx[:3]

    def check_dist_mic(self, candidate, mic=True):
        dMat = candidate.get_all_distances(mic=mic)
        numbers = [covalent_radii[candidate.numbers[i]] for i in range(len(candidate))]

        dist = upper_tri_masking(dMat)
        dist1 = np.tile(numbers, (len(numbers), 1))
        dist2 = dist1.T
        dist_tot_min = 0.7 * (dist1 + dist2)
        vect_dist_min = upper_tri_masking(dist_tot_min)

        new_vec = dist - vect_dist_min
        if any(new_vec < 0):
            return False
        return True

    def get_symmetry_points(
        self,
        p,
        combine_nearby_positions=False,
        sym_type="slab",
        order=None,
        atomic_number=None,
        candi=None,
    ):
        """The main function that returns on sym points altogether"""
        p = np.copy(p).reshape(1, 3)
        self.atomic_number = atomic_number
        self.sym_type = sym_type
        psym = np.zeros((1, 3))

        if sym_type == "cluster":
            if self.cluster_center is None:
                center = self.get_cluster_center()
            # axe0=p-center
            psym = p
            cov = 0.7 * (covalent_radii[self.atomic_number] + covalent_radii[self.atomic_number])
            len_clu = self.get_mid_conf()
            psym = None
            tries = 0
            sym_dict = self.group
            prot = np.copy(p)
            p_new = np.copy(prot)
            # p_new=np.array([self.cluster_center + self.get_displacement_vector(self.radius)])
            self.construction = np.random.choice(["inner", "outer"])
            self.radius = cov / 0.7
            if self.construction == "outer":
                self.radius = len_clu
                p_new = np.array([self.cluster_center + self.get_displacement_vector(self.radius)])
            radius0 = self.radius
            # radius0=len_clu/2
            # self.radius=radius0
            maxtries = 40
            for tries in range(maxtries):
                sym_dict = self.group
                if self.max_at < sym_dict["number_max"] or tries > maxtries / 2:
                    if tries == maxtries / 2:
                        # if self.max_at<=sym_dict['number_max']:
                        #    return None
                        # else:
                        self.radius = radius0
                    if sym_dict["points"] is not None:
                        p_new = self.select_mult_point(sym_dict, p_new)
                p_new = self.do_sym_operations(p_new, sym_dict, cutoff=cov / 2, mic=False)
                if p_new.shape[0] > 2 and sym_dict["number_max"] > 2:
                    ghost = self.group["ghost"]
                    if self.pbc.all() and self.group["name"] in ["D2h", "D3h", "D4h"]:
                        ghost *= 2
                    if self.max_at < ghost or self.tries_max > 20:
                        group, tabl = self.select_group_desym_cluster(group=self.group)
                        if group["number_max"] > 6:
                            self.group = group
                            self.radius = radius0
                            continue
                        else:
                            return None
                    # dist = pdist(p_new)
                    dist = cdist(p_new, p_new)
                    dist = dist[dist > 0.01]
                    if candi is not None and p_new.shape[0] > 0:
                        vector, distances = get_distances(p_new, candi.positions)
                        dist = np.concatenate((dist.flatten(), distances.flatten()))
                    distances = dist
                    if (2 < (self.max_at - p_new.shape[0]) < self.group["ghost"] and tries < 10) or distances.shape[
                        0
                    ] < 1:
                        continue
                    if (
                        np.amin(distances) < cov
                        or np.amin(distances) > 2.5 * cov
                        or p_new.shape[0] > self.max_at
                        or sym_dict["number_max"] % p_new.shape[0] != 0
                        or p_new.shape[0] < sym_dict["ghost"]
                    ):
                        if self.radius < len_clu:
                            if self.construction == "inner":
                                self.radius += (len_clu - cov) / (maxtries / 2)
                            else:
                                self.radius = max(
                                    cov,
                                    self.radius - (len_clu - 1.5 * cov) / (maxtries / 2),
                                )
                        p_new = np.array([self.cluster_center + self.get_displacement_vector(self.radius)])
                        continue
                elif (self.max_at > 2 and sym_dict["number_max"] > 2) or (
                    self.max_at == 2
                    and not self.group["name"].__contains__("C")
                    and p_new.shape[0] == 1
                    and self.system == "cluster"
                ):
                    p_new = np.array([self.cluster_center + self.get_displacement_vector(self.radius)])
                    continue
                p_new[:] = wrap_positions(p_new, self.cell, pbc=self.pbc)
                p_new = sort(p_new, tags=p_new[:, 2])
                p_new = sort(p_new, tags=abs(p_new[:, 2] - self.cluster_center[2]))
                if self.older_max_at == self.max_at:
                    self.tries_max += 1
                else:
                    self.tries_max == 0
                psym = np.copy(p_new)
                self.older_max_at = self.max_at
                break
        elif sym_type == "slab":
            cov = 0.75 * (covalent_radii[self.atomic_number] + covalent_radii[self.atomic_number])
            psym = None
            tries = 0
            sym_dict = self.group
            prot = np.copy(p)
            p_new = np.copy(prot)
            while psym is None and tries < 15:
                if self.max_at < sym_dict["number_max"] or tries > 10:
                    if sym_dict["points"] is not None:
                        p_new = self.select_mult_point(sym_dict, p_new)
                p_new = self.do_sym_operations(p_new, group=sym_dict, cutoff=0.25, mic=True)
                # advantage axis on rotation point because rotation point can come frome merging
                if sym_dict["axes"] is not None and self.max_at >= sym_dict["number_max"] / 2:
                    if p_new.shape[0] < sym_dict["number_max"] / 2:
                        tries += 1
                        continue
                p_new[:] = wrap_positions(p_new, self.cell, self.pbc)
                if p_new.shape[0] > 1:
                    vector, distances = get_distances(p_new, p_new, cell=self.cell, pbc=self.pbc)
                    distances = distances.flatten()
                    distances = distances[distances > 0.05]
                    if (
                        np.amin(distances) < cov
                        or p_new.shape[0] > self.max_at
                        or p_new.shape[0] > sym_dict["number_max"]
                    ):
                        p_new = np.array([self.get_box_vector()])
                        tries += 1
                        continue
                psym = np.copy(p_new)
        return psym

    def del_duplicate_positions(self, pos, cutoff=0.5, delete=True, merge=False, mic=False, atomic_number=1):
        dists = pdist(pos, "euclidean")
        dup = np.nonzero(dists < cutoff)
        rem = np.array(self._row_col_from_pdist(pos.shape[0], dup[0]))
        # to test merge atoms
        tab_todel = None
        if delete:
            if rem.size != 0:
                try:
                    pos = np.delete(pos, rem[:, 0], axis=0)
                except:
                    pos = np.delete(pos, rem[0], axis=0)
            if merge:
                pos = self.get_symmetrised_positions(pos, atomic_number)
                return pos
            # slower method but more accurate used after to exec on a shorter list
            elif mic:
                # working with mic but slow then the shorter the list the better this method has been created for helping finding back the plane group
                tab_todel = None
                for i in range(len(pos - 1)):
                    disti = self.get_distances(pos, i, range(i + 1, len(pos)), mic=True)
                    tabdel = (np.argwhere(disti < cutoff) + i + 1).flatten()
                    if tabdel is not None and len(tabdel) > 0:
                        if tab_todel is None:
                            tab_todel = tabdel
                        else:
                            tab_todel = np.concatenate((tab_todel, tabdel))
                if tab_todel is not None and len(tab_todel) > 0:
                    tab_todel = np.unique(tab_todel)
                    pos = np.delete(pos, list(tab_todel), axis=0)
            return pos
        else:
            return rem

    def _row_col_from_pdist(self, dim, i):
        i = np.array(i)
        b = 1 - 2 * dim
        x = (np.floor((-b - np.sqrt(b**2 - 8 * i)) / 2)).astype(int)
        y = (i + x * (b + x + 2) / 2 + 1).astype(int)
        if i.shape:
            return list(zip(x, y))
        else:
            return [(x, y)]

    def rotate_around_vector(self, p_rot, theta, v, center=np.array([0, 0, 0])):
        if np.array(p_rot).ndim == 1:
            p_rot = [p_rot]
        norm = np.linalg.norm
        normv = norm(v)
        v /= normv
        p_copy = np.copy(p_rot)
        center = self.cell.cartesian_positions(center)
        p_copy = p_copy - center
        pos_new = None
        # for j, p1 in enumerate(p_rot):
        for a in theta:
            angle = a * np.pi / 180
            c = cos(angle)
            s = sin(angle)
            rot_new = c * p_copy - np.cross(p_copy, s * v) + np.outer(np.dot(p_copy, v), (1.0 - c) * v) + center
            if pos_new is None:
                pos_new = rot_new
            else:
                pos_new = np.vstack((pos_new, rot_new))
        return pos_new

    def get_distances(self, pos, a, i, mic=True, vector=False):
        p1 = pos[a]
        p2 = pos[i]

        cell = None
        pbc = None

        if mic:
            cell = self.cell
            pbc = self.pbc
        D, D_len = get_distances(np.array([p1]), np.array([p2]), cell=self.cell, pbc=self.pbc)

        if vector:
            D.shape = (-1, 3)
            return D
        else:
            D_len.shape = (-1,)
            return D_len

    def do_sym_operations(
        self,
        psym,
        group=None,
        cutoff=0.25,
        merge=False,
        mic=False,
        return_only_sym_pos=False,
    ):
        pcop = psym.copy()
        if self.group is not None and group is None:
            group = self.group
        else:
            group = group

        p_new = np.copy(psym)
        if p_new.ndim == 1:
            p_new = np.array([p_new])
        rot_list = group["rotations"]
        if "cluster" in group["system"]:
            mode = "cluster"
            centersym = self.cell.scaled_positions(self.cluster_center)
        else:
            mode = "slab"
        if group["name"] == "Ih5":
            for axe in group["axes"]:
                if mode == "cluster":
                    p_new = self.symmetry_ax(p_new, axe, p0=centersym)
                else:
                    p_new = self.symmetry_ax(p_new, axe)
        if rot_list is not None:
            for rotations in rot_list:
                order = rotations[1]
                listangles = [k * 360 // order for k in range(order)]
                centerot = rotations[0].copy()
                vecterot = [0, 0, 1]
                if mode == "cluster":
                    centerot = centersym
                    vecterot = rotations[0].copy()
                p_new = self.rotate_around_vector(p_new, listangles, vecterot, center=centerot)
        p_new = self.del_duplicate_positions(p_new, cutoff=cutoff, delete=True, merge=merge, mic=mic)
        if self.pbc.any():
            p_new[:] = wrap_positions(p_new, self.cell, self.pbc)
        p_ref = None
        if group["axes"] is not None:
            for axe in group["axes"]:
                if mode == "cluster":
                    p_new = self.symmetry_ax(p_new, axe, p0=centersym)
                else:
                    p_new = self.symmetry_ax(p_new, axe)
        if mode == "cluster":
            if group["plane"] is not None:
                for plane in group["plane"]:
                    if group["plane"] is not None:
                        if plane == [-1, -1, -1]:
                            p_inv = -p_new + 2 * self.cell.cartesian_positions(centersym)
                            p_new = np.vstack((p_new, p_inv))
                        elif plane == [1, 1, 1]:
                            p_inv = p_new.copy()
                            p_inv = p_inv - (
                                2
                                * (
                                    p_inv * [0, 0, 1]
                                    - [
                                        0,
                                        0,
                                        self.cell.cartesian_positions(centersym)[2],
                                    ]
                                )
                            )
                            p_new = np.vstack((p_new, p_inv))
                        elif plane == [1, -1, -1]:
                            p_inv = p_new.copy()
                            p_inv = p_inv - (
                                2
                                * (
                                    p_inv * [0, 1, 1]
                                    - [
                                        0,
                                        self.cell.cartesian_positions(centersym)[1],
                                        self.cell.cartesian_positions(centersym)[2],
                                    ]
                                )
                            )
                            p_new = np.vstack((p_new, p_inv))
                        else:
                            p_new = self.symmetry_plane(p_new, plane, p0=centersym)
        if mode != "cluster":
            p_new[:] = wrap_positions(p_new, self.cell, self.pbc)
        p_sym2 = np.copy(p_new)
        if return_only_sym_pos:
            p_sym2 = self.del_duplicate_positions(p_sym2, cutoff=0.1, delete=True, merge=False, mic=True)
            jdel = []
            for j, sy in enumerate(p_sym2):
                if any((pcop[:] == sy).all(axis=0)):
                    jdel.append(j)
            psym_2 = np.delete(p_sym2, jdel, axis=0)
            return p_sym2
        p_sym2 = self.del_duplicate_positions(p_sym2, cutoff=cutoff, delete=True, merge=merge, mic=mic)
        return p_sym2

    def identify_mult_point_fast(self, candidate, table_mult, i, displacement, keep_sym=True):
        # super fast identification that relies on direct coordinates
        ind = self.get_position_in_table(candidate, i, table_mult)
        if table_mult[ind] == self.group["number_max"]:
            if keep_sym == True or self.group["axes"] is None:
                return [0.0, 0.0, 0.0]
        # print(table_mult[ind])
        if (
            table_mult[ind] < int(self.group["number_max"] / 2) - 0.1
            or self.group["axes"] is None
            or self.group["name"] == "p2gg"
        ):
            return [0.0, 0.0, 1.0]
        else:
            pos = np.copy([candidate.positions[i]])
            pos[0, 2] = 0
            pos2 = np.copy(pos)
            ax = None
            if self.group["axes"] is not None:
                ax = self.is_on_ax2(pos)
                if ax is False:
                    if keep_sym == False and table_mult[ind] == self.group["number_max"]:
                        return [0.0, 0.0, 0.0]
                    return ax
                ax = self.cell.cartesian_positions(ax)
                ax = ax / np.linalg.norm(ax)
                ax[2] = np.random.rand()
                return ax
        return displacement

    def identify_mult_point_cluster_new(self, candidate, table_mult, i, displacement, keep_sym):
        ind = self.get_position_in_table(candidate, i, table_mult)
        if table_mult[ind] == self.group["number_max"]:
            # if keep_sym ==True:
            return [0.0, 0.0, 0.0]
        axes = self.group["axes"]
        plane = self.group["plane"]
        rotations = self.group["rotations"]
        pos = candidate[i].position.copy()
        mult = np.array(
            [
                1,
                1,
                1,
            ]
        )
        if candidate.pbc.all():
            for j, elem in enumerate(self.cell.scaled_positions(pos)):
                if elem <= 0.05 or 0.48 < elem < 0.52:
                    mult[j] = 0
        pos -= self.cluster_center
        pos *= mult
        if np.linalg.norm(pos) < 1e-3 or (2 < table_mult[ind] < self.group["ghost"]) or table_mult[ind] == 1:
            return False
        to_ret = np.random.choice((-1, 1)) * pos / np.linalg.norm(pos)
        if table_mult[ind] < self.group["number_max"] / 2 or axes is None:
            return to_ret
        elif table_mult[ind] == self.group["number_max"] / 2 and axes is not None:
            if self.group["name"].__contains__("h") is True and abs(pos[2]) < 1:
                to_ret = np.array(
                    [
                        np.random.random() * np.random.choice((-1, 1)),
                        np.random.random() * np.random.choice((-1, 1)),
                        0,
                    ]
                )
                to_ret /= np.linalg.norm(to_ret)
            else:
                to_ret = to_ret + np.random.choice((-1, 1)) * np.random.random() * np.array([0, 0, 1])
                to_ret /= np.linalg.norm(to_ret)
            return to_ret
        return to_ret

    def identify_mult_point_cluster(self, candidate, table_mult, i, displacement, keep_sym):
        ind = self.get_position_in_table(candidate, i, table_mult)
        if table_mult[ind] == self.group["number_max"]:
            # if keep_sym ==True:
            return [0.0, 0.0, 0.0]
        axes = self.group["axes"]
        plane = self.group["plane"]
        rotations = self.group["rotations"]
        pos = candidate[i].position.copy()
        pos -= self.cluster_center

        if np.linalg.norm(pos) < 1e-3 or 2 < table_mult[ind] < self.group["ghost"]:
            return False
        numofsym = 4
        if axes is not None and rotations is not None:
            numofsym = len(axes) * 2
        if self.group["name"] in ["D2d_2", "D2d", "D4d", "D6d"]:
            numofsym = 4
        if self.group["name"] == "D2":
            return pos / np.linalg.norm(pos)
        # handles simple C groups and D groups
        if axes is None and plane is None and rotations is not None:
            # C and D groups on z axis
            if table_mult[ind] <= 2:
                pos[0] = 0
                pos[1] = 0
            # D point groups on rot centers
            elif self.group["name"].__contains__("D") is True:
                # pos[0]=random.random()
                pos[2] = 0
            return pos / np.linalg.norm(pos)
        # handle is in the xy plane
        if table_mult[ind] <= self.group["number_max"] / numofsym or self.group["name"] in ["Th"]:
            if table_mult[ind] > 2 and self.group["name"].__contains__("D"):
                pos[2] = 0
            if abs(pos[2]) < 6e-1:
                pos[2] = 0
            return pos / np.linalg.norm(pos)
        # in the plane + axe  linear combination of vector - center and  (001) is in the symmetric plane
        axes = np.random.random() * pos + np.random.choice((-1, 1)) * np.random.random() * np.array([0, 0, 1])
        axes /= np.linalg.norm(axes)
        """
        if  table_mult[ind]>self.group['number_max']/numofsym and self.group['name'] not in ['Th','Td'] and pos[2]>3e-1 and axes is not None:
            axes=random.random()*pos+random.choice((-1, 1))*random.random()*np.array([0,0,1]) 
            axes/=np.linalg.norm(axes)
            #print(str(self.group['name'])+ ' bouger dans le plan')
        else:
            axes=pos
            axes/=np.linalg.norm(pos) 
        """
        return axes

    def switch_mult_point(self, pos, force_number=0):
        if np.array(pos).ndim == 1:
            pos = np.array([pos])
        mode = "slab"
        if self.group["name"].__contains__("p") == False:
            mode = "cluster"
        pos2 = np.copy(pos)
        sym_dict = self.group
        new_mult = self.select_mult_point(sym_dict, pos2)
        new_mult = self.do_sym_operations(new_mult, sym_dict)
        tries = 0
        if force_number > 0:
            while new_mult.shape[0] != force_number and tries < 50:
                new_mult = self.select_mult_point(sym_dict, pos2)
                new_mult = self.do_sym_operations(new_mult, sym_dict)
                tries += 1
                if mode == "cluster" or tries > 20:
                    pos2 = np.array([self.get_box_vector()])
            if tries == 49:
                return None
            return new_mult
        else:
            return new_mult

    def get_position_in_table(self, a, ind, table_mult):
        template = a.get_template()
        table = np.concatenate(([0], table_mult[:-1]))
        for i in range(len(table)):
            if i > 0:
                table[i] = table[i] + table[i - 1]
        table += len(template)
        table = table.tolist()
        for k in range(len(table) - 1):
            if table[k + 1] > ind >= table[k]:
                return k
        return len(table) - 1

    def get_two_mult_points(self, a, table_mult, atomic_number=None, n=2):
        template = a.get_template()
        table_mult2 = table_mult.copy()
        table = np.concatenate(([len(template)], table_mult2[:-1]))
        for i in range(1, len(table)):
            table[i] += table[i - 1]
        table = table.tolist()
        table_candi = []
        twopoints = []
        tries = 0
        copytabl = table_mult.copy()
        randax = np.random.random()

        while len(twopoints) < n and tries < 30:
            r = np.random.randint(0, len(table))
            tries += 1
            if atomic_number is None or atomic_number == a.numbers[int(table[r])]:
                if r not in twopoints:
                    if table_mult2[r] == self.group["number_max"] and self.group["number_max"] > 3:
                        continue
                    if (
                        table_mult2[r] == self.group["number_max"] / 2
                        and self.group["axes"] is not None
                        and self.group["number_max"] > 4
                    ):
                        if n > 2 or randax < 0.7:
                            continue
                    twopoints.append(r)
                    if table_mult2[r] >= self.group["number_max"] / 2 and self.group["number_max"] > 2:
                        break
                    tries = 0
        twopoints.sort(reverse=True)
        for j in range(len(twopoints)):
            table_mult2.pop(twopoints[j])
        for k in twopoints:
            if k == len(table) - 1:
                table_candi += range(len(a) - copytabl[-1], len(a))
            else:
                table_candi += range(table[k], table[k + 1])
        return table_candi, table_mult2

    def fill_mult_point(self, pos, force_number=-1, candidate=None):
        # fill  a cell with special point
        sym_dict = self.group
        maxtries = 60
        if sym_dict["name"].__contains__("p") == False:
            mode = "cluster"
            maxtries = 80
            pos = np.array([self.get_box_vector()])
            if candidate is not None and candidate.pbc.any():
                mic = True
            else:
                mic = False
        else:
            mode = "slab"
            mic = True
        new_mult = np.array([], dtype=np.int64).reshape(0, 3)
        table_mult = []
        if candidate is None:
            new_mult = self.select_mult_point(sym_dict, pos)
            new_mult = self.do_sym_operations(new_mult, sym_dict, mic=mic)
            table_mult = [new_mult.shape[0]]
            dists = pdist(new_mult, "euclidean")
            if len(dists) > 0 and min(dists) < 1.8:
                new_mult = np.array([], dtype=np.int64).reshape(0, 3)
        tries = 0
        while new_mult.shape[0] != force_number and tries < maxtries:
            if tries == maxtries - 1:
                return None, None
            if mode == "cluster" or tries > 5:
                pos = np.array([self.get_box_vector()])
            app_mult = self.select_mult_point(sym_dict, pos)
            app_mult = self.do_sym_operations(app_mult, sym_dict, mic=mic)
            dists = pdist(app_mult, "euclidean")
            if len(dists) > 0 and min(dists) < 1.8:
                tries += 1
                continue
            if candidate is not None:
                _, distances = get_distances(
                    np.vstack((new_mult, candidate.positions)),
                    app_mult,
                    cell=self.cell,
                    pbc=candidate.pbc,
                )
            elif new_mult.shape[0] > 0:
                _, distances = get_distances(app_mult, new_mult, cell=self.cell, pbc=[1, 1, 1])
            if new_mult.shape[0] == 0:
                distances = np.array([2])
            distances = distances.flatten()
            if new_mult.shape[0] + app_mult.shape[0] <= force_number and min(distances) > 1.8:
                new_mult = np.vstack((new_mult, app_mult))
                table_mult.append(app_mult.shape[0])
            elif min(distances) > 1.8:
                new_mult = app_mult
                table_mult = [app_mult.shape[0]]
            tries += 1
        if new_mult.shape[0] != force_number:
            return None, None
        return new_mult, table_mult

    def select_mult_point(self, sym_dict, p_rot, number=1):
        """
        This function selects a random special point
        for cluster it places atoms according to the cluster center
        """
        if self.group is not None:
            group = self.group
        else:
            group = sym_dict
        if group["name"].__contains__("p") == False:
            mode = "cluster"
        else:
            mode = "slab"
        if np.array(p_rot).ndim == 1:
            p_rot = np.array([p_rot])
        if type(p_rot) == list:
            p_rot = np.array(p_rot)
        psym = sym_dict["points"]
        if self.pbc.all() and mode == "cluster":
            # add some wyckoff positions for bulk
            psym = np.vstack((psym, self.cluster_center, self.cluster_center * [1, 0, 0]))
        x = np.random.uniform(0, 1)
        y = np.random.uniform(0, 1)
        if mode == "cluster":
            # else:
            p_rot = abs(p_rot) - self.cluster_center
            x = p_rot[0][0]
            y = p_rot[0][2]
        # if  self.sym_type=='cluster':
        select = np.random.randint(0, len(psym))
        psym = psym[select].copy()
        for j, elem in enumerate(psym):
            if type(elem) == int or type(elem) == float:
                continue
            if elem == "x":
                psym[j] = x
            elif elem == "y":
                psym[j] = y
            elif elem == "1/2(1-x)":
                psym[j] = 1 / 2 * (1 - x)
            elif elem.__contains__("x"):
                elem = elem.replace("x", str(x))
                elem = eval(elem)
                psym[j] = elem
        psym = np.copy(np.array(psym))
        psym = psym.astype(np.float64)
        if self.pbc.all() and mode == "cluster":
            for kl, ps in enumerate(psym):
                if ps == 0 and np.sum(psym) != 0:
                    psym[kl] = np.random.choice([0, self.cluster_center[kl]])
        if mode != "cluster":
            psym = np.array(self.cell.cartesian_positions(psym))
            if psym[2] == 0:
                try:
                    psym[:, 2] = p_rot[:, 2]
                    return psym
                except:
                    psym[2] = p_rot[0, 2]
        else:
            psym += self.cluster_center
        return np.array([psym])

    def is_on_ax2(self, pref, lim=5e-2):
        """
        This function identifies the mirror on which the atom is on
        based on sclaed positions
        """
        pos = self.cell.scaled_positions(pref)
        cell_u = self.cell.cellpar()[0]
        lim = lim * 12 / cell_u
        pos = pos[0]
        if self.group["name"] == "p4g":
            if 0.5 - lim <= abs(pos[1] - pos[0]) <= 0.5 + lim:
                return [1, 1, 0]
            if 0.5 - lim <= abs(pos[1] + pos[0] - 1) <= 0.5 + lim:
                return [1, -1, 0]
        if self.group["name"] == "p4m" or self.group["name"] == "p2mm":
            if 0.5 - lim <= abs(pos[1]) <= 0.5 + lim:
                return [1, 0, 0]
            if 0.5 - lim <= abs(pos[0]) <= 0.5 + lim:
                return [0, 1, 0]
        if self.group["name"] != "p3m1":
            if pos[0] < lim or pos[0] > 1 - lim:
                return [0, 1, 0]
            if pos[1] < lim or pos[1] > 1 - lim:
                return [1, 0, 0]
            if 1 - lim <= pos[0] + pos[1] <= 1 + lim:
                return [1, -1, 0]
        if self.group["name"] != "p31m":
            if pos[1] - lim <= pos[0] <= pos[1] + lim:
                return [1, 1, 0]
            if self.system == "hexagonal":
                if (
                    0.5 - 0.5 * pos[0] - lim <= pos[1] <= 0.5 - 0.5 * pos[0] + lim
                    or round(1 - 0.5 * pos[0], 2) - lim <= pos[1] <= round(1 - 0.5 * pos[0], 2) + lim
                ):
                    return [1, -1 / 2, 0]
                if (
                    round(0.5 - 0.5 * pos[1], 2) - lim <= pos[0] <= round(0.5 - 0.5 * pos[1], 2) + lim
                    or round(1 - 0.5 * pos[1], 2) - lim <= pos[0] <= round(1 - 0.5 * pos[1], 2) + lim
                ):
                    return [-1 / 2, 1, 0]
        return False

    def replace_on_ax(self, pref):
        """
        This function replaces atom on the closest mirror
        useful because relaxation can move them out
        """
        pos = self.cell.scaled_positions(pref)
        # pos=pos[0]
        minim = 1
        if self.group["name"] == "p4g":
            d = abs(0.5 - abs(pos[1] - pos[0]))
            if d < minim:
                minim = d
                minax = [1, 1, 0]
            d = abs(0.5 - abs(pos[1] - pos[0] - 1))
            if d < minim:
                minim = d
                minax = [1, -1, 0]
        if self.group["name"] == "p4m" or self.group["name"] == "p2mm":
            d = abs(0.5 - abs(pos[1]))
            if d < minim:
                minim = d
                minax = [1 / 2, 0, 0]
            d = abs(0.5 - abs(pos[0]))
            if d < minim:
                minim = d
                minax = [0, 1 / 2, 0]
        if self.group["name"] != "p3m1":
            d = abs(pos[0])
            if d < minim or abs(d - 1) < minim:
                minim = d
                minax = [0, 1, 0]
            d = abs(pos[1])
            if d < minim or abs(d - 1) < minim:
                minim = d
                minax = [1, 0, 0]
            d = abs(pos[1] + pos[0])
            if abs(d - 1) < minim:
                minim = d
                minax = [1, -1, 0]
        if self.group["name"] != "p31m":
            d = abs(pos[1] - pos[0])
            if d < minim:
                minim = d
                minax = [1, 1, 0]
            if self.system == "hexagonal":
                d = abs(pos[1] + 0.5 * pos[0] - 0.5)
                if d < minim:
                    minim = d
                    minax = [1, -1 / 2, 0]
                d = abs(pos[1] + 0.5 * pos[0] - 1)
                if d < minim:
                    minim = d
                    minax = [1, -1 / 2, 0]
                d = abs(pos[0] + 0.5 * pos[1] - 1)
                if d < minim:
                    minim = d
                    minax = [-1 / 2, 1, 0]
                d = abs(pos[0] + 0.5 * pos[1] - 0.5)
                if d < minim:
                    minim = d
                    minax = [-1 / 2, 1, 0]
        if self.group["name"] == "p4g":
            if pos[1] < 0.5:
                pos_new = np.array([pos[1], pos[1] + 0.5, pos[2]])
            else:
                pos_new = np.array([pos[1], pos[1] - 0.5, pos[2]])

        elif minax == [1, -1 / 2, 0] and pos[1] < 0.5:
            pos_new = np.array([pos[0] * minax[0], 0.5 + pos[0] * minax[1], pos[2]])
        elif minax == [-1 / 2, 1, 0] and pos[0] < 0.5:
            pos_new = np.array([pos[0] * minax[0] - 0.5, pos[0] * minax[1], pos[2]])
        elif 1 / 2 in minax and (self.group["name"] == "p4m" or self.group["name"] == "p2mm"):
            if minax[0] == 1 / 2:
                pos_new = np.array([pos[0], 1 / 2, pos[2]])
            else:
                pos_new = np.array([1 / 2, pos[1], pos[2]])
        elif minax[0] != 0:
            pos_new = np.array([pos[0] * minax[0], pos[0] * minax[1], pos[2]])
        else:
            pos_new = np.array([pos[1] * minax[0], pos[1] * minax[1], pos[2]])
        pos_newcar = self.cell.cartesian_positions(pos_new)
        mincar = self.cell.cartesian_positions(minax)
        mincar = mincar / np.linalg.norm(mincar)
        return pos_newcar, mincar, pos_new, minax

    def choose_rotation_ax(self, group, order):
        tab_rot = None
        rotations = group["rotations"]
        for rot in rotations:
            if rot[1] == order:
                if tab_rot is None:
                    tab_rot = np.array([rot[0]])
                else:
                    tab_rot = np.vstack((tab_rot, rot[0]))

        if tab_rot is None:
            return None
        else:
            ind = list(range(tab_rot.shape[0]))
            chosen = np.random.choice(ind)
            return tab_rot[chosen]

    def replace_on_point_cluster(self, pos, j):
        """
        This function is used to replace atoms on a guessed symmetric position
        """
        group = self.group
        axes = self.group["axes"]
        if pos.ndim == 2:
            pos = pos[0] - self.cluster_center
        elif group["number_max"] > 6:
            return self.cluster_center
        """
        if j < group['ghost'] and group['name'] not in ['Th','Td','T','Oh4','Ih5']:
            if sum(pos)>0:
                pos=np.linalg.norm(pos)*np.array([0,0,1])
            else:
                pos=-np.linalg.norm(pos)*np.array([0,0,1])
        """
        if group["name"] in ["D2", "D3", "D4", "D5", "D6"]:
            if group["name"] == "D2" and j == 2:
                if max(abs(pos)) == abs(pos[2]):
                    pos[0] = 0
                    pos[1] = 0
                else:
                    if abs(pos[0]) < abs(pos[1]):
                        pos[0] = 0
                    else:
                        pos[1] = 0
                    pos[2] = 0
            elif j == 2:
                pos[0] = 0
                pos[1] = 0
            elif j == group["ghost"]:
                sym_di = self.cluster_sym_dict
                gr = str(group["name"]) + "h"
                for sym in sym_di:
                    if sym["name"] == gr:
                        pseudo_axes = np.array(sym["axes"])
                        break
                ind = list(range(len(pseudo_axes)))
                chosen = np.random.choice(ind)
                # posz=pos[2].copy()
                pos[2] = 0
                pos = np.linalg.norm(pos) * np.array(pseudo_axes[chosen])
                # pos[2]=posz
        elif group["name"] in ["D2h", "D2h_2", "D2d", "D2d_2"] and j == 2:
            if max(abs(pos)) == pos[2]:
                pos[0] = 0
                pos[1] = 0
            elif group["name"] in ["D2d", "D2d_2"]:
                pos = np.linalg.norm(pos) * np.array([0, 0, 1])
            else:
                pos[2] = 0
                ind = list(range(len(axes)))
                chosen = np.random.choice(ind)
                if sum(pos) > 0:
                    pos = np.linalg.norm(pos) * np.array(axes[chosen])
                else:
                    pos = -np.linalg.norm(pos) * np.array(axes[chosen])
        elif axes is not None and j >= group["ghost"]:
            # for  Dh et Dd point groups
            if (
                group["ghost"] == group["number_max"] / 4
                and j == group["ghost"]
                and group["name"] not in ["D2d", "D2d_2"]
            ):
                pos[2] = 0
            posz = pos[2]
            ind = list(range(len(axes)))
            chosen = np.random.choice(ind)
            if sum(pos) > 0:
                pos = np.linalg.norm(pos) * np.array(axes[chosen])
            else:
                pos = -np.linalg.norm(pos) * np.array(axes[chosen])
            pos[2] = posz
        elif group["rotations"] is not None:
            # doit gerer C et D
            rot = self.choose_rotation_ax(self.group, int(self.group["number_max"] / j))
            if rot is not None:
                if sum(pos) > 0:
                    pos = np.linalg.norm(pos) * np.array(rot)
                else:
                    pos = -np.linalg.norm(pos) * np.array(rot)
            else:
                return None
        elif j < group["ghost"] and group["name"] not in [
            "Th",
            "Td",
            "T",
            "Oh4",
            "Ih5",
        ]:
            if sum(pos) > 0:
                pos = np.linalg.norm(pos) * np.array([0, 0, 1])
            else:
                pos = -np.linalg.norm(pos) * np.array([0, 0, 1])
        else:
            print(group)
            print("point not found " + str(self.group["name"]))
        try:
            if abs(pos[2]) < 0.6:
                pos[2] = 0
            pos += self.cluster_center
            return pos
        except:
            print(str(group["name"]) + " " + str(pos))
            pass
        return None

    def symmetry_ax(self, p_new, axe, p0=[0, 0, 0]):
        glidaxe = [0, 0, 0]
        axe2 = np.array(axe)
        c = self.cell.reshape(3, 3)
        if axe2.ndim == 2 and axe2.shape[0] > 1:
            glidaxe = np.array(axe2[1])
            # p0=np.dot(p0,c)
            axe = np.array(axe2[0])
            if axe2.shape[0] > 2:
                p0 = axe2[2]
        p0 = self.cell.cartesian_positions(p0)
        p0[2] = p_new[0][2]
        pref = np.array([p_new[0]])
        norm = np.linalg.norm
        nvec = np.cross(axe, np.array([0, 0, 1]))
        nvec = np.dot(nvec / norm(nvec), c)
        glidaxe = self.cell.cartesian_positions(glidaxe)
        for j, pr in enumerate(p_new):
            proj = self.get_orthog_vec_from_plane(pr, nvec, p0)
            # print(str(axe) +' ' + str(nvec) +' ' + str(proj))
            p_reflected = pr - 2 * proj
            p_reflected += glidaxe
            pref = np.vstack((pref, p_reflected))
        if pref.shape[0] > 1:
            p_new = np.vstack((p_new, pref[1:]))
        # print(p_new)
        return p_new

    def symmetry_plane(self, p_new, axe, p0=[0.5, 0.5, 0.5]):
        norm = np.linalg.norm
        pref = np.array([p_new[0]])
        glidaxe = [0, 0, 0]
        c = self.cell.reshape(3, 3)
        p0 = self.cell.cartesian_positions(p0)
        nvec = axe
        if np.array(axe).ndim == 2:
            glidaxe = np.array(axe[1])
            # p0=axe[2]
            # p0=np.dot(p0,c)
            axe = axe[0]
        nvec = np.dot(nvec / norm(nvec), c)
        for j, pr in enumerate(p_new):
            p_reflected = self.mirror_point_in_plane(pr, nvec, p0=p0)
            pref = np.vstack((pref, p_reflected))
        if pref.shape[0] > 1:
            p_new = np.vstack((p_new, pref[1:]))
        return p_new

    def mirror_point_in_plane(self, p, nvec, p0=np.array([0, 0, 0])):
        proj = self.get_orthog_vec_from_plane(p, nvec, p0)
        p_reflected = p - 2 * proj
        return p_reflected

    def get_orthog_vec_from_plane(self, p, nvec, p0=np.array([0, 0, 0])):
        a = p - p0
        nvec_unit = (nvec / np.linalg.norm(nvec)).reshape(1, 3)
        proj_orthog = a @ nvec_unit.T @ nvec_unit
        return proj_orthog

    def make_clustering(self, pos, atomic_number):
        min_dist = 1.4 * covalent_radii[atomic_number]
        Natoms = pos.shape[0]
        a = Atoms(
            numbers=[atomic_number] * Natoms,
            positions=pos,
            pbc=self.pbc,
            cell=self.cell,
        )
        dMat = a.get_all_distances(mic=True)
        dVec = ssd.squareform(dMat)
        linked = linkage(dVec, "single", metric=None)
        clustering = fcluster(linked, t=min_dist, criterion="distance") - 1
        return clustering

    def select_group_desym_cluster(
        self,
        group=None,
        table_mult=None,
    ):
        # handle decreasing symmetry on slab
        sym_di = self.cluster_sym_dict
        sym_dict = []
        proba = []
        if group is None:
            group = self.group
        for elem in sym_di:
            if group is not None:
                if elem["name"] in group["subgroups"] and self.system in elem["system"]:
                    sym_dict.append(elem)
        if len(sym_dict) == 0:
            print("fail desym " + str(elem["name"]))
            return group, table_mult
        ind = list(range(len(sym_dict)))
        chosen = np.random.choice(ind)
        group = sym_dict[chosen]
        if table_mult is not None:
            table_mult = self.table_cluster_desym(group, table_mult)
        return group, table_mult

    def table_cluster_desym(self, group, table_mult):
        table_mult_cluster_desym = []
        for ta in table_mult:
            if ta > group["number_max"]:
                if ta == 12 and group["number_max"] == 8:
                    table_mult_cluster_desym.append(4)
                    table_mult_cluster_desym.append(8)
                elif ta == 12 and group["name"] in ["C5"]:
                    table_mult_cluster_desym.append(5)
                    table_mult_cluster_desym.append(5)
                    table_mult_cluster_desym.append(1)
                    table_mult_cluster_desym.append(1)
                elif ta == 12 and group["name"] in ["C5v"]:
                    table_mult_cluster_desym.append(10)
                    table_mult_cluster_desym.append(1)
                    table_mult_cluster_desym.append(1)
                else:
                    num_f = ta // group["number_max"]
                    if ta % group["number_max"] != 0:
                        table_mult_cluster_desym += [ta % group["number_max"]]
                    table_mult_cluster_desym += [group["number_max"]] * num_f
            elif group["number_max"] % ta != 0:
                if ta == 12 and group["name"] == "D5d":
                    table_mult_cluster_desym.append(2)
                    table_mult_cluster_desym.append(10)
                elif ta == 6 and group["number_max"] == 8:
                    table_mult_cluster_desym.append(2)
                    table_mult_cluster_desym.append(4)
                elif ta == 12 and group["number_max"] == 16:
                    table_mult_cluster_desym.append(8)
                    table_mult_cluster_desym.append(4)
                elif ta == 6 and group["number_max"] == 16:
                    table_mult_cluster_desym.append(4)
                    table_mult_cluster_desym.append(2)
                elif ta == 8 and group["number_max"] == 12:
                    table_mult_cluster_desym.append(4)
                    table_mult_cluster_desym.append(4)
                elif ta == 2 and group["name"] in [
                    "C3",
                    "C4",
                    "C5",
                    "C6",
                    "C3v",
                    "C4v",
                    "C5v",
                    "C6v",
                ]:
                    table_mult_cluster_desym.append(1)
                    table_mult_cluster_desym.append(1)
                else:
                    table_mult_cluster_desym.append(ta)
            elif ta == 2 and group["name"] in ["C4", "C6", "C4v", "C6v"]:
                table_mult_cluster_desym.append(1)
                table_mult_cluster_desym.append(1)
            elif ta == 8 and group["name"] == "Td":
                table_mult_cluster_desym.append(4)
                table_mult_cluster_desym.append(4)
            else:
                table_mult_cluster_desym.append(ta)
        return table_mult_cluster_desym

    def select_group_desym(self, group=None, table_mult=None):
        # handle decreasing symmetry on slab
        sym_di = self.defaut_sym_dict
        sym_dict = []
        proba = []
        for elem in sym_di:
            if group is not None:
                if self.system in elem["system"]:
                    if (
                        len(list(set(elem["name"]) & set(group["name"]))) > 1
                        or len(group["name"]) == 2
                        or group["name"] == "pcmm"
                    ):
                        if (
                            elem["number_max"] == group["number_max"] / 2
                            or elem["number_max"] == group["number_max"] / 3
                        ):
                            sym_dict.append(elem)
                            if elem["axes"] == None and elem["number_max"] > 4:
                                proba.append(2)
                            else:
                                proba.append(1)
        group_or = group.copy()
        if len(sym_dict) == 0:
            return group, table_mult
        proba = np.array(proba) / np.sum(proba)
        ind = list(range(len(sym_dict)))
        chosen = np.random.choice(ind, p=proba)
        group = sym_dict[chosen]
        table_mult_new = []

        for t in table_mult:
            if t > group["number_max"]:
                if t == group_or["number_max"]:
                    if group["number_max"] == group_or["number_max"] / 2:
                        table_mult_new.append(int(group["number_max"]))
                        table_mult_new.append(int(group["number_max"]))
                    elif group["number_max"] == group_or["number_max"] / 3:
                        table_mult_new.append(int(group["number_max"]))
                        table_mult_new.append(int(group["number_max"]))
                        table_mult_new.append(int(group["number_max"]))
                    else:
                        return group_or, table_mult
                else:
                    for i in range(t):
                        table_mult_new.append(1)
            else:
                table_mult_new.append(int(t))
        return group, table_mult_new

    def select_group(self, return_all=False, mode=None):
        "This function selects a start group"
        sym_di = self.defaut_sym_dict
        sym_dict = []
        number_max = 1
        if mode == "cluster":
            sym_di = self.cluster_sym_dict
            sym_dict = []
            number_max = 16
        for elem in sym_di:
            if self.system in elem["system"] or isinstance(self.force_group, str):
                if elem["name"] == self.force_group:
                    sym_dict.append(elem)
                    return sym_dict[0]
                elif isinstance(self.force_group, str):
                    continue
                elif mode == "cluster" and elem["number_max"] >= number_max and len(elem["name"]) >= 2:
                    # get rid of some point groups at some conditions
                    if elem["name"] in ["D5d"]:
                        continue
                    if (self.max_at % 2 != 0 or self.system == "cubic") and elem["name"] in ["D4h", "D4d"]:
                        continue
                    if self.max_at % 5 != 0 and elem["name"] in ["D5h"]:
                        continue
                    # if self.max_at % 3 !=0 and elem['name'] in ['D6h','D6d']:
                    #   continue
                    if self.max_at % 7 != 0 and elem["name"] in [
                        "D7h",
                        "D7d",
                    ]:  # these are not very useful most of the time
                        continue
                    sym_dict.append(elem)
                elif mode != "cluster" and elem["number_max"] >= number_max:
                    sym_dict.append(elem)
                    if return_all is False:
                        number_max = elem["number_max"]
        if len(sym_dict) == 1:
            return sym_dict[0]
        chosen = np.random.randint(0, len(sym_dict))
        if return_all == False:
            sym_dict = sym_dict[chosen]
        return sym_dict

    def determine_plane_group(self, pos, cutoff=0.5):
        # the number of atoms is supposed to remain constant by operations
        sym = self.select_group(return_all=True)
        final_group = None
        for group in sym:
            pos_to_compare = self.do_sym_operations(pos, group, cutoff=cutoff, merge=True, mic=True)
            if pos_to_compare.shape[0] <= pos.shape[0]:
                if final_group is None or final_group["number_max"] <= group["number_max"]:
                    final_group = group
                    break
        return final_group

    def get_clusters(self, pos, atomic_number):
        clustering = self.make_clustering(pos, atomic_number)
        Nclusters = np.max(clustering) + 1
        clusters = [[] for i in range(Nclusters)]

        for i, ci in enumerate(clustering):
            clusters[ci].append(i)
        return clusters

    def get_symmetrised_positions(self, pos, atomic_number=None):
        clusters = self.get_clusters(pos, atomic_number)

        Natoms = pos.shape[0]
        a = Atoms(
            numbers=[atomic_number] * Natoms,
            positions=pos,
            pbc=self.pbc,
            cell=self.cell,
        )
        dVec_Mat = a.get_all_distances(mic=True, vector=True)

        pos_symm_all = []
        for cluster in clusters:
            p0 = pos[cluster[0]]
            pos_cluster = np.array([p0 + dVec for dVec in dVec_Mat[cluster[0], cluster]])
            pos_symm = pos_cluster.mean(axis=0)
            pos_symm_all.append(pos_symm)
        pos_symm_all = np.array(pos_symm_all)

        return pos_symm_all

    def swap_some_points(self, candidate, environement, table_mult):
        # redo this part to switch
        not_sym = candidate.get_meta_information("non_sym")
        if not_sym is None:
            not_sym = []
        tabelem = environement.get_numbers()
        output = []
        for x in tabelem:
            if x not in output and x not in not_sym:
                output.append(x)
        tabelem = output
        elem = np.random.choice(tabelem)
        counter = 0
        for el in table_mult:
            if el <= 4:
                counter += 1
        if self.group["name"].__contains__("p") == True:
            if counter > 2:
                n = np.random.choice([2, 3])
            else:
                n = np.random.choice([1, 2])
        elif min(table_mult) >= 8:
            n = np.random.choice([1, 2])
        elif self.group["name"].__contains__("6") == True:
            n = np.random.choice([2, 3, 6])
        elif self.group["name"].__contains__("5") == True:
            n = np.random.choice([2, 5])
        elif counter > 2:
            n = np.random.choice(list(range(2, counter + 2)))
        else:
            n = np.random.choice([1, 2])
        print(n)
        # n=2
        tab_tofil, table_mult2 = self.get_two_mult_points(candidate, table_mult, atomic_number=elem, n=n)
        candi = Atoms(
            numbers=candidate.numbers[:],
            positions=candidate.positions[:],
            cell=candidate.cell,
            pbc=candidate.pbc,
        )
        candi = candidate.copy()
        del candi[tab_tofil]
        if tab_tofil is not None and len(tab_tofil) >= 1:
            pos, tb = self.fill_mult_point(
                candidate.positions[np.random.choice(tab_tofil)],
                force_number=len(tab_tofil),
                candidate=candi,
            )
            # print(str(pos) + ' ' +str(tb))
            if pos is None or pos.shape[0] != len(tab_tofil):
                return None, None
            else:
                for sugg in pos:
                    # candidate.extend(Atom(elem, sugg))
                    candi.extend(Atoms(numbers=[elem], positions=[sugg]))
                table_mult2 += tb
        else:
            return None, None
        if not self.check_dist_mic(candi, mic=True):
            # write("POSCAR", candi, format="vasp")
            print("check_dist mic")
            return None, None
        return candi, table_mult2

    def resymmetrize(
        self,
        a,
        group,
        table_mult,
        cutoff=0.5,
        keep_sym=True,
        indices_to_rattle=[],
        not_sym=[],
    ):
        """
        This function resymmetrize the structure according to the right group
        It is supposed to handle gaining or losing symmetry
        """

        template = a.get_template()
        resym = None
        self.group = group
        table = np.concatenate(([0], table_mult[:-1]))
        if self.group["name"].__contains__("p") == False:
            print("cluster")
            mode = "cluster"
        else:
            mode = "slab"
        for i in range(len(table)):
            if i > 0:
                table[i] = table[i] + table[i - 1]
        table += len(template)
        new_table_mult = []
        for j, ta in enumerate(table):
            new_t = table_mult[j]
            if a[ta].number in not_sym:
                newpos = np.array([a.positions[ta]])
            # elif keep_sym==False and resym is not None and new_t==group['number_max'] and ta not in indices_to_rattle:
            elif keep_sym == False and resym is not None and ta not in indices_to_rattle:
                dist = [0]
                k = 0
                while min(dist) < cutoff and k < new_t:
                    newpos = self.do_sym_operations(a.positions[ta + k], cutoff=cutoff, merge=False)
                    dist = cdist(resym[-new_t:], newpos)
                    dist = dist.flatten()
                    k += 1
            else:
                newpos = self.do_sym_operations(a.positions[ta], cutoff=cutoff, merge=False)
            if newpos.shape[0] > 1:
                newpos = self.del_duplicate_positions(
                    newpos,
                    cutoff=cutoff,
                    delete=True,
                    merge=True,
                    atomic_number=a[ta].number,
                )
            if new_t < group["number_max"]:
                # handle losing symmetry
                if newpos.shape[0] > table_mult[j]:
                    if mode == "cluster":
                        newpos = self.replace_on_point_cluster(newpos, table_mult[j])
                        if newpos is None:
                            print("fail replace " + str(table_mult[j]) + " " + str(group["name"]))
                            return None, None
                        newpos = self.do_sym_operations(newpos, cutoff=cutoff, merge=False)
                    if newpos.shape[0] > table_mult[j]:
                        print(
                            "problem1 of losing sym "
                            + " a.ppos  "
                            + str(a.positions[ta])
                            + " apr switch "
                            + str(group["name"])
                            + " taille "
                            + str(newpos.shape[0])
                            + " "
                            + str(table_mult[j])
                            + " "
                            + str(keep_sym)
                        )
                        newpos, new_t = self.fill_mult_point(a.positions[ta], force_number=table_mult[j])
                    if newpos is None:
                        print("check fill 1339")
                        return None, None
            if newpos.shape[0] < table_mult[j]:
                new_t = [newpos.shape[0]]
                # Handle gaining symmetry here
                if table_mult[j] % newpos.shape[0] != 0:
                    if self.cluster_center is None:
                        self.cluster_center = np.array([0, 0, 0])
                    # print('prob of gaining sym '+str(newpos[0]-self.cluster_center) + ' '+str(group['name'])+' taille '+str(newpos.shape[0]) + ' '+str(table_mult[j]) +' '+str(keep_sym))
                    # newpos=newpos[:int(table_mult[j]/2)]
                    new_mult, new_2 = self.fill_mult_point(newpos, force_number=table_mult[j])
                    new_t = []
                    newpos = None
                else:
                    new_mult, new_2 = self.fill_mult_point(newpos, force_number=table_mult[j] - newpos.shape[0])
                if new_mult is None:
                    new_mult, new_2 = self.fill_mult_point(newpos, force_number=table_mult[j])
                    new_t = []
                    newpos = None
                if new_mult is None:
                    print("check full 1357")
                    return None, None
                if newpos is None:
                    newpos = new_mult
                else:
                    newpos = np.vstack((newpos, new_mult))
                for n in new_2:
                    new_t.append(n)
                if newpos.shape[0] != table_mult[j]:
                    return None, None
            if resym is None:
                resym = newpos
            elif newpos is not None:
                resym = np.vstack((resym, newpos))
            try:
                new_table_mult.extend(new_t)
            except:
                new_table_mult.append(new_t)

        # new_table_mult=[x for xs in new_table_mult for x in xs]
        return resym, new_table_mult

    def merger(self, a, index, group, table_mult, cutoff=0.5, disp=None):
        """
        This function handles completing the cell corresponding to the right table of positions
        """
        template = a.get_template()
        newpos = None
        resym = None
        self.group = group
        mode = None
        if self.group["name"].__contains__("p") == False:
            mode = "cluster"
        table = np.concatenate(([0], table_mult[:-1]))

        for i in range(len(table)):
            if i > 0:
                table[i] = table[i] + table[i - 1]
        table += len(template)
        new_table_mult = []
        for j, ta in enumerate(table):
            ta = int(ta)
            if ta == index:
                num_to_return = table_mult[j]
                newpos = self.do_sym_operations(a.positions[ta], cutoff=cutoff, merge=False)
                if newpos.shape[0] > 1:
                    newpos = self.del_duplicate_positions(
                        newpos,
                        cutoff=cutoff,
                        delete=True,
                        merge=True,
                        atomic_number=a[ta].number,
                    )
                new_t = [newpos.shape[0]]
                if newpos.shape[0] > num_to_return:
                    if mode == "cluster":
                        newpos = self.replace_on_point_cluster(newpos, table_mult[j])
                        if newpos is None:
                            return None, None, None
                        newpos = self.do_sym_operations(newpos, cutoff=cutoff, merge=False)
                    else:
                        # print('check displacement ' + str(newpos[0]))
                        newpos, num = self.fill_mult_point(newpos, force_number=num_to_return)
                    if newpos is None:
                        return None, None, None
                    if newpos.shape[0] > num_to_return:
                        if self.cluster_center is None:
                            self.cluster_center = np.array([0, 0, 0])
                        # print('problem in merge' + str(group['name'])+ ' '+str(table_mult[j]) + ' '+str(newpos.shape[0])+' '+str(newpos[0]-self.cluster_center)+' '+str(disp))
                        newpos = newpos[: table_mult[j]]
                    break
                elif newpos.shape[0] < table_mult[j]:
                    new_mult, new_2 = self.fill_mult_point(newpos, force_number=table_mult[j] - newpos.shape[0])
                    if new_mult is None or newpos is None:
                        new_mult, new_2 = self.fill_mult_point(newpos, force_number=table_mult[j])
                        new_t = []
                        if new_mult is None:
                            return None, None, None
                        else:
                            newpos = new_mult
                    else:
                        newpos = np.vstack((newpos, new_mult))
                    for n in new_2:
                        new_t.append(n)
                    new_table_mult = table_mult[:j] + new_t
                    if len(table_mult[j + 1 :]) > 0:
                        new_table_mult = new_table_mult + table_mult[j + 1 :]
                    if sum(new_table_mult) != sum(table_mult):
                        return None, None, None
                    # return newpos[:num_to_return] , new_table_mult , new_t
                break
        if newpos is None:
            return None, None, None
        return newpos[:num_to_return], table_mult, new_t

    """
    def set_single_position(self, a, index, pos_new, index_avail):
        indices_symm = set(self.get_symmetry_equivalent_atoms(a, index))
        indices_rattle = list(indices_symm.intersection(set(index_avail)))
        #print('indices_rattle:', indices_symm, indices_rattle)

        pos_symm = self.get_symmetry_points(pos_new)
        Nsym = pos_symm.shape[0]
        if Nsym > len(indices_rattle):
            return None
        indices_use = indices_rattle[:Nsym]
        a.positions[indices_use] = pos_symm
        return indices_use
    """
