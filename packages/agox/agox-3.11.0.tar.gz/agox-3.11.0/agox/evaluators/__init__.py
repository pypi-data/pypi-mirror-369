"""
Evaluators are responsible for evaluating the objective function of a candidate.
The main two flavours of evaluators are single-point and local optimization.

Single-point evaluators evaluate the objective function at a single point,
whereas local optimization evaluators perform a local optimization starting from
the candidate's coordinates.
"""
# ruff: noqa: I001, E402
from typing import TypeAlias
from .ABC_evaluator import EvaluatorBaseClass
Evaluator: TypeAlias = EvaluatorBaseClass

from .local_optimization import LocalOptimizationEvaluator
from .rattle import RattleEvaluator
from .single_point import SinglePointEvaluator

__all__ = [
    "EvaluatorBaseClass",
    "Evaluator",
    "SinglePointEvaluator", 
    "LocalOptimizationEvaluator", 
    "RattleEvaluator"
    ]
