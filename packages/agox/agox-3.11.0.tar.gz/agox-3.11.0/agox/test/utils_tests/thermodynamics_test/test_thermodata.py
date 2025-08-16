from typing import Union, Tuple, List
from pathlib import Path

import pytest

from agox.utils.thermodynamics import ThermodynamicsData


@pytest.mark.parametrize('element', ['Cu', 29])
def test_thermodata_get_copper(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    assert thermo_data.get_chemical_potential(element) == -1.0

@pytest.mark.parametrize('element', ['O', 8])
def test_thermodata_get_oxygen(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    assert thermo_data.get_chemical_potential(element) == -2.0

@pytest.mark.parametrize('element', ['O', 8])
def test_thermodata_set_oxygen(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    thermo_data.set_chemical_potential(element, -3.0)
    assert thermo_data.get_chemical_potential('O') == -3.0
    thermo_data.set_chemical_potential(element, -2.0)
    assert thermo_data.get_chemical_potential('O') == -2.0

@pytest.mark.parametrize('element', ['Cu', 29])
def test_thermodata_set_copper(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    thermo_data.set_chemical_potential(element, -3.0)
    assert thermo_data.get_chemical_potential('Cu') == -3.0
    thermo_data.set_chemical_potential(element, -1.0)
    assert thermo_data.get_chemical_potential('Cu') == -1.0

@pytest.mark.parametrize('element', ['Al', 13])
def test_thermodata_get_aluminium(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    with pytest.raises(KeyError):
        thermo_data.get_chemical_potential(element)

@pytest.mark.parametrize('element', ['Cu', 29])
def test_thermodata_get_ref_copper(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    thermo_data.get_reference(element) == -1.0

@pytest.mark.parametrize('element', ['O', 8])
def test_thermodata_get_ref_oxygen(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    thermo_data.get_reference(element) == -2.0

@pytest.mark.parametrize('element', ['O', 8])
def test_thermodata_set_ref_oxygen(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    thermo_data.set_reference(element, -3.0)
    assert thermo_data.get_reference('O') == -3.0
    thermo_data.set_reference(element, -2.0)
    assert thermo_data.get_reference('O') == -2.0

@pytest.mark.parametrize('element', ['Cu', 29])
def test_thermodata_set_ref_copper(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    thermo_data.set_reference(element, -3.0)
    assert thermo_data.get_reference('Cu') == -3.0
    thermo_data.set_reference(element, -1.0)
    assert thermo_data.get_reference('Cu') == -1.0

@pytest.mark.parametrize('element', ['Al', 13])
def test_thermodata_get_ref_aluminium(element: Union[str, int], thermo_data: ThermodynamicsData) -> None:
    with pytest.raises(KeyError):
        thermo_data.get_reference(element)

@pytest.mark.parametrize('element_result', ([29, 'Cu'], [8, 'O'], ['Cu', 'Cu'], ['O', 'O'], [13, 'Al'], ['Al', 'Al']))
def test_thermodata_convert_element(element_result: Tuple[List[Union[str, int]]], thermo_data: ThermodynamicsData) -> None:
    element = element_result[0]
    assert thermo_data.convert_number_to_element(element) == element_result[1]

def test_thermodata_template_energy(thermo_data: ThermodynamicsData) -> None:
    assert thermo_data.template_energy == -10.0

def test_thermodata_save(thermo_data: ThermodynamicsData, tmpdir: Path) -> None:
    thermo_data.save(tmpdir / 'thermo_data.json')
    thermo_data2 = ThermodynamicsData.load(tmpdir / 'thermo_data.json')

    assert thermo_data.references == thermo_data2.references
    assert thermo_data.chemical_potentials == thermo_data2.chemical_potentials
    assert thermo_data.template_energy == thermo_data2.template_energy

def test_thermodata_save_raise(thermo_data: ThermodynamicsData, tmpdir: Path) -> None:
    thermo_data.save(tmpdir / 'thermo_data.json')

    with pytest.raises(FileExistsError):
        thermo_data.save(tmpdir / 'thermo_data.json')

def test_thermodata_save_overwrite(thermo_data: ThermodynamicsData, tmpdir: Path) -> None:
    thermo_data.save(tmpdir / 'thermo_data.json')
    thermo_data.save(tmpdir / 'thermo_data.json', overwrite=True)




