import numpy as np

from agox.generators.complementary_energy.attractor_methods.ABC_attractors import AttractorMethodBaseClass


class AttractorAnotherStructure(AttractorMethodBaseClass):
    """
    Method for picking attractors from another structure.

    Parameters
    -----------
    descriptor: Local descriptor
        Used to calculate local features
    possible_number_of_attractors: int or list with two ints
        If int, then that exact amount of attractors will be created. If a list,
        the number of attractors will be a random number between the two given numbers
    attractors_from_template: Bool
        Whether attractors can be picked as feature vectors of template atoms
    predefined_attractors: List of attractors
        If not None, the specified attractors will be given to the CE generator
    order: int
        When to update the structures by checking the database
    """

    name = "AttractorAnotherStructure"

    def __init__(
        self,
        descriptor,
        possible_number_of_attractors=[3, 6],
        attractors_from_template=True,
        predefined_attractors=None,
        order=5,
    ):
        super().__init__(order=order)
        self.descriptor = descriptor
        self.possible_number_of_attractors = possible_number_of_attractors
        self.attractors_from_template = attractors_from_template
        self.predefined_attractors = predefined_attractors

    def get_attractors(self, structure):
        if self.predefined_attractors is not None:
            return self.predefined_attractors

        template = structure.get_template()
        n_template = len(template)

        if isinstance(self.possible_number_of_attractors, int):
            number_of_attractors = self.possible_number_of_attractors
        else:
            number_of_attractors = np.random.randint(
                self.possible_number_of_attractors[0], self.possible_number_of_attractors[1]
            )

        database_structure_index = np.random.randint(len(self.structures))

        structure_from_database = self.structures[database_structure_index]

        features = self.descriptor.get_features(structure_from_database)
        if not self.attractors_from_template:
            features = features[n_template:]

        attractor_indices = np.random.choice(range(len(features)), size=number_of_attractors, replace=False)

        attractors = features[attractor_indices]

        return attractors
