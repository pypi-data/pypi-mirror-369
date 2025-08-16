
import numpy as np

from agox.models.descriptors.ABC_descriptor import DescriptorBaseClass


class SOAP(DescriptorBaseClass):
    name = "SOAP"
    descriptor_type = "local"

    """
    SOAP descriptor wrapper for DScribe.

    Parameters
    ----------
    r_cut : float
        Cutoff radius for the local environment.
    nmax : int
        Maximum number of radial basis functions.
    lmax : int
        Maximum degree of spherical harmonics.
    sigma : float
        Standard deviation of the gaussian used to expand the atomic density.
    weight : bool or dict
        If True, use polynomial weighting function. If False, use no weighting
        function. If dict, use custom weighting function.
    periodic : bool
        Whether to use periodic boundary conditions.
    dtype : str
        Data type of the output.
    crossover : bool
        Whether to use crossover compression.
    compression : dict
        Compression parameters. If None, crossover is used.
    """

    def __init__(
        self,
        r_cut=4,
        nmax=3,
        lmax=2,
        sigma=1.0,
        weight=True,
        periodic=True,
        dtype="float64",
        crossover=False,
        compression=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        from dscribe.descriptors import SOAP as dscribeSOAP

        self.r_cut = r_cut

        # Weighting function
        if weight is True:
            weighting = {"function": "poly", "r0": r_cut, "m": 2, "c": 1}
        elif weight is None:
            weighting = None
            method = "analytical"
        elif weight is False:
            weighting = None
            method = "analytical"
        else:
            weighting = weight

        # Compression / Crossover:
        if compression is None:
            assert type(crossover) == bool, "crossover must be bool"
            if crossover:
                compression = {"mode": "crossover"}
            else:
                compression = {"mode": "off"}
        elif type(compression) == dict:
            pass

        # Create dscribe SOAP descriptor object:
        self.soap = dscribeSOAP(
            species=self.environment.get_species(),
            periodic=periodic,
            r_cut=r_cut,
            n_max=nmax,
            l_max=lmax,
            sigma=sigma,
            weighting=weighting,
            dtype=dtype,
            compression=compression,
            sparse=False,
        )

        self.length = self.soap.get_number_of_features()

    def create_features(self, atoms) -> np.ndarray:
        """
        Calculate SOAP features.

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object.

        Returns
        -------
        features : np.ndarray
            Array of shape [n_centers, n_features]
        """
        return self.soap.create(atoms)

    def create_feature_gradient(self, atoms) -> np.ndarray:
        """
        Calculate the gradient of the SOAP features wrt. atomic coordinates.

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object.

        Returns
        -------
        feature gradient: np.ndarray
            Array of shape [n_centers, n_atoms, n_features, 3]
        """
        f_deriv = self.soap.derivatives(atoms, return_descriptor=False, attach=True, method="numerical")
        return f_deriv

    def get_number_of_centers(self, atoms):
        """
        Get the number of centers for the SOAP descriptor.

        Parameters
        ----------
        atoms : ase.Atoms
            Atoms object.

        Returns
        -------
        n_centers : int
            Number of centers.
        """
        return len(atoms)

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
