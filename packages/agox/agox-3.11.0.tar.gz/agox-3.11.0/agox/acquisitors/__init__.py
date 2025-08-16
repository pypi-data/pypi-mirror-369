r"""
Acquisitors are used to select the next candidate to evaluate among a number of
candidates, usually by sorting according to some metric.
The concept of acquisitors comes from Bayesian search algorithms.

A common acquisitor is the Lower Confidence Bound (LCB) acquisitor, which
selects according to the expression

.. math::
    LCB(x) = E(x) - \kappa \sigma(x).

Where E(x) is a prediction of the objective function at x, and :math:`\sigma(x)`
is the uncertainty of the prediction. :math:`\kappa` is a parameter that
controls the trade-off between exploration and exploitation.
This lets an algorithm choose which candidates to evaluate, but
does require the generation of multiple candidates to choose from.
"""
# ruff: noqa: I001, E402
from typing import TypeAlias
from .ABC_acquisitor import AcquisitonCalculatorBaseClass, AcquisitorBaseClass
Acquisitor: TypeAlias = AcquisitorBaseClass

from .LCB import LowerConfidenceBoundAcquisitor
from .LCB_penalty import LCBPenaltyAcquisitor
from .LCB_power import PowerLowerConfidenceBoundAcquisitor
from .GFE_aquisitor import GibbsFreeEnergyAquisitor
from .meta_acquisitor import MetaInformationAcquisitor
from .replica_exchange.default import ReplicaExchangeAcquisitor

__all__ = [
    "AcquisitorBaseClass",
    "Acquisitor",
    "LowerConfidenceBoundAcquisitor",
    "LCBPenaltyAcquisitor",
    "PowerLowerConfidenceBoundAcquisitor",
    "AcquisitonCalculatorBaseClass",
    "MetaInformationAcquisitor",
    'GibbsFreeEnergyAquisitor',
    "ReplicaExchangeAcquisitor",
]
