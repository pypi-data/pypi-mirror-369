from abc import ABC, abstractmethod

import numpy as np

from agox.candidates.ABC_candidate import CandidateBaseClass
from agox.module import Module
from agox.utils import candidate_list_comprehension


class DescriptorBaseClass(ABC, Module):
    def __init__(self, environment, surname="", use_cache=True):
        Module.__init__(self, surname=surname, use_cache=use_cache)
        self.environment = environment

        assert self.descriptor_type in ["global", "local"], 'Descriptor type must be either "global" or "local".'

    ##########################################################################################################
    # Create methods - Implemented by classes that inherit from this base-class.
    # Not called directly by methods of other classes.
    ##########################################################################################################

    @property
    @abstractmethod
    def descriptor_type(self):
        """
        Returns
        -------
        str
            The type of descriptor either 'global' or 'local'.
            Generally this refers to the n_centers dimension of calculated features,
            which is 1 for global descriptors and typically (but not required) n_atoms for local features.
        """
        pass

    @property
    @abstractmethod
    def get_number_of_centers(self, atoms):
        """
        Returns
        -------
        int
            The number of centers that the descriptor will be calculated for.
            This is the n_centers dimension of the calculated features.
        """
        pass

    def create_features(self, atoms):
        """
        Method to implement on child classes that does the calculation
        of feature vectors.

        This method should not (generally) deal with being given a list of
        Atoms objects.

        Parameters
        ----------
        atoms : Atoms object

        Returns
        --------
        Features of shape [n_centers, n_features]
        """
        pass

    def create_feature_gradient(self, atoms):
        """
        Method to implement on child classes that does the calculation
        of feature gradients.

        This method should not (generally) deal with being given a list of
        Atoms objects.

        Parameters
        ----------
        atoms : Atoms object

        Returns
        --------
        Feature gradients of shape [n_centers, n_atoms, 3, n_features]
        """
        return self.central_difference_gradient(atoms)

    ##########################################################################################################
    # Get methods - Ones to use in other scripts.
    ##########################################################################################################

    @candidate_list_comprehension
    @CandidateBaseClass.cache("features")
    def get_features(self, atoms):
        """
        Method to get global features.

        Parameters
        ----------
        atoms : Atoms object or list or Atoms objects.
            Atoms to calculate features for.

        Returns
        -------
        list
            Global features for the given atoms.
        """
        return self.create_features(atoms)

    @candidate_list_comprehension
    @CandidateBaseClass.cache("feature_gradient")
    def get_feature_gradient(self, atoms):
        """
        Method to get global features.

        Parameters
        ----------
        atoms : Atoms object or list or Atoms objects.
            Atoms to calculate features for.

        Returns
        -------
        list
            Global feature gradients for the given atoms.
        """
        return self.create_feature_gradient(atoms)

    @Module.reset_cache_key
    def change_descriptor_somehow(self):
        """
        This is not a real method.

        This is just to illustrate that if you use the caching capability of the
        descriptor-baseclass then you MUST use the @Module.reset_cache_key decorator
        on any function that changes the descriptor - e.g. changing parameters.
        """
        return

    def central_difference_gradient(self, atoms, delta=0.0001):
        """
        Calculate the gradient of the features using a central difference method.
        """

        f0 = self.get_features(atoms)
        dF_dx = np.zeros((f0.shape[0], len(atoms), 3, f0.shape[1]))

        for i in range(len(atoms)):
            for d in range(3):
                atoms.positions[i, d] -= delta
                fm = self.get_features(atoms)
                atoms.positions[i, d] += 2 * delta
                fp = self.get_features(atoms)
                atoms.positions[i, d] -= delta
                dF_dx[:, i, d, :] = (fp - fm) / (2 * delta)

        return dF_dx

    def __eq__(self, other):
        if not isinstance(other, DescriptorBaseClass):
            return False
        return self.cache_key == other.cache_key
