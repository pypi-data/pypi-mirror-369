import numpy as np

from agox.acquisitors.ABC_acquisitor import AcquisitorBaseClass
from agox.candidates import Candidate


class ReplicaExchangeAcquisitor(AcquisitorBaseClass):
    name = "ReplicaExchangeAcquisitor"

    def __init__(
        self,
        filter_last: bool = True,
        random: bool = True,
        sample_size: int = 10,
        gets: dict[str, str] = {"get_key": "sample"},
        always_lowest: bool = False,
        **kwargs,
    ) -> None:
        """
        Acquisitor for mananging selection of candidates for DFT evaluation in a
        replica exchange simulation.

        Parameters
        ----------
        dft_interval : int
            Number of iterations between DFT evaluations.
        filter_last : bool, optional
            If True, the last candidate in the list will be set to 0.0 fitness,
            which means it will not be selected for DFT evaluation. 
        random : bool, optional
            If True, the fitness values will be randomly generated between -1.0 and 0, otherwise 
            the fitness will be proportional to the index of walker it comes from, favouring low temperature walkers.
        sample_size : int, optional
            Number of candidates to sample from the pool of candidates. Default is 10.                
        """


        super().__init__(gets=gets, **kwargs)
        self.random = random
        self.always_lowest = always_lowest
        self.filter_last = filter_last
        self.sample_size = 10

    def calculate_acquisition_function(self, candidates: list[Candidate]) -> np.ndarray:
        if self.random:
            fitness = np.random.uniform(low=-1.0, high=0.0, size=len(candidates))
        else:
            fitness = np.linspace(-1.0, 0.0, num=len(candidates))
        should_ignore = False

        if len(candidates) >= self.sample_size:
            should_ignore = True
        if self.always_lowest:
            fitness[0] = -1.0
        if self.filter_last * should_ignore:
            fitness[len(candidates) - 1] = 0.0

        return fitness

    @classmethod
    def with_interval(cls, dft_interval: int, **kwargs):
        """
        Returns the interval for DFT evaluations.

        Parameters
        ----------
        dft_interval : int
            Number of iterations between DFT evaluations.

        Returns
        -------
        dict[str, int]
            Dictionary with the key 'dft_interval' and the value of the input parameter.
        """

        def skip_function(self, candidate_list: list[Candidate]) -> bool:
            """
            Function defining how often iterations are skipped for evaluation
            """
            if (self.get_iteration_counter()) % dft_interval != 0:
                return True
            else:
                return False

        return cls(
            skip_function=skip_function,
            **kwargs,
        )
