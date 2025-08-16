import numpy as np

from agox.analysis import SearchData
from agox.analysis.property import ArrayPropertyData, FreeEnergyProperty


def test_energy_property_computes(free_energy_array_prop: ArrayPropertyData) -> None:
    print(free_energy_array_prop)

def test_energy_property_hasdata(free_energy_array_prop: ArrayPropertyData) -> None:
    assert free_energy_array_prop.data is not None

def test_energy_property_data_nparray(free_energy_array_prop: ArrayPropertyData) -> None:
    assert isinstance(free_energy_array_prop.data, np.ndarray)

def test_energy_property_shape(free_energy_array_prop: ArrayPropertyData) -> None:
    assert free_energy_array_prop.shape == ('Restarts', 'Indices [#]') or free_energy_array_prop.shape == ('Restarts', 'Iterations [#]')

def test_energy_property_axis(free_energy_array_prop: ArrayPropertyData) -> None:
    assert isinstance(free_energy_array_prop.axis, tuple)
    assert isinstance(free_energy_array_prop.axis[0], list)
    assert isinstance(free_energy_array_prop.axis[1], np.ndarray)

def test_energy_property_name(free_energy_array_prop: ArrayPropertyData) -> None:
    assert hasattr(free_energy_array_prop, 'name')

def test_energy_property_minimum(free_energy_property: FreeEnergyProperty, free_energy_array_prop: ArrayPropertyData, search_data: SearchData) -> None:
    min_energy = free_energy_property.get_minimum([search_data])
    np.testing.assert_allclose(free_energy_array_prop.data.min(), min_energy)

