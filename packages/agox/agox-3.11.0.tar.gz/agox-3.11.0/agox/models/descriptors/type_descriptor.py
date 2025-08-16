import numpy as np

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass


class TypeDescriptor(DescriptorBaseClass):
    descriptor_type = "local"
    name = "TypeDescriptor"

    def __init__(self, environment, **kwargs):
        super().__init__(environment=environment, **kwargs)
        self.unique_numbers = np.unique(environment.get_all_numbers())

    def get_number_of_centers(self, atoms):
        return len(atoms)

    def create_features(self, atoms):
        x = np.zeros((len(atoms), len(self.unique_numbers)))
        for atom in atoms:
            x[atom.index, np.where(self.unique_numbers == atom.number)[0][0]] = 1
        return x

    def create_feature_gradient(self, atoms):
        n = len(atoms)
        return np.zeros_like(n, n, 3, len(self.unique_numbers))

    @classmethod
    def from_species(cls, species, **kwargs):
        """
        Create a SOAP descriptor from a list of species.

        Parameters
        ----------
        species : list
            List of species.
        **kwargs : dict
            Keyword arguments for the SOAP descriptor.
        """
        from ase import Atoms

        from agox.environments import Environment

        environment = Environment(
            template=Atoms(""),
            symbols="".join(species),
            use_box_constraint=False,
            print_report=False,
        )
        return cls(environment=environment, **kwargs)
