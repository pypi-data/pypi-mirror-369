import numpy as np

from agox.postprocessors.disjoint_filtering import DisjointFilteringPostprocess


def test_disjoint_filtering(environment_and_dataset):
    environment, dataset = environment_and_dataset

    # the dataset includes some structures that would be disjoint by default,
    # so we increase the default scale factor
    postprocessor = DisjointFilteringPostprocess(graph_kwargs=dict(scale_factor=1.6))

    filtered = postprocessor.process_list(dataset)

    assert filtered.count(None) == 0

    # manually make a disjoint version of all structures in the dataset
    for candidate in dataset:
        candidate = candidate.copy()
        candidate.set_pbc(False)
        rattle_idx = np.argmax(candidate.positions[:, 2])
        candidate.positions[rattle_idx, 2] += 5
        assert postprocessor.postprocess(candidate) is None
