
import numpy as np
from ase.data import covalent_radii

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass


class Voronoi(DescriptorBaseClass):
    name = "Voronoi"
    descriptor_type = "global"

    """
    Voronoi graph descriptor.

    Parameters
    ----------
    indices : list
        List of indices of atoms to be considered.
        If None and template is None, all atoms are considered.
        If None and template is not None, all atoms except for template are considered.
    template : Atoms
        Template structure. If None, the first structure in the list of structures is used.
    covalent_bond_scale_factor : float  
        Scaling of covalent bond length to determine the cutoff radii.
    n_points : int
        Number of points sampled from circle on plane.
    angle_from_central_atom : float
        Angle from central atom to determine the points sampled from circle on plane.
    """

    def __init__(
        self,
        indices=None,
        template=None,
        covalent_bond_scale_factor=1.3,
        n_points=8,
        angle_from_central_atom=20,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.indices = indices
        self.template = template
        self.covalent_bond_scale_factor = covalent_bond_scale_factor
        self.n_points = n_points
        self.angle_from_central_atom = angle_from_central_atom

    def get_bond_matrix(self, candidate) -> np.ndarray:
        """
        Calculate the bond matrix for a candidate structure.

        Parameters
        ----------
        candidate : ase.Atoms
            Atoms object.

        Returns
        -------
        bond matrix: np.ndarray
            Array of shape [n_atoms, n_atoms]
        """
        candidate_copy = candidate.copy()
        candidate_copy.set_constraint()

        del candidate_copy[[i for i in range(len(candidate)) if i not in self.indices]]

        distance_vectors = candidate_copy.get_all_distances(mic=True, vector=True)
        distance_abs = np.linalg.norm(distance_vectors, axis=2)
        numbers = candidate_copy.get_atomic_numbers()
        r = [covalent_radii[number] for number in numbers]
        x, y = np.meshgrid(r, r)
        optimal_distances = x + y

        distances_rel = distance_abs / optimal_distances

        matrix = np.logical_and(distances_rel > 1e-3, distances_rel < self.covalent_bond_scale_factor).astype(int)
        matrix += np.diag(numbers)

        for i, (distances, vectors, position) in enumerate(
            zip(distance_abs, distance_vectors, candidate_copy.positions)
        ):
            planes = []

            args = np.argsort(distances)[1:]
            distances = np.expand_dims(distances, 1)
            distances = distances[args]
            normal_vectors = vectors[args] / distances
            points = 0.5 * distances * normal_vectors + position
            for j, normal_vector, point, distance in zip(args, normal_vectors, points, distances):
                if i != j and matrix[i, j] == 1:
                    if len(planes) == 0:
                        plane = Plane(normal_vector, point)
                        planes.append(plane)
                    else:
                        cuts = [plane.plane_cut(point) for plane in planes]
                        cuts = np.any(cuts)

                        plane = Plane(normal_vector, point)

                        if cuts:
                            matrix[i, j] = 0
                        elif self.n_points != 0 and self.angle_from_central_atom != 0:
                            points_in_plane = plane.points_in_plane(
                                self.n_points, 0.5 * distance, self.angle_from_central_atom
                            )
                            for p in points_in_plane:
                                cuts = [plane.plane_cut(p) for plane in planes]
                                cuts = np.any(cuts)
                                if cuts:
                                    matrix[i, j] = 0
                                    break

                        planes.append(plane)

        matrix = np.floor((matrix + matrix.T) / 2)

        return matrix

    def convert_matrix_to_eigen_value_string(self, matrix) -> str:
        """
        Convert the bond matrix to a string of sorted eigenvalues.

        Parameters
        ----------
        matrix : np.ndarray
            Bond matrix.

        Returns
        -------
        eigenvalue string : str
            String of sorted eigenvalues.
        """
        w, _ = np.linalg.eig(matrix)
        w = np.real(w)
        w.sort()
        s = "[" + ",".join(["{:8.3f}".format(e) for e in w]) + "]"
        s = s.replace("-0.000", " 0.000")
        return s

    def create_features(self, t, allow_read_from_meta_information=False) -> str:
        """
        Calculate the Voronoi graph descriptor.

        Parameters
        ----------
        t : ase.Atoms
            Atoms object.
        allow_read_from_meta_information : bool
            Whether to allow reading the eigenvalue string from the meta information of the Atoms object.

        Returns
        -------
        eigenvalue string : str
            String of sorted eigenvalues.
        """

        # this is conditioned that the meta information is trusted (corrupted when Candidates are copied and changed)
        if allow_read_from_meta_information:
            if t.has_meta_information("eigen_string"):
                return t.get_meta_information("eigen_string")

        if self.indices is None and self.template is not None:
            self.indices = list(range(len(self.template), len(t)))
            print("SETTING INDICES:", self.indices)
        elif self.indices is None and self.template is None:
            self.indices = list(range(len(t)))

        m = self.get_bond_matrix(t)

        s = self.convert_matrix_to_eigen_value_string(m)
        try:
            t.add_meta_information("eigen_string", s)
        except:
            pass

        return s

    def get_number_of_centers(self, atoms):
        """
        Get the number of eigenvalues for Voronoi graph descriptor.

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object.

        Returns
        -------
        n_centers : int
            Number of eigenvalues.
        """
        return len(atoms)


class Plane:
    """
    Class for constructing planes to determine whether or not two atoms
    are bound to each other.

    Parameters:
    ------------
    nvec: Numpy array
        Normal vector of the plane
    p0: Numpy array
        Point in the plane
    """

    def __init__(self, nvec, p0):
        self.nvec = nvec
        self.p0 = p0

    def plane_cut(self, p) -> bool:
        """
        Determine whether a point is cut by the plane or not.

        Parameters
        ----------
        p : Numpy array
            Point to be checked.

        Returns
        -------
        cut : bool
            Whether the point is cut by the plane (True) or not (False).
        """
        return np.sum(self.nvec * (p - self.p0)) > 0

    def points_in_plane(self, n_points, distance_from_atom_to_p0=1, angle_from_central_atom=10) -> list:
        """
        Generate points on the circle on the plane.

        Parameters
        ----------
        n_points : int
            Number of points to be generated.
        distance_from_atom_to_p0 : float
            Distance from atom to the point p0.
        angle_from_central_atom : float
            Angle from central atom to determine the points sampled from circle on plane.

        Returns
        -------
        points : list
            List of points on the circle on the plane.
        """

        index1 = np.argmax(np.abs(self.nvec))
        if index1 != 0:
            index2 = 0
        else:
            index2 = 1

        p1 = np.zeros(3)
        p1[index2] = 1
        p1[index1] = -self.nvec[index2] / self.nvec[index1]

        p1 /= np.linalg.norm(p1)
        p2 = np.cross(self.nvec, p1)

        angle = 2 * np.pi / n_points

        points = []
        for i in range(n_points):
            p = np.cos(angle * i) * p1 + np.sin(angle * i) * p2
            p *= distance_from_atom_to_p0 * np.tan(np.deg2rad(angle_from_central_atom))
            p += self.p0
            points.append(p)

        return points
