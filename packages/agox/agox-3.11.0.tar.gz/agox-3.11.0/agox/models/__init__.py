"""
Models are used to predict the output of a given input. Generally this corresponds
to predicting the energy and forces of a given atomic configuration.

This module also contains the descriptors used to represent the atomic configurations.
"""
# ruff: noqa: I001, E402
from typing import TypeAlias
from .ABC_model import ModelBaseClass
Model: TypeAlias = ModelBaseClass

from agox.models.GPR import GPR, SparseGPR, SparseGPREnsemble
from agox.models.composition_model import CompositionModel
from agox.models.ase_model import CalculatorModel

__all__ = ['ModelBaseClass', 'Model', 'GPR', 'SparseGPR', 'SparseGPREnsemble', 'CompositionModel', 'CalculatorModel']

