import numpy as np

from agox.analysis import SearchData
from agox.analysis.property import ArrayPropertyData, EnergyProperty, FreeEnergyProperty
from agox.utils.thermodynamics.thermodynamics_data import ThermodynamicsData


def free_energy_property() -> FreeEnergyProperty:
    """
    Todo: Not working yet, need to fix it on the GC branch.
    """
    references = {"Ni": 0, "Au": 0}
    chemical_potentials = {"Ni": 0, "Au": 0}

    thermo_data = ThermodynamicsData(references=references, chemical_potentials=chemical_potentials)
    prop = FreeEnergyProperty(thermo_data=thermo_data)
    return prop


def test_energy_property_computes(energy_array_prop: ArrayPropertyData) -> None:
    print(energy_array_prop)


def test_energy_property_hasdata(energy_array_prop: ArrayPropertyData) -> None:
    assert energy_array_prop.data is not None


def test_energy_property_data_nparray(energy_array_prop: ArrayPropertyData) -> None:
    assert isinstance(energy_array_prop.data, np.ndarray)


def test_energy_property_shape(energy_array_prop: ArrayPropertyData) -> None:
    assert energy_array_prop.shape[0] == "Restarts"
    assert energy_array_prop.shape[1] in ["Iterations [#]", "Indices [#]"]


def test_energy_property_axis(energy_array_prop: ArrayPropertyData) -> None:
    assert isinstance(energy_array_prop.axis, tuple)
    assert isinstance(energy_array_prop.axis[0], list)
    assert isinstance(energy_array_prop.axis[1], np.ndarray)


def test_energy_property_name(energy_array_prop: ArrayPropertyData) -> None:
    assert hasattr(energy_array_prop, "name")


def test_energy_property_minimum(energy_array_prop: ArrayPropertyData, search_data: SearchData) -> None:
    energy_property = EnergyProperty()
    min_energy = energy_property.get_minimum([search_data])
    np.testing.assert_allclose(energy_array_prop.data.min(), min_energy)
