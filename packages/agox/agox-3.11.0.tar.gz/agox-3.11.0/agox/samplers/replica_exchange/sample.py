from dataclasses import dataclass

import numpy as np
from ase.calculators.singlepoint import SinglePointCalculator

from agox.candidates import Candidate


@dataclass
class SampleMember:
    _candidate: Candidate = None
    _energy: float = np.inf

    def empty(self) -> bool:
        return self.candidate is None
    
    def get_energy(self) -> float:
        return self._energy
    
    @property
    def candidate(self) -> Candidate:
        if self._candidate is None:
            return None
        candidate = self._candidate.copy()
        candidate.calc = SinglePointCalculator(candidate, **self._candidate.calc.results)
        return candidate
    
    @candidate.setter
    def candidate(self, value: Candidate) -> None:
        if isinstance(value, Candidate) or value is None:
            self._candidate = value
        else:
            raise ValueError('Candidate must be an instance of Candidate')

    @property
    def energy(self) -> float:
        return self._energy
    
    @energy.setter
    def energy(self, value: float) -> None:
        if isinstance(value, (int, float)) or value is None:
            self._energy = value
        else:
            raise ValueError('Energy must be a float or int')

    def set_index(self, i): 
        self._candidate.meta_information["walker_index"] = i


class ReplicaExchangeSample:

    def __init__(self, sample_size: int) -> None:
        self.sample_size = sample_size
        self.sample = [SampleMember() for _ in range(sample_size)]

    def swap(self, i: int, j: int) -> None:
        self.sample[i], self.sample[j] = self.sample[j], self.sample[i]
        self.sample[i].set_index(i)
        self.sample[j].set_index(j)
        
    def update(self, key: int, value: Candidate, energy: float) -> None:   
        if value is None: 
            _value = None
            energy = np.inf
        else:
            _value = value.copy()
            _value.calc = SinglePointCalculator(_value, **value.calc.results)
        self.sample[key].candidate = _value
        self.sample[key].energy = energy

    def __getitem__(self, key: int) -> Candidate:
        return self.sample[key]
    
    def __setitem__(self, key: int, value: Candidate) -> None:
        self.update(key, value, value.get_potential_energy())

    def __len__(self) -> int:
        return len(self.sample)
    
    def __iter__(self) -> iter:
        return iter(self.sample)