import numpy as np
from ase.data import atomic_numbers
from matscipy.neighbours import neighbour_list as msp_nl

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass


class ExponentialDensity(DescriptorBaseClass):
    name = "ExponentialDensity"
    descriptor_type = "local"

    def __init__(self, indices=None, lambs=[1], rc=10.0, **kwargs):
        super().__init__(**kwargs)
        self.species = sorted([atomic_numbers[i] for i in self.environment.get_species()])

        self.indices = indices
        self.lambs = np.array(lambs)
        self.rc = rc

        self.n_features = len(self.species) * len(self.lambs) + 1

    def create_features(self, atoms):
        F = np.zeros((len(atoms), self.n_features))

        periodic_structure = np.any(atoms.pbc)

        if self.indices is not None:
            indices = self.indices
        else:
            indices = range(len(atoms))

        if periodic_structure:
            i1, i2, S = msp_nl("ijS", atoms, self.rc)
            D = atoms.positions[i1] - atoms.positions[i2] - S.dot(atoms.cell)
            d = np.linalg.norm(D, axis=1)

        for i in indices:
            if periodic_structure:
                args = i1 == i
                ind = i2[args]
                distances = d[args]

            else:
                ind = [j for j in range(len(atoms)) if j != i]
                pos = atoms.positions[ind]
                distances = np.linalg.norm(atoms.positions[i] - pos, axis=1)

            for c, species in enumerate(self.species):
                filter = atoms.numbers[ind] == species
                dists = distances[filter].reshape(-1, 1)
                F[i, c * len(self.lambs) : (c + 1) * len(self.lambs)] = np.sum(
                    np.exp(-dists / self.lambs) * self.gc(dists) / self.lambs, axis=0
                )

        F[indices, -1] = atoms.get_atomic_numbers()[indices]
        #        F[:, -1] = atoms.get_atomic_numbers()
        return F

    def create_feature_gradient(self, atoms):
        derivatives = np.zeros((len(atoms), len(atoms), 3, self.n_features))

        periodic_structure = np.any(atoms.pbc)
        if periodic_structure:
            i1, i2, S = msp_nl("ijS", atoms, self.rc)
            D = atoms.positions[i1] - atoms.positions[i2] - S.dot(atoms.cell)
            d = np.linalg.norm(D, axis=1)

        if self.indices is not None:
            indices = self.indices
        else:
            indices = range(len(atoms))

        for i in range(len(atoms)):
            if periodic_structure:
                args = i1 == i
                ind = i2[args]
                relative_positions = D[args]
                distances = d[args]

            else:
                ind = [j for j in range(len(atoms)) if j != i]
                positions = atoms.positions[ind]
                relative_positions = atoms.positions[i] - positions
                distances = np.linalg.norm(relative_positions, axis=1)

            for c, species in enumerate(self.species):
                filter = atoms.numbers[ind] == species
                d_vecs = relative_positions[filter]
                dists = distances[filter].reshape(-1, 1)

                for e, lamb in enumerate(self.lambs):
                    scalar_vector = (
                        np.exp(-dists / lamb) * (-self.gc(dists) / lamb + self.dgc(dists)) / (dists * lamb) * d_vecs
                    )
                    derivatives[i, i, :, c * len(self.lambs) + e] += np.sum(scalar_vector, axis=0)

                    feature_index = len(self.lambs) * self.species.index(atoms[i].number) + e
                    filtered_indices = np.array(ind)[filter]
                    for k in range(len(filtered_indices)):
                        derivatives[filtered_indices[k], i, :, feature_index] += scalar_vector[k]

        return derivatives

    def gc(self, distances):
        filter = distances < self.rc
        values = np.zeros((len(distances), 1))
        values[filter] += 1 / 2 * np.cos(np.pi * distances[filter] / self.rc) + 1 / 2
        return values

    def dgc(self, distances):
        filter = distances < self.rc
        values = np.zeros((len(distances), 1))
        values[filter] = -1 / 2 * np.pi * np.sin(np.pi * distances[filter] / self.rc) / self.rc
        return values

    @classmethod
    def from_species(cls, species, **kwargs):
        from ase import Atoms

        from agox.environments import Environment

        environment = Environment(
            template=Atoms(""),
            symbols="".join(species),
            use_box_constraint=False,
            print_report=False,
        )
        return cls(environment=environment, **kwargs)

    def get_number_of_centers(self, atoms):
        return len(atoms)
