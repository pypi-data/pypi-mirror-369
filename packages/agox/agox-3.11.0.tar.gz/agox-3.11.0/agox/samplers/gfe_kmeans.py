from .kmeans import KMeansSampler
from agox.utils.thermodynamics import (
    gibbs_free_energy,
    ThermodynamicsData,
)
import numpy as np
from sklearn.cluster import KMeans


class GFEKMeansSampler(KMeansSampler):
    name = "SamplerGFEKMeans"
    parameters = {}

    """
    Parameters
    ----------
    descriptor : agox.models.descriptor.ABC_descriptor.DescriptorBaseClass
        Descriptor object that inherits from DescriptorBaseClass.
    model : agox.models.model.ABC_model.ModelBaseClass
        Model object that inherits from ModelBaseClass.
    sample_size : int
        The number of sample members, or population size. 
    max_gfe : float
        The max Gibbs Free energy of formation difference, compared to the most stable structure, 
        for a structure to be considered for sampling.
    mix_stcs : bool
        Wether to preform kmeans on all of the stoichiometries together or for each stoichiometry separately, choosing the most stable one
    n_most_stable_stc : int
        If mix_stcs is False, consider for sampling n of the most stable stcs. if 0 considers all
    """

    def __init__(
        self,
        thermo_data=None,
        descriptor=None,
        model=None,
        sample_size=10,
        max_gfe=5,
        **kwargs,
    ):
        super().__init__(
            descriptor=descriptor,
            model=model,
            sample_size=sample_size,
            max_energy=max_gfe,
            **kwargs,
        )

        self.thermo_data = thermo_data

    def setup(self, all_finished_structures):
        """
        Setup up the KMeans Sampler.

        Parameters
        ----------
        all_finished_structures : list of ase.Atoms or agox.candidates.candidate.Candidate
        """

        # Check if there are any finished structures
        if len(all_finished_structures) < 1:
            self.sample = []
            return

        # Sort the structures according to gfe:
        structures, gfes = self.gfe_filter_structures(all_finished_structures)
        # Calculate features:
        X = self.get_features(structures)

        # Determine the number of clusters:
        n_clusters = 1 + min(self.sample_size - 1, int(np.floor(len(gfes) / 5)))

        # Perform KMeans clustering:
        kmeans = KMeans(
            n_clusters=n_clusters,
            init="k-means++",
            n_init=10,
            random_state=np.random.randint(0, 10e6),
        ).fit(X)
        labels = kmeans.labels_

        # For each cluster find the lowest energy member:
        sample_indices = self.select_from_clusters(gfes, n_clusters, labels)
        sample = [structures[i] for i in sample_indices]
        sample_features = [X[i] for i in sample_indices]
        cluster_centers = [kmeans.cluster_centers_[i] for i in labels[sample_indices]]

        # Sort the sample mmebers according to energy.
        # This is only important for the output.
        sample_energies = [gibbs_free_energy(candidate=t, thermo_data=self.thermo_data) for t in sample]
        sorting_indices = np.argsort(sample_energies)
        self.sample = [sample[i] for i in sorting_indices]
        self.sample_features = [sample_features[i] for i in sorting_indices]
        self.cluster_centers = [cluster_centers[i] for i in sorting_indices]
        # Print information about the sample:
        self.print_output(all_finished_structures)

    def gfe_filter_structures(self, all_structures):
        """
        Filter out structures with gfe higher than e_min + max_energy

        Parameters
        ----------
        all_structures : list of ase.Atoms or agox.candidates.candidate.Candidate

        Returns
        -------
        structures : list of ase.Atoms or agox.candidates.candidate.Candidate
            List of structures that are within the energy range.
        e : list of float
            List of energies of the structures.
        """
        # Get energies of all structures:
        gfe_all = np.array(
            [
                gibbs_free_energy(candidate=candidate, thermo_data=self.thermo_data)
                for candidate in all_structures
            ]
        )

        gfe_min = np.min(gfe_all)

        for i in range(5):
            filt = gfe_all <= gfe_min + self.max_energy * 2**i
            if np.sum(filt) >= 2 * self.sample_size:
                break
        else:
            filt = np.ones(len(gfe_all), dtype=bool)
            index_sort = np.argsort(gfe_all)
            filt[index_sort[2 * self.sample_size :]] = False

        # The final set of structures to consider:
        structures = [all_structures[i] for i in range(len(all_structures)) if filt[i]]
        e = gfe_all[filt]
        return structures, e

    def get_features(self, structures):
        features = np.array(
            [self.descriptor.get_features(s).sum(axis=0) for s in structures]
        )
        return features
