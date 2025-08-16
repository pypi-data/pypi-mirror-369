import json
from pathlib import Path
from typing import Dict, Optional, Union

import numpy as np
from ase.data import atomic_numbers

symbols = {n: s for s, n in atomic_numbers.items()}


class ThermodynamicsData:
    def __init__(
        self,
        references: Dict[str, float],
        chemical_potentials: Dict[str, float],
        template_energy: Optional[float] = 0.0,
    ) -> None:
        """
        Container for thermodynamic data.

        Parameters
        ----------
        references :
            Reference energies for each element. Keys are element symbols.
        chemical_potentials :
            Chemical potentials for each element. Keys are element symbols.
        template_energy :
            Energy of the template structure.
        """
        self.references = references
        self.chemical_potentials = chemical_potentials
        self.template_energy = template_energy

    def set_chemical_potential(self, element: Union[str, int], value: float) -> None:
        """
        Set the chemical potential of an element.

        Parameters
        ----------
        element : str or int
            Element symbol or atomic number.
        value : float
            Chemical potential.
        """
        element = self.convert_number_to_element(element)
        self.chemical_potentials[element] = value

    def get_chemical_potential(self, element: Union[str, int]) -> float:
        """
        Get the chemical potential of an element.

        Parameters
        ----------
        element : str or int
            Element symbol or atomic number.
        """
        element = self.convert_number_to_element(element)
        return self.chemical_potentials[element]

    def set_reference(self, element: str, value: float) -> None:
        """
        Set the reference energy of an element.

        Parameters
        ----------
        element : str or int
            Element symbol or atomic number.
        value : float
            Reference energy.
        """
        element = self.convert_number_to_element(element)
        self.references[element] = value

    def get_reference(self, element: Union[str, int]) -> float:
        """
        Get the reference energy of an element.

        Parameters
        ----------
        element : str or int
            Element symbol or atomic number.
        """
        element = self.convert_number_to_element(element)
        return self.references[element]

    def convert_number_to_element(self, element: Union[int, str]) -> str:
        """
        Convert an atomic number to an element symbol.

        Parameters
        ----------
        element : int or str
            Atomic number or element symbol.

        Returns
        -------
        str
            Element symbol.
        """
        if isinstance(element, (int, np.int64)):
            return symbols[element]
        return element

    @classmethod
    def from_file(cls, path: Union[str, Path]):
        """
        Load thermodynamic data from a file.

        Parameters
        ----------
        path : str or Path
            Path to the file.

        Returns
        -------
        ThermodynamicsData
            Thermodynamic data.
        """
        if isinstance(path, str):
            path = Path(path)

        if not path.exists():
            raise FileNotFoundError(f"{path} does not exist")

        with open(path, "r") as f:
            data = json.load(f)

        return cls(
            references=data["references"],
            chemical_potentials=data["chemical_potentials"],
            template_energy=data.get("template_energy", 0.0),
        )
    
    @classmethod
    def load(cls, path: Path):
        return ThermodynamicsData.from_file(path)

    def save(self, path: Union[str, Path], overwrite: bool = False) -> None:
        """
        Save thermodynamic data to a file.

        Parameters
        ----------
        path : str or Path
            Path to the file.
        overwrite : bool
            Whether to overwrite the file if it already exists.
        """
        if isinstance(path, str):
            path = Path(path)

        data = {
            "references": self.references,
            "chemical_potentials": self.chemical_potentials,
            "template_energy": self.template_energy,
        }

        if not path.exists() or overwrite:
            with open(path, "w") as f:
                json.dump(data, f, indent=4)
        else:
            raise FileExistsError(f"{path} already exists")