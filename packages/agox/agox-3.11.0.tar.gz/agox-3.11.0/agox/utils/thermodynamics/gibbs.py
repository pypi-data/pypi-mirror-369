from copy import deepcopy as dcpy
from typing import Dict, Optional

import numpy as np
from ase import Atoms

from agox.candidates import StandardCandidate
from agox.utils.thermodynamics import ThermodynamicsData


def get_composition(numbers: np.array, references: dict) -> dict:
    ##Gets sorted array of numbers containing species or molecules that contribute to gfe, longer first
    size_sort = np.argsort([-len(Atoms(k).numbers) for k in references.keys()])
    r_nums = [Atoms(k).numbers for k in references.keys()]
    r_keys = [k for k in references.keys()]
    nums = dcpy(numbers)
    ret = dict()
    for sz in size_sort:
        unique, counts = np.unique(nums, return_counts=True)
        d = dict(zip(unique, counts))
        hits = min([d.get(i, 0) for i in r_nums[sz]])
        ret[r_keys[sz]] = hits
        # delete from array
        for i in r_nums[sz]:
            idx = np.flatnonzero(nums == i)
            np.delete(nums, idx[:hits])
    return ret


def gibbs_free_energy(
    candidate: Optional[StandardCandidate] = None,
    numbers: Optional[np.array] = None,
    total_energy: float = None,
    template_energy: float = None,
    thermo_data: Optional[ThermodynamicsData] = None,
    references: Optional[Dict] = None,
    chemical_potentials: Optional[Dict] = None,
) -> float:
    """
    Calculate the Gibbs free energy of a candidate. 

    Parameters
    -----------
    candidate: StandardCandidate
        The candidate to calculate the Gibbs free energy for. Can be omitted 
        if numbers and total_energy are provided.
    numbers: np.array
        Array of the atomic numbers of the candidate. Can be omitted if candidate
        is provided.
    total_energy: float
        The total energy of the candidate. Can be omitted if candidate is provided.
    thermo_data: ThermodynamicsData
        The thermodynamic data to use for the calculation. Can be omitted if 
        references and chemical_potentials are provided.
    references: dict
        The references to use for the calculation. Can be omitted if thermo_data
        is provided.
    chemical_potentials: dict
        The chemical potentials to use for the calculation. Can be omitted if 
        thermo_data is provided.
    """

    if total_energy is None:
        total_energy = candidate.get_total_energy()
    if numbers is None:
        numbers = candidate.get_search_numbers()

    if thermo_data is not None:
        if references is None:
            references = thermo_data.references
        if chemical_potentials is None:
            chemical_potentials = thermo_data.chemical_potentials
        if template_energy is None:
            template_energy = thermo_data.template_energy
    else:
        if references is None or chemical_potentials is None or template_energy is None:
            raise ValueError("Thermodynamic data or references, chemical_potentials and template_energy must be provided")

    gibbs_energy = total_energy - template_energy
    comp = get_composition(numbers, references)

    for k in comp.keys():
        n = comp.get(k, 0)
        gibbs_energy -= n * (references[k] + chemical_potentials[k])

    return gibbs_energy
