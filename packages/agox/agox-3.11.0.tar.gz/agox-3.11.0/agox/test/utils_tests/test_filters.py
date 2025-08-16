from agox.utils.filters.random import RandomFilter


def test_random_filter(environment_and_dataset):
    environment, dataset = environment_and_dataset
    random_filter = RandomFilter(N=100)

    # Test that the filter works
    structures, indices = random_filter.filter(dataset)
    assert len(structures) == 100

    # Test that the filter works with N > len(dataset):
    random_filter = RandomFilter(N=len(dataset) * 2)
    structures, indices = random_filter.filter(dataset)

    assert len(structures) == len(dataset)
