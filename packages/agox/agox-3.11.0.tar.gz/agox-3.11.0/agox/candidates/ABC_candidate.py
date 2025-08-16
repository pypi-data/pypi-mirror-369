import functools
from abc import ABC
from copy import deepcopy
from typing import Any, Callable, Tuple

import numpy as np
from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator

from agox.module import Module
from agox.utils.cache import Cache


class CandidateBaseClass(ABC, Atoms, Module):
    """
    Base-class for Candidate objects.

    Parameters
    ------------
    template: ase.Atoms
        Atoms object of the template structure. Does not need to be supplied
        if 'template_indices' are given.
    template_indices: np.array
        Indices of template atoms.
    kwargs:
        Everything that can be supplied to an ASE atoms object, specifically
        cell, positions and numbers of ALL atoms - including template atoms.
    """

    def __init__(
        self, template: Atoms = None, template_indices: np.ndarray = None, use_cache: bool = True, **kwargs
    ) -> None:
        Atoms.__init__(self, **kwargs)  # This means all Atoms-related stuff gets set.
        Module.__init__(self, use_cache=use_cache)
        self.meta_information = self.info

        self.use_cache = use_cache
        self._cache = Cache()

        # Template stuff:
        if template_indices is not None:
            self.template_indices = template_indices.astype(int)
            self.template = self.get_template()
        elif template is not None:
            self.template = template
            self.template_indices = np.arange(len(template))
        else:
            print("You have not supplied a template, using an empty atoms object without PBC and no specified cell.")
            self.template = Atoms(pbc=self.pbc)
            self.template_indices = np.arange(0)

        self.set_pbc(self.template.get_pbc())  # Inherit PBC's from template.

    @classmethod
    def cache(cls, key: str) -> Callable:  # noqa: ANN001
        def decorator(func):  # noqa: ANN001
            @functools.wraps(func)
            def wrapper(self, atoms: Atoms, *args, **kwargs):  # noqa: ANN001
                if not self.use_cache:
                    return func(self, atoms, *args, **kwargs)

                full_key = self.cache_key + "/" + key
                if isinstance(atoms, CandidateBaseClass):
                    value = atoms.get_from_cache(full_key)
                    if value is None:
                        value = func(self, atoms, *args, **kwargs)
                        if atoms.use_cache:
                            atoms.set_to_cache(full_key, value)
                else:
                    value = func(self, atoms, *args, **kwargs)

                return value

            return wrapper

        return decorator

    def get_from_cache(self, key: str) -> Any:
        if not self.use_cache:
            return None

        identifier, value = self._cache.get(key, (None, None))
        if identifier is not None:
            if self.compare_identity(identifier):
                return value
        else:
            return None

    def set_to_cache(self, key: str, value: Any) -> None:
        self._cache.put(key, (self.get_identifier(), value))

    def compare_identity(self, identifier: Tuple) -> bool:
        for a, b in zip(identifier, self.get_identifier()):
            equal = (a == b).all()
            if not equal:
                return equal
        return equal

    def get_identifier(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        return (self.get_atomic_numbers(), self.get_positions(), self.get_cell())

    def add_meta_information(self, name: str, value: Any) -> None:
        """
        Adds an entry to the meta_information dictionary

        Parameters
        -----------
        name: str (preferably, but can take anything that indexes a dict)
            Key to the dict
        value:
            Value to be set in the dict.
        """
        self.meta_information[name] = value

    def add_write_key(self, value: Any) -> None:
        """
        Adds a write key to the candidates meta information.

        Parameters
        -----------
        value: str
            key to add to the write information

        """
        try:
            keys = self.get_meta_information("write_keys")
            if isinstance(keys, str):
                keys = list(keys.split(" "))
            if value not in keys:
                keys.append(value)
        except Exception:
            keys = [value]
        self.add_meta_information("write_keys", keys)

    def print_properties(self, writer: Callable, iteration: int) -> None:
        keys = self.get_meta_information("write_keys")
        strings_list = []
        write_string = "Energy: " + str(iteration) + "  " + str(self.get_potential_energy()) + "  "

        if keys is not None:
            for key in keys:
                addendum = "[" + key + ":" + " " + self.get_meta_information(key) + "] "
                if len(write_string) + len(addendum) > 120:
                    strings_list.append(write_string)
                    write_string = ""

                write_string += addendum
        strings_list.append(write_string)
        if strings_list is not None:
            for string in strings_list:
                writer(string)

    def get_meta_information(self, name: str) -> Any:
        """
        Get from the meta_information dict.

        Parameters
        -----------
        name: str
            Key to get with.

        Returns
        --------
        value - any type
            A copy of the wanted entry in the dict or None if it is not set.
        """
        try:
            return self.meta_information.get(name, None).copy()
        except AttributeError:
            # This catches for example 'int' that dont have a copy method.
            # Ints won't change in-place, but it perhaps custom classes will.
            return self.meta_information.get(name, None)

    def get_meta_information_no_copy(self, name: str) -> Any:
        """
        Get from the meta_information dict without copying

        Parameters
        -----------
        name: str
            Key to get with.

        Returns
        --------
        value - any type
            The wanted entry in the dict or None if it is not set.
        """
        return self.meta_information.get(name, None)

    def has_meta_information(self, name: str) -> bool:
        """
        Get from the meta_information dict without copying

        Parameters
        -----------
        name: str
            Key to get with.

        Returns
        --------
        bool
            True if the 'name' is a key to meta_information.
        """
        return name in self.meta_information.keys()

    def pop_meta_information(self, name: str) -> Any:
        """
        Pop from the meta_information dict.

        Parameters
        -----------
        name: str
            Key to get with.

        Returns
        --------
        value - any type
            The wanted entry in the dict or None if it is not set.
        """
        return self.meta_information.pop(name, None)

    def reset_meta_information(self) -> None:
        """
        Resets meta_information
        """
        self.meta_information = dict()

    def get_template(self) -> Atoms:
        """
        Get the template atoms object.

        Returns
        --------
        atoms
            Template as an Atoms object.
        """
        return Atoms(
            numbers=self.numbers[self.template_indices],
            positions=self.positions[self.template_indices],
            cell=self.cell,
            pbc=self.pbc,
        )

    def copy(self) -> "CandidateBaseClass":
        """
        Return a copy of candidate object.

        Not sure if template needs to be copied, but will do it to be safe.

        Returns
        --------
        candidate
            A copy of the candidate object.
        """
        candidate = self.__class__(
            template=self.template.copy(), cell=self.cell, pbc=self.pbc, info=self.info, celldisp=self._celldisp.copy()
        )
        candidate.meta_information = self.meta_information.copy()

        candidate.arrays = {}
        for name, a in self.arrays.items():
            candidate.arrays[name] = a.copy()

        candidate.constraints = deepcopy(self.constraints)

        return candidate

    def copy_calculator_to(self, atoms: Atoms) -> None:
        """
        Copy current calculator and attach to the atoms object
        """
        if self.calc is not None and "energy" in self.calc.results:
            if "forces" in self.calc.results:
                calc = SinglePointCalculator(
                    atoms, energy=self.calc.results["energy"], forces=self.calc.results["forces"]
                )
            else:
                calc = SinglePointCalculator(atoms, energy=self.calc.results["energy"])
            atoms.set_calculator(calc)

    def get_property(self, key: str) -> Any:
        """
        Get property from calculator.

        Parameters
        -----------
        key
            Key used to index calc.get_property

        Returns
        --------
        value
            Value of calc.get.property(key)
        """

        return self.calc.get_property(key)

    def get_template_indices(self) -> np.array:
        """
        Returns
        --------
        np.array
            Array of template indices
        """
        return self.template_indices

    def get_optimize_indices(self) -> np.array:
        """
        Returns
        --------
        np.array
            Indices of of atoms that are part of the search.
        """
        return np.arange(len(self.template), len(self))

    def get_center_of_geometry(self, all_atoms: bool = False) -> np.array:
        """
        Returns the center of geometry.

        Parameters
        -----------
        all_atoms: bool
            If True all atoms are included, if False only non-template atoms are.
        """

        if all_atoms:
            return np.mean(self.positions, axis=0).reshape(1, 3)
        else:
            return np.mean(self.positions[self.get_optimize_indices()], axis=0).reshape(1, 3)

    def set_calculator(self, calc: Any) -> None:
        """
        "Old" ASE syntax for setting calculator, avoids the annoying warning and
        uses this better syntax.

        Parameters
        -----------
        calc: calculator
            Calculator to set.
        """
        self.calc = calc

    def get_search_formula(self):
        """
        Get the formula of the search atoms.

        Returns
        --------
        str
            Chemical formula of the search atoms.
        """
        numbers = self.get_search_numbers()
        return Atoms(numbers=numbers).symbols.get_chemical_formula()

    def get_search_numbers(self):
        """
        Get the atomic numbers of the search atoms.

        Returns
        --------
        np.array
            Atomic numbers of the search atoms.
        """
        return self.get_atomic_numbers()[self.get_optimize_indices()]

    def __getitem__(self, i):
        """
        Get item from atoms object.

        Parameters
        -----------
        i: int, array-like or slice.
            Index to get.

        Returns
        --------
        atom
            Atom at index i.
        """
        import numbers

        if isinstance(i, numbers.Integral):
            return super().__getitem__(i)

        # All the indices that are to be extracted:
        if isinstance(i, slice):
            indices = np.arange(i.start, len(self), i.step)
        else:
            indices = np.array(i)

        # Determine if any are template atoms:
        template_indices = np.intersect1d(indices, self.template_indices)

        # If there are template atoms, we need to adjust the indices.
        template_indices = np.where(np.isin(indices, self.template_indices))[0]

        return self.__class__(
            template_indices=template_indices,
            positions=self.positions[indices].copy(),
            numbers=self.numbers[indices].copy(),
            cell=self.cell.copy(),
            pbc=self.pbc.copy(),
        )

    def set_constraint(self, constraints=None):
        """
        Set constraints to the candidate.

        Parameters
        -----------
        """
        from agox.utils.constraints import ConstraintManager

        if isinstance(constraints, ConstraintManager):
            constraints = constraints.get_constraints(self)
        super().set_constraint(constraints)


def disable_cache(candidate: CandidateBaseClass) -> None:
    # Can be either Candidate or Atoms.
    if isinstance(candidate, CandidateBaseClass):
        candidate.use_cache = False


def switch_cache(candidate: CandidateBaseClass, state: bool) -> bool:
    prev_state = False
    if isinstance(candidate, CandidateBaseClass):
        prev_state = candidate.use_cache
        candidate.use_cache = state
    return prev_state
