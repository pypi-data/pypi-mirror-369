import numpy as np
from ase.io import write
from scipy.spatial.distance import cdist
from sklearn.cluster import KMeans

from agox.utils.filters.kmeans_energy import KMeansEnergyFilter

from .ABC_sampler import SamplerBaseClass


class KMeansSampler(SamplerBaseClass):
    """
    KMeans Sampler for selecting candidates based on a KMeans clustering algorithm.

    Parameters
    ----------
    descriptor : agox.models.descriptor.ABC_descriptor.DescriptorBaseClass
        Descriptor to use for the similarity criterion.
    model : agox.models.model.ABC_model.ModelBaseClass
        Model to use for the similarity criterion.
    sample_size : int
        The number of sample members, or population size.
    max_energy : float
        The maximum energy difference, compared to the lowest energy structure,
        for a structure to be considered for sampling.
    """

    name = "SamplerKMeans"
    parameters = {}

    def __init__(self, descriptor=None, model=None, sample_size=10, max_energy=5, **kwargs):
        super().__init__(**kwargs)
        self.descriptor = descriptor
        self.sample_size = sample_size
        self.max_energy = max_energy
        self.sample = []
        self.sample_features = []
        self.model = model
        self.debug = False

        energy_filter = KMeansEnergyFilter(sample_size=sample_size, max_energy=max_energy)
        if self.filters is None:
            self.filters = energy_filter
        else:
            from agox.utils.filters import SumFilter

            self.filters = SumFilter(f0=self.filters, f1=energy_filter)

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
            return False

        # Sort the structures according to energy:
        energies = np.array([s.get_potential_energy() for s in all_finished_structures])

        # Calculate features:
        X = self.get_features(all_finished_structures)

        # Determine the number of clusters:
        # TODO: Why is this necessary?
        n_clusters = 1 + min(self.sample_size - 1, int(np.floor(len(energies) / 5)))

        # Perform KMeans clustering:
        kmeans = KMeans(
            n_clusters=n_clusters, init="k-means++", n_init=10, random_state=np.random.randint(0, 10e6)
        ).fit(X)
        labels = kmeans.labels_

        # For each cluster find the lowest energy member:
        sample_indices = self.select_from_clusters(energies, n_clusters, labels)
        sample = [all_finished_structures[i] for i in sample_indices]
        sample_features = [X[i] for i in sample_indices]
        cluster_centers = [kmeans.cluster_centers_[i] for i in labels[sample_indices]]

        # Sort the sample mmebers according to energy.
        # This is only important for the output.
        sample_energies = [t.get_potential_energy() for t in sample]
        sorting_indices = np.argsort(sample_energies)
        self.sample = [sample[i] for i in sorting_indices]
        self.sample_features = [sample_features[i] for i in sorting_indices]
        self.cluster_centers = [cluster_centers[i] for i in sorting_indices]

        # Print information about the sample:
        self.print_output(all_finished_structures)

        return True

    def select_from_clusters(self, energies, n_clusters, labels):
        """
        Select the lowest energy member from each cluster.

        Parameters
        ----------
        energies : list of float
            List of energies of the structures.
        n_clusters : int
            Number of clusters.
        labels : list of int
            List of cluster labels for each structure.

        Returns
        -------
        sample_indices : list of int
            List of indices of the lowest energy member of each cluster.
        """
        indices = np.arange(len(energies))
        sample_indices = []
        for n in range(n_clusters):
            filt_cluster = labels == n
            cluster_indices = indices[filt_cluster]
            if len(cluster_indices) == 0:
                continue
            min_e_index = np.argmin(energies[filt_cluster])
            index_best_in_cluster = cluster_indices[min_e_index]
            sample_indices.append(index_best_in_cluster)
        return sample_indices

    def get_label(self, candidate):
        """
        Get the label of a candidate.

        Parameters
        ----------
        candidate : ase.Atoms or agox.candidates.candidate.Candidate
            Object to get the label of.

        Returns
        -------
        label : int
            The label of the candidate.
        """

        if len(self.sample) == 0:
            return None

        # find out what cluster we belong to
        f_this = np.array(self.descriptor.get_global_features([candidate]))
        distances = cdist(f_this, self.cluster_centers, metric="euclidean").reshape(-1)

        label = int(np.argmin(distances))
        return label

    def get_closest_sample_member(self, candidate):
        """
        Get the sample member that the candidate belongs to.

        Parameters
        ----------
        """
        label = self.get_label(candidate)
        cluster_center = self.sample[label]
        return cluster_center

    def get_features(self, structures):
        features = np.array(self.descriptor.get_features(structures)).sum(axis=1)
        return features

    def print_output(self, all_finished_structures):
        sample_energies = [t.get_potential_energy() for t in self.sample]
        for i, sample_energy in enumerate(sample_energies):
            self.writer(f"{i}: Sample energy {sample_energy:8.3f}")

        if self.model is not None and self.model.ready_state:
            for s in self.sample:
                t = s.copy()
                t.set_calculator(self.model)
                E = t.get_potential_energy()
                sigma = self.model.get_property("uncertainty")
                s.add_meta_information("model_energy", E)
                s.add_meta_information("uncertainty", sigma)
            self.writer(
                "SAMPLE_MODEL_ENERGY",
                "[",
                ",".join(["{:8.3f}".format(t.get_meta_information("model_energy")) for t in self.sample]),
                "]",
            )
            self.writer(
                "SAMPLE_MODEL_SIGMA",
                "[",
                ",".join(["{:8.3f}".format(t.get_meta_information("uncertainty")) for t in self.sample]),
                "]",
            )

        if self.debug:
            write(
                f"filtered_strucs_iteration_{self.get_iteration_counter()}.traj",
                all_finished_structures,
            )
            write(f"sample_iteration_{self.get_iteration_counter()}.traj", self.sample)

    @property
    def initialized(self):
        return len(self) > 0
