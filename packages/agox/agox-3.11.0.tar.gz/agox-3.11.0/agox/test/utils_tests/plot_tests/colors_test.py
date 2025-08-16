import numpy as np
import pytest
from ase.data import atomic_numbers
from ase.data.colors import cpk_colors, jmol_colors
from matplotlib.colors import to_rgba, to_rgba_array

from agox.candidates import StandardCandidate
from agox.utils.plot.colors import Colors


@pytest.mark.parametrize("color_palette", [None, jmol_colors, cpk_colors])
def test_init(environment_and_dataset, color_palette):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure, color_palette)

    expected_color_palette = color_palette if color_palette is not None else jmol_colors

    np.testing.assert_allclose(colors.colors, to_rgba_array(expected_color_palette[structure.numbers]))


def test_get_indices(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure)

    assert isinstance(colors._get_indices(None), np.ndarray)
    assert isinstance(colors._get_indices(0), np.ndarray)
    assert isinstance(colors._get_indices([0, 1]), np.ndarray)
    assert isinstance(colors._get_indices(np.array([0, 1])), np.ndarray)

    np.testing.assert_array_equal(colors._get_indices(None), np.arange(len(structure)))
    np.testing.assert_array_equal(colors._get_indices(0), [0])
    np.testing.assert_array_equal(colors._get_indices([0, 1]), [0, 1])
    np.testing.assert_array_equal(colors._get_indices(np.array([0, 1])), [0, 1])


# examples from https://matplotlib.org/stable/users/explain/colors/colors.html
@pytest.mark.parametrize(
    "color",
    [
        (0.1, 0.2, 0.5),
        (0.1, 0.2, 0.5, 0.3),
        "#0f0f0f",
        "#abc",
        "0.8",
        "b",
        "aquamarine",
        "xkcd:sky blue",
        "tab:blue",
        "C0",
    ],
)
def test_set_color(environment_and_dataset, color):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure)
    colors.set_color(color)

    expected_color = to_rgba(color)

    for color in colors.colors:
        np.testing.assert_array_equal(color, expected_color)


def test_set_alpha(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure)
    colors.set_alpha(0.5)

    np.testing.assert_array_equal(colors.colors[:, 3], 0.5)


def test_set_element(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    one_species = sorted(structure.symbols.species())[0]

    # using symbol input
    colors = Colors(structure)
    colors.set_element(one_species, "r")

    for atom, color in zip(structure, colors):
        expected_color = to_rgba("r" if atom.symbol == one_species else jmol_colors[atom.number])
        np.testing.assert_array_equal(color, expected_color)

    # using number input
    colors = Colors(structure)
    colors.set_element(atomic_numbers[one_species], "r")

    for atom, color in zip(structure, colors):
        expected_color = to_rgba("r" if atom.symbol == one_species else jmol_colors[atom.number])
        np.testing.assert_array_equal(color, expected_color)


def test_set_template(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure)
    colors.set_template("w")

    for i, (atom, color) in enumerate(zip(structure, colors)):
        expected_color = to_rgba("w" if i in structure.template_indices else jmol_colors[atom.number])
        np.testing.assert_array_equal(color, expected_color)


def test_darken_constant(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure)
    colors.darken(factor=0.1)

    base_colors = to_rgba_array(jmol_colors[structure.numbers])
    assert np.all(colors.colors <= base_colors)


def test_darken_threshold(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    threshold = 0.5 * structure.cell[2, 2]

    colors = Colors(structure)
    colors.darken(factor=0.1, threshold=threshold)

    for atom, color in zip(structure, colors):
        base_color = to_rgba(jmol_colors[atom.number])
        expected_darker = atom.position[2] > threshold

        if expected_darker:
            assert np.all(color <= base_color)
        else:
            np.testing.assert_allclose(color, base_color)


def test_lighten_constant(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    colors = Colors(structure)
    colors.lighten(factor=0.1)

    base_colors = to_rgba_array(jmol_colors[structure.numbers])
    assert np.all(colors.colors >= base_colors)


def test_lighten_threshold(environment_and_dataset):
    _, dataset = environment_and_dataset
    structure: StandardCandidate = dataset[0]

    threshold = 0.5 * structure.cell[2, 2]

    colors = Colors(structure)
    colors.lighten(factor=0.1, threshold=threshold)

    for atom, color in zip(structure, colors):
        base_color = to_rgba(jmol_colors[atom.number])
        expected_lighter = atom.position[2] > threshold

        if expected_lighter:
            assert np.all(color >= base_color)
        else:
            np.testing.assert_allclose(color, base_color)
