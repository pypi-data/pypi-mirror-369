import numpy as np
import pytest

from agox.analysis import SearchData
from agox.analysis.property import DescriptorProperty, ListPropertyData
from agox.models.descriptors import Fingerprint


@pytest.fixture(scope="module")
def descriptor(search_data: SearchData) -> Fingerprint:
    example_atoms = search_data.get_candidate(0, 0)
    descriptor = Fingerprint.from_atoms(example_atoms)
    return descriptor


@pytest.fixture(scope="module")
def desc_property_obj(descriptor: Fingerprint) -> DescriptorProperty:
    prop = DescriptorProperty(descriptor=descriptor)
    return prop


@pytest.fixture(scope="module")
def desc_property(search_data: SearchData, desc_property_obj: DescriptorProperty) -> ListPropertyData:
    return desc_property_obj.compute(search_data)


def test_desc_property_computes(desc_property: ListPropertyData) -> None:
    print(desc_property)


def test_desc_property_hasdata(desc_property: ListPropertyData) -> None:
    assert desc_property.data is not None


def test_desc_property_hasname(desc_property: ListPropertyData) -> None:
    assert desc_property.name is not None


def test_desc_property_hasshape(desc_property: ListPropertyData) -> None:
    assert desc_property.shape is not None


def test_desc_property_hasaxis(desc_property: ListPropertyData) -> None:
    assert desc_property.axis is not None


def test_desc_property_repr(desc_property: ListPropertyData) -> None:
    assert repr(desc_property) is not None


def test_desc_property_get_minimum(desc_property_obj: DescriptorProperty, search_data: SearchData) -> None:
    with pytest.raises(ValueError):
        desc_property_obj.get_minimum([search_data])


def test_desc_property_match(
    desc_property: DescriptorProperty, descriptor: Fingerprint, search_data: SearchData
) -> None:
    fingerprint = descriptor.get_features(search_data.get_candidate(0, 0))
    np.testing.assert_allclose(desc_property.data[0][0], fingerprint)


def test_desc_property_match_shape(desc_property: ListPropertyData) -> None:
    assert desc_property.shape == ("Restarts", "Indices [#]")
