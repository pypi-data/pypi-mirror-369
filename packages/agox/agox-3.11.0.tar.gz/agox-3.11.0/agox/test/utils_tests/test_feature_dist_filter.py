import pytest
from ase.io import read

from agox.models.descriptors.spectral_graph_descriptor import SpectralGraphDescriptor
from agox.test.test_utils import test_data_dicts
from agox.utils.filters.feature_distance import FeatureDistanceFilter


@pytest.mark.ray
@pytest.mark.parametrize("test_data_dict", test_data_dicts)
def test_feature_distance_filter(test_data_dict):
    path = test_data_dict["path"]

    # Load structures from directory
    all_structures = read(path, ":")

    # Setup a descriptor
    descriptor = SpectralGraphDescriptor.from_atoms(all_structures[0])

    # Setup a filter, structures closer than threshold are considered duplicates
    threshold = 1e-8
    feature_filter = FeatureDistanceFilter(descriptor, threshold)

    # Filter the structures
    filtered_structures, filtered_indices = feature_filter.filter(all_structures)

    print("Before filtering: ", len(all_structures))
    print("After filtering: ", len(filtered_structures))
