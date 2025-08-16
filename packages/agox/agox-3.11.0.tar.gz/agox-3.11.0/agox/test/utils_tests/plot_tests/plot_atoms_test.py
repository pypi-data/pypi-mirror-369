from typing import List

import ase.data.colors
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pytest
from ase.constraints import FixAtoms
from matplotlib.collections import PatchCollection
from matplotlib.path import Path

from agox.candidates import StandardCandidate
from agox.utils.plot.plot_atoms import plot_atoms
from agox.utils.plot.utils import plane_to_indices


@pytest.mark.parametrize("plane", ["xy", "xz", "yz"])
@pytest.mark.parametrize("repeat", [0, 1])
def test_plot_atoms(environment_and_dataset, plane, repeat):
    matplotlib.use("Agg")

    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    d0, d1, d2, kv = plane_to_indices(plane)

    sorted_numbers = structure.numbers[np.argsort(kv * structure.positions[:, d2])]

    fig, ax = plt.subplots()
    patch_collection = plot_atoms(ax, structure, plane=plane, repeat=repeat, repeat_patch_kwargs=dict(alpha=0.5))

    expected_repeat = repeat > 0 and structure.get_pbc()[[d0, d1]].sum() > 0

    assert isinstance(patch_collection, PatchCollection)

    assert len(ax.collections) == 1
    assert isinstance(ax.collections[0], PatchCollection)

    p: PatchCollection = ax.collections[0]

    paths: List[Path] = p.get_paths()

    pbc_dimensions = structure.get_pbc()[[d0, d1]].sum()
    expected_copies = (2 * repeat + 1) ** pbc_dimensions

    assert len(paths) == len(structure) * expected_copies

    colors = p.get_facecolor()[:, :3]
    alphas = p.get_facecolor()[:, 3]

    if not expected_repeat:
        np.testing.assert_allclose(colors[: len(structure)], ase.data.colors.jmol_colors[sorted_numbers])
        np.testing.assert_allclose(alphas[: len(structure)], 1)
    else:
        num_original = np.sum(np.isclose(alphas, 1))
        num_repeat = np.sum(np.isclose(alphas, 0.5))

        assert num_original == len(structure)
        assert num_repeat == len(structure) * (expected_copies - 1)

    ax_xmin, ax_xmax = ax.get_xlim()
    ax_ymin, ax_ymax = ax.get_ylim()

    struc_xmin, struc_ymin = structure.positions[:, [d0, d1]].min(axis=0)
    struc_xmax, struc_ymax = structure.positions[:, [d0, d1]].max(axis=0)
    struc_xspan = struc_xmax - struc_xmin
    struc_yspan = struc_ymax - struc_ymin

    assert struc_xmin - struc_xspan < ax_xmin <= struc_xmin
    assert struc_xmax + struc_xspan > ax_xmax >= struc_xmax
    assert struc_ymin - struc_yspan < ax_ymin <= struc_ymin
    assert struc_ymax + struc_yspan > ax_ymax >= struc_ymax

    plt.close(fig)


@pytest.mark.parametrize("plot_constraint", [False, True])
@pytest.mark.parametrize("repeat", [0, 1])
def test_plot_constraint(environment_and_dataset, plot_constraint, repeat):
    matplotlib.use("Agg")

    environment, dataset = environment_and_dataset
    template = environment.get_template()
    structure: StandardCandidate = dataset[0]

    # this part of the test should be changed if `FixAtoms` is more integrated
    # in the environment/candidate
    structure.set_constraint(FixAtoms(indices=range(len(template))))

    fig, ax = plt.subplots()
    patch_collection = plot_atoms(ax, structure, repeat=repeat, plot_constraint=plot_constraint)

    paths: List[Path] = patch_collection.get_paths()

    pbc_dimensions = structure.get_pbc()[[0, 1]].sum()
    expected_copies = (2 * repeat + 1) ** pbc_dimensions

    if plot_constraint:
        # one circle for every atom, one cross for every fixed atom
        expected_n_paths = expected_copies * (len(structure) + len(template))
    else:
        # one circle for every atom
        expected_n_paths = expected_copies * len(structure)

    assert len(paths) == expected_n_paths

    plt.close(fig)
