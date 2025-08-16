from functools import reduce

import numpy as np
from ase import Atoms
from ase.atoms import symbols2numbers
from ase.symbols import Symbols

from agox.environments.ABC_environment import EnvironmentBaseClass


# This is a bit messy but it crates a matrix with a combination of all possible atom types and numbers so that it works without changing
# the underlying self._numbers approach
def make_numbers_list_from_matrix(symbols, matrix):
    numbers_list = []
    for line in matrix:
        combination = []
        for j in range(len(symbols)):
            combination += line[j] * [symbols2numbers(symbols[j])]
        combination = list(reduce(lambda x, y: x + y, combination, []))
        numbers_list.append(combination)
    return numbers_list


def set_combination_matrix(symbols_dict):
    symbols = list(symbols_dict.keys())
    lengths = 1
    lengths_array = []
    for i in symbols:
        lengths_array.append(len(list(symbols_dict[i])))
        lengths = lengths * len(list(symbols_dict[i]))
    combiantion_matrix = np.zeros((lengths, len(symbols)), dtype=int)
    for x in range(lengths):
        for i in range(len(symbols)):
            advancement = int(np.prod(lengths_array[i + 1 : len(symbols)]))
            pos = int(x / advancement) % len(symbols_dict[symbols[i]])
            combiantion_matrix[x, i] = symbols_dict[symbols[i]][pos]
    return make_numbers_list_from_matrix(symbols, combiantion_matrix)


class Environment(EnvironmentBaseClass):
    """
    Environment class for the generation of candidates.

    Parameters
    ----------
    template : Atoms
        The template structure to use.
    numbers : list, optional
        List of atomic numbers to add to the template, by default None.
    symbols : list, optional
        List of atomic symbols to add to the template, by default None.
    numbers_list  : list, optional
        List of list of atomic numbers to add to the template each sublist corresponding to one stoichiometry of interes, by default None.
    symbols_list  : list, optional
        List of list of atomic symbols to add to the template each sublist corresponding to one stoichiometry of interes, by default None.
    symbols_range : dict, optional
        Dictionary specifying ranges of composition for each element, by default None.

    print_report : bool, optional
        If True, a report is printed, by default True.

    """

    def __init__(
        self,
        template: Atoms,
        symbols: str = None,
        numbers: list = None,
        numbers_list: list = None,
        symbols_list: list = None,
        symbols_range: dict = None,
        print_report: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # Both numbers and symbols cannot be specified:
        assert (
            (
                ((numbers_list is not None) is not (symbols_list is not None))
                is not (symbols_range is not None)
            )
            is not (symbols is not None)
        ) is not (numbers is not None)  # XOR

        if numbers is not None:
            self.set_numbers(numbers)
        if symbols is not None:
            self.set_numbers(symbols2numbers(symbols))
        if numbers_list is not None:
            self.set_numbers_list(numbers_list)

        elif symbols_list is not None:
            self.set_numbers_list(
                [symbols2numbers(symbols) for symbols in symbols_list]
            )

        elif symbols_range is not None:
            self.set_numbers_list(set_combination_matrix(symbols_range))

        if type(template) is Atoms:
            template = self.convert_to_candidate_object(template)
        self._template = template

        if self.confinement_cell is None:
            self.confinement_cell = self._template.get_cell()
            self.confinement_corner = np.array([0, 0, 0])

        if print_report:
            self.environment_report()

    def has_multiple_compositions(self):  # -> bool
        return len(self._numbers_list) > 1

    def get_template(self):
        return self._template.copy()

    def set_template(self, template):
        self._template = template

    def set_numbers(self, numbers):
        # Will override all of the _numbers list
        self._numbers_list = [numbers]
        self._numbers = self._numbers_list[0]

    def get_numbers(self):
        id = np.random.randint(len(self._numbers_list))
        return np.array(self._numbers_list[id]).flatten()

    def get_missing_types(self):
        return np.sort(np.unique(self.get_numbers()))

    def get_all_types(self):  # -> listlist[int]:
        return list(set(list(self._template.numbers) + self.get_numbers_list_flat()))

    def get_identifier(self):
        return self.__hash__()

    def get_missing_indices(self):
        max_additional = max([len(n) for n in self._numbers_list])
        return np.arange(len(self._template), len(self._template) + max_additional)

    def get_numbers_by_index(self, idx):
        return self._numbers_list[idx]

    def set_numbers_list(self, numbers_list):  # list[list[int]]):
        self._numbers_list = numbers_list
        self._numbers = [
            self._numbers_list[
                max(
                    range(len(self._numbers_list)),
                    key=lambda x: len(self._numbers_list[x]),
                )
            ]
        ]

    def get_numbers_list(self):  # -> listlist[list[int]]:
        return self._numbers_list

    def get_numbers_list_flat(self):  # -> listlist[int]:
        fl = []
        for nl in self.get_numbers_list():
            fl.extend(nl)
        return fl

    # Returns types of one or all the systems including template
    def get_types(self):  # -> listlist[int]:
        return list(set(list(self._template.numbers) + self.get_numbers()))

    # Returns types of one or all the systems including template
    def get_all_types_notemplate(self):  # ->list[int]:
        return list(set(list(self.get_numbers_list_flat())))

    def get_numbers_indices(self):
        return np.arange(len(self._template), len(self._template) + len(self._numbers))

    def get_all_numbers(self):
        all_numbers = np.append(self.get_numbers(), self._template.get_atomic_numbers())
        return all_numbers

    def get_numbers_types_by_index(self, idx):
        return np.sort(np.unique(self._numbers_list[idx].copy()))

    def get_numbers_indices_by_index(self, idx):
        return np.arange(
            len(self._template),
            len(self._template) + len(self.get_numbers_types_by_index(idx)),
        )

    def get_full_formula(self):
        return np.append(self.get_numbers(), self._template.get_atomic_numbers())

    def get_full_formula_by_index(self, idx):
        return np.append(
            self.get_numbers_by_index(idx), self._template.get_atomic_numbers()
        )

    def get_all_species(self):
        return list(Symbols(self.get_all_types()).species())

    def get_species(self):
        return list(np.unique(self.get_all_species()))

    def get_atoms(self):
        atoms = self.get_template()
        atoms += Atoms(self.get_numbers())
        return atoms

    def get_atoms_by_index(self, idx):  # -> Atoms
        atoms = self.get_template()
        atoms += Atoms(self.get_numbers_list()[idx % len(self.get_numbers_list())])
        return atoms

    def get_all_atoms(self):
        n_list = self.get_numbers_list()
        return [self.get_template() + Atoms([at]) for at in n_list]

    def match(self, candidate):
        cand_numbers = candidate.get_atomic_numbers()
        if not (
            candidate.positions[0 : len(candidate.template)] == self._template.positions
        ).all():
            return False
        c = cand_numbers[len(candidate.template) :]
        for i, n in enumerate(self._numbers_list):
            if (np.sort(c) == np.sort(n)).all():
                return True
        return False

    def get_candidate_numbers_strict(self, candidate):
        """
        Returns the list with the numbers specific for that candidate
        Checks if candidate has same template"""
        assert [
            candidate[idx].symbol for idx in candidate.get_template_indices()
        ] == list(self._template.symbols)
        numbers = sorted(
            [candidate[i].number for i in candidate.get_optimize_indices()]
        )
        for idx, n in enumerate(self._numbers_list):
            if numbers == sorted(n):
                return n, idx

        return None, -1

    def get_candidate_numbers(self, candidate):
        """
        Returns the list with the numbers specific for that candidate
        Does not check if candidate has the same tempalte"""
        numbers = sorted([candidate[i] for i in candidate.get_optimize_indices()])
        for n in self._numbers_list:
            if (numbers == sorted(n)).all():
                return n
        return None

    def __hash__(self):
        feature = (
            tuple(self.get_numbers())
            + tuple(self._template.get_atomic_numbers())
            + tuple(self._template.get_positions().flatten().tolist())
        )
        return hash(feature)

    def get_identifier(self):
        return self.__hash__()

    def environment_report(self) -> None:
        self.writer.write_panel(str(self), "Environment report")

    def __str__(self) -> str:
        string = ""
        tab = "    "
        string += "Atoms in search:\n"

        missing_numbers = self.get_numbers()
        for number in np.unique(missing_numbers):
            symbols_object = Symbols([number])
            specie = symbols_object.species().pop()
            count = np.count_nonzero(missing_numbers == number)
            string += f"{tab}{specie} = {count}\n"

        total_symbols = Symbols(self.get_all_numbers())
        string += f"Template formula: {self._template.get_chemical_formula()}\n"
        string += f"Full formula: {total_symbols.get_chemical_formula()}\n"

        string += "Cell:\n"
        for cell_vec in self._template.get_cell():
            string += tab + "{:4.2f} {:4.2f} {:4.2f}\n".format(*cell_vec)
        
        string += "Periodicity:\n"
        string += tab + "{} {} {}\n".format(*self._template.pbc)

        string += f"Box constraint: {self.use_box_constraint}\n"
        
        if self.use_box_constraint:
            assert self.confinement_cell is not None
            assert self.confinement_corner is not None
            string += "Confinement corner\n"
            string += tab + "{:4.2f} {:4.2f} {:4.2f}\n".format(*self.confinement_corner)
            string += "Confinement cell:\n"
            for i, cell_vec in enumerate(self.confinement_cell):
                string += tab + "{:4.2f} {:4.2f} {:4.2f}".format(*cell_vec)
                if i != 2:
                    string += "\n"
        return string
        
