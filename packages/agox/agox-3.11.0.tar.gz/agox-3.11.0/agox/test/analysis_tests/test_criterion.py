import numpy as np
import pytest

from agox.analysis.criterion import DistanceCriterion, ThresholdCriterion
from agox.analysis.criterion.base_criterion.discrete_distribution import DiscreteDistribution
from agox.analysis.property import ArrayPropertyData


@pytest.fixture(scope="module")
def threshold_criterion() -> ThresholdCriterion:
    criterion = ThresholdCriterion(threshold=1)
    return criterion


@pytest.fixture(scope="module")
def threshold_output(
    threshold_criterion: ThresholdCriterion, energy_array_prop: ArrayPropertyData
) -> DiscreteDistribution:
    return threshold_criterion(energy_array_prop)


def test_threshold_criterion(threshold_output: DiscreteDistribution) -> None:
    assert threshold_output is not None


@pytest.fixture(scope="module")
def distance_criterion() -> DistanceCriterion:
    comparate = np.atleast_2d(np.array([1]))
    criterion = DistanceCriterion(threshold=0.1, comparate=comparate)
    return criterion


@pytest.fixture(scope="module")
def distance_output(
    distance_criterion: DistanceCriterion, energy_array_prop: ArrayPropertyData
) -> DiscreteDistribution:
    return distance_criterion(energy_array_prop)


def test_distance_criterion(distance_output: DiscreteDistribution) -> None:
    assert distance_output is not None
