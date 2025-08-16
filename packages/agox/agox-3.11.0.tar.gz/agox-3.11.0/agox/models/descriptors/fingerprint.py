import numpy as np

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass
from agox.models.descriptors.fingerprint_cython.angular_fingerprintFeature_cy import Angular_Fingerprint


class Fingerprint(DescriptorBaseClass):
    name = "Fingerprint"
    descriptor_type = "global"

    """
    Fingerprint descriptor that calculates radial and angular distribution functions 
    for a given atoms object. 

    Parameters
    ----------
    rc1 : float
        Radial cutoff for the radial distribution function.
    rc2 : float
        Radial cutoff for the angular distribution function.
    binwidth : float
        Binwidth for the radial distribution function.
    Nbins : int
        Number of bins for the angular distribution function.
    sigma1 : float
        Width of the gaussian used for the radial distribution function.
    sigma2 : float
        Width of the gaussian used for the angular distribution function.
    gamma : float
        Parameter of the cutoff function. 
    eta : float
        Weighting factor for the angular distribution function. 
    """

    def __init__(
        self,
        rc1=6,
        rc2=4,
        binwidth=0.2,
        Nbins=30,
        sigma1=0.2,
        sigma2=0.2,
        gamma=2,
        eta=20,
        use_angular=True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.cython_module = Angular_Fingerprint(
            self.environment.get_atoms(),
            Rc1=rc1,
            Rc2=rc2,
            binwidth1=binwidth,
            Nbins2=Nbins,
            sigma1=sigma1,
            sigma2=sigma2,
            gamma=gamma,
            eta=eta,
            use_angular=use_angular,
        )

    def create_features(self, atoms) -> np.ndarray:
        """

        Calculate feature vector for an atoms object.

        Parameters
        ----------
        atoms : Atoms object

        Returns
        -------
        features : np.ndarray
        """
        return self.cython_module.get_feature(atoms).reshape(1, -1)

    def create_feature_gradient(self, atoms) -> np.ndarray:
        """
        Calculate derivative of features with respect to atomic positions for
        given atoms object.

        Parameters
        ----------
        atoms : Atoms object

        Returns
        -------
        feature_gradient : np.ndarray
        """
        return self.cython_module.get_featureGradient(atoms).reshape(1, len(atoms), 3, -1)

    def get_number_of_centers(self, atoms) -> int:
        """
        Get the number of centers for the given atoms object.
        Because this is a global descriptor, this is always 1.

        Parameters
        ----------
        atoms : Atoms object

        Returns
        -------
        int
            The number of centers that the descriptor will be calculated for.
            Always 1.
        """
        return 1

    @classmethod
    def from_atoms(cls, atoms, **kwargs):
        """
        Create a descriptor from an atoms object.

        Parameters
        ----------
        atoms : Atoms object
            The atoms object used to setup the descriptor.
        kwargs : dict
            Any keyword arguments to pass to the descriptor.
        """
        from agox.environments import Environment

        environment = Environment(template=atoms, symbols="", use_box_constraint=False, print_report=False)
        return cls(environment=environment, **kwargs)
