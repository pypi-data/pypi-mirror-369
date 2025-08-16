"""
A candidate is the basic piece of data being moved around in the algorithm.
Generators create candidates, and evaluators evaluate the objective function
at the coordinates described by the candidate.
"""
# ruff: noqa: I001, E402
from typing import TypeAlias

from agox.candidates.ABC_candidate import CandidateBaseClass
Candidate: TypeAlias = CandidateBaseClass

from agox.candidates.standard import StandardCandidate

__all__ = ["CandidateBaseClass", 
           "Candidate",
           "StandardCandidate"]
