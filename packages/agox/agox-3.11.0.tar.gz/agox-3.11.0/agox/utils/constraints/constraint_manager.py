from copy import deepcopy
from typing import List, Literal, Optional, Sequence, TypeAlias

try: 
    from typing import Self
except ImportError:
    Self: TypeAlias = "ConstraintManager"

import numpy as np
from ase.constraints import IndexedConstraint

from agox.candidates import CandidateBaseClass

Candidate: TypeAlias = CandidateBaseClass


class Constraint:
    """
    Type alias for ASE constraints.
    """


class ManagedConstraint:
    def __init__(
        self,
        constraint: Constraint,
        mode: Optional[Literal["all", "optimize", "template"]] = None,
        index: Optional[Sequence[int]] = None,
    ) -> None:
        """
        A wrapper around a constraint that manages the indices that the constraint is applied to.
        This helps for searches where candidates with a different number of atoms may be generated,
        as ASE's implementation of constraints don't take this into account.

        Parameters
        ----------

        constraint : Constraint
            The constraint to manage.
        index : Optional[Sequence[int]]
            The indices to apply the constraint to.
        mode : Optional[Literal["all", "optimize", "template"]]
            The mode in which to apply the constraint. If mode is not None, index is ignored.
            If mode is 'all' then the constraint is applied to all atoms.
            If mode is 'optimize' then the constraint is applied to the atoms that are being optimized.
            If mode is 'template' then the constraint is applied to the atoms that are in the template.

        """
        self.constraint = constraint
        self.index = index
        if mode in ["all", "optimize", "template"]:
            self.mode = mode
        else:
            self.mode = None
        self.is_index_constraint = isinstance(constraint, IndexedConstraint)

    def get(self, candidate: Candidate) -> Constraint:
        constraint = deepcopy(self.constraint)
        if self.is_index_constraint:
            index = self.get_index(candidate)
            constraint.index = index
        return constraint

    def get_index(self, candidate: Candidate) -> Sequence[int]:
        if self.mode is not None:
            index = self.get_index_from_mode(candidate)
        elif self.index is not None:
            index = self.index.copy()
        return index

    def get_index_from_mode(self, candidate: Candidate) -> Sequence[int]:
        if self.mode == "all":
            return np.arange(len(candidate))
        elif self.mode == "optimize":
            indices = candidate.get_optimize_indices()
            return indices
        elif self.mode == "template":
            indices = candidate.get_template_indices()
            return indices

    def __str__(self) -> str:
        string = f"ManagedConstraint({self.constraint.__class__.__name__})"
        if self.is_index_constraint:
            if self.index is not None:
                string += f" applied to {self.index}"
            elif self.mode is not None:
                string += f" applied to {self.mode}"
        return string


class ConstraintManager:
    def __init__(self) -> None:
        """
        A class to manage constraints for candidates.

        Effecitvely acts like a list of constraints, but with the ability to
        indicate the mode in which the constraint is applied.
        """
        self.constraints = []

    def add_constraint(
        self, constraint: Constraint, mode: Optional[Literal["all", "optimize", "template"]] = None
    ) -> None:
        if isinstance(constraint, IndexedConstraint):
            if mode is None:
                index = constraint.index.copy()
            else:
                index = None
            managed_constraint = ManagedConstraint(constraint, index=index, mode=mode)
        else:
            managed_constraint = ManagedConstraint(constraint)

        self.constraints.append(managed_constraint)

    def get_constraints(self, candidate: Candidate) -> List[Constraint]:
        constraints = []
        for managed_constraint in self.constraints:
            constraint = managed_constraint.get(candidate)
            constraints.append(constraint)
        return constraints

    def apply(self, candidate: Candidate) -> Candidate:
        constraints = self.get_constraints(candidate)
        candidate.set_constraint(constraints)
        return candidate

    def append(self, constraint: Candidate, mode: Optional[Literal["all", "optimize", "template"]] = None) -> None:
        self.add_constraint(constraint, mode)

    def __iter__(self) -> Self:
        self.iter_count = 0
        return self

    def __add__(self, other: Self) -> Self:
        new_manager = deepcopy(self)
        if isinstance(other, list):
            for constraint in other:
                new_manager.add_constraint(constraint)
        elif isinstance(other, ConstraintManager):
            for key, constraint in other.constraints.items():
                new_manager.add_constraint(constraint.constraint, constraint.index)

        return new_manager

    def _radd__(self, other: Self) -> Self:
        return self.__add__(other)

    def __next__(self) -> ManagedConstraint:
        if self.iter_count < len(self.constraints):
            constraint = self.constraints[self.iter_count]
            self.iter_count += 1
            return constraint
        else:
            raise StopIteration

    def __repr__(self) -> str:
        rep = """ConstraintManager:"""
        for constraint in self.constraints:
            rep += f"\n\t{constraint}"
        return rep
