import numpy as np

from agox.models.descriptors import Fingerprint


def test_cache(environment_and_dataset):
    environment, dataset = environment_and_dataset

    descriptor = Fingerprint(environment=environment, use_cache=True)
    descriptor_no_cache = Fingerprint(environment=environment, use_cache=False)

    F_all_cache = descriptor.get_features(dataset)
    F_all_no_cache = descriptor_no_cache.get_features(dataset)

    np.testing.assert_allclose(F_all_cache, F_all_no_cache)

    # Use the cached descriptor again:
    F_all_cache_2 = descriptor.get_features(dataset)

    # Compare cached and non-cached:
    np.testing.assert_allclose(F_all_cache, F_all_cache_2)
