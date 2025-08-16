from abc import ABC, abstractmethod  # noqa: N999
from typing import List

from ase import Atoms
from ase.calculators.singlepoint import SinglePointCalculator

from agox.candidates import Candidate
from agox.main.state import State
from agox.observer import Observer, ObserverHandler


class DatabaseBaseClass(ABC, ObserverHandler, Observer):
    """
    Base class for all databases.

    Databases are used to store, typically evaluated, candidates.

    Parameters
    ----------
    gets : dict
        Dictionary of get keys, e.g. {'get_key':'evaluated_candidates'}. Used to select
        from which entry in the agox.main.State cache the database should get candidates.
    order : int
        Order of the database, by default 6
    """

    def __init__(
        self,
        gets: dict[str, str] | None = None,
        sets: dict[str, str] | None = None,
        order: int = 6,
        surname: str = "",
        **kwargs,
    ) -> None:

        if gets is None:
            gets = {"get_key": "evaluated_candidates"}        

        Observer.__init__(self, gets=gets, sets=sets, order=order, surname=surname, **kwargs)
        ObserverHandler.__init__(self, handler_identifier="database", dispatch_method=self.store_in_database)
        self.candidates = []

        self.objects_to_assign = []

        self.add_observer_method(
            self.store_in_database, sets=self.sets[0], gets=self.gets[0], order=self.order[0], handler_identifier="AGOX"
        )

    ########################################################################################
    # Required methods
    ########################################################################################

    @abstractmethod
    def write(self, *args, **kwargs):  # pragma: no cover # noqa
        """
        Write stuff to database
        """

    @abstractmethod
    def store_candidate(self, candidate):  # pragma: no cover # noqa
        pass

    @property
    @abstractmethod
    def name(self):  # pragma: no cover # noqa
        return NotImplementedError

    ########################################################################################
    # Default methods
    ########################################################################################

    def _copy_candidate(self, candidate: Candidate) -> Candidate:
        new_candidate = candidate.copy()
        calc_dict = candidate.calc.results.copy()
        new_calc = SinglePointCalculator(candidate, **calc_dict)
        new_candidate.set_calculator(new_calc)
        return new_candidate

    def get_all_candidates(self, **kwargs) -> List[Candidate]:
        all_candidates = []
        for candidate in self.candidates:
            all_candidates.append(self._copy_candidate(candidate))
        return all_candidates

    def get_most_recent_candidate(self) -> Candidate:
        if len(self.candidates) > 0:
            candidate = self._copy_candidate(self.candidates[-1])
        else:
            candidate = None
        return candidate

    def get_recent_candidates(self, number: int) -> List[Candidate]:
        return [self._copy_candidate(candidate) for candidate in self.candidates[-number:]]

    def __len__(self) -> int:
        return len(self.candidates)

    @Observer.observer_method
    def store_in_database(self, state: State) -> None:
        evaluated_candidates = state.get_from_cache(self, self.get_key)
        anything_accepted = False
        for j, candidate in enumerate(evaluated_candidates):
            if candidate:
                self.store_candidate(candidate, accepted=True, write=True)
                anything_accepted = True

            elif candidate is None:
                dummy_candidate = self.candidate_instanstiator(template=Atoms())
                dummy_candidate.set_calculator(SinglePointCalculator(dummy_candidate, energy=float("nan")))

                # This will dispatch to observers if valid data has been added but the last candidate is None.
                self.store_candidate(candidate, accepted=False, write=True)

        if anything_accepted:
            self.dispatch_to_observers(database=self, state=state)
