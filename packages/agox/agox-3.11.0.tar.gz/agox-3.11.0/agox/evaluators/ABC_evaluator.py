import time
from abc import ABC, abstractmethod
from typing import Callable

from agox import State
from agox.candidates import Candidate, CandidateBaseClass
from agox.observer import Observer


class EvaluatorBaseClass(ABC, Observer):
    """
    Base class for evaluators.

    Evaluators calculate the objective function (usually the energy).

    Parameters
    ----------
    number_to_evaluate : int, optional
        The number of candidates to evaluate before stopping. The default is 1.
    check_callback : Callable[[CandidateBaseClass], None], optional
        A function that is called with every evaluated candidate as argument
        before it is added to the list of evaluated candidates. If this
        callable raises an exception, the candidate will not be added. This can
        be used to, e.g., check for convergence when using ASE calculators that
        do not raise an exception themselves if they did not converge. When not
        provided, no check will be performed.
    """

    def __init__(
        self,
        number_to_evaluate: int = 1,
        max_evaluate: int = None,
        check_callback: Callable[[CandidateBaseClass], None] | None = None,
        gets: dict[str, str] | None = None,
        sets: dict[str, str] | None = None,
        order: int | float = 5,
        surname: str | None = None,
        **kwargs,
    ) -> None:

        if sets is None:
            sets = {"set_key": "evaluated_candidates"}
        if gets is None:
            gets = {"get_key": "prioritized_candidates"}

        Observer.__init__(self, gets=gets, sets=sets, order=order, surname=surname, **kwargs)
        self.number_to_evaluate = number_to_evaluate
        self.check_callback = check_callback or self._default_check_callback
        self.total_evaluated = 0
        self.max_evaluate = max_evaluate

        self.evaluated_candidates = []

        self.add_observer_method(
            self.evaluate, sets=self.sets[0], gets=self.gets[0], order=self.order[0], handler_identifier="AGOX"
        )

        self.start_time = time.time()

    def __call__(self, candidate):
        return self.evaluate_candidate(candidate)

    @abstractmethod
    def evaluate_candidate(self, candidate: list[Candidate]) -> None:  # pragma: no cover
        """
        Evaluates the given candidate.

        This function MUST append the candidates it wishes to pass to the AGOX
        State cache to the list self.evaluated_candidates.

        Parameters
        ----------
        candidate : AGOX candidate object.
            The candidate object to evaluate.

        Returns
        -------
        bool
            Whether the evaluation was successful.
        """
        ...

    @property
    @abstractmethod
    def name(self) -> None:  # pragma: no cover
        pass

    @Observer.observer_method
    def evaluate(self, state: State) -> None:
        candidates = state.get_from_cache(self, self.get_key)
        done = False

        self.evaluated_candidates = []
        passed_evaluation_count = 0
        if self.do_check():
            while candidates and not done:
                self.writer(f"Trying candidate - remaining {len(candidates)}")
                candidate = candidates.pop(0)

                if candidate is None:
                    self.writer("Candidate was None - are your other modules working as intended?")
                    continue

                internal_state = self.evaluate_candidate(candidate)

                if internal_state:
                    self.writer("Succesful calculation of candidate.")
                    passed_evaluation_count += 1
                    self.evaluated_candidates[-1].add_meta_information("final", True)
                    iteration = self.get_iteration_counter()
                    energy_dict = {iteration : self.evaluated_candidates[-1].get_potential_energy()}
                    self.evaluated_candidates[-1].add_meta_information("evaluator_energy", energy_dict)
                    if passed_evaluation_count == self.number_to_evaluate:
                        self.writer("Calculated required number of candidates.")
                        done = True

        state.add_to_cache(self, self.set_key, self.evaluated_candidates, mode="a")

        self.total_evaluated += len(self.evaluated_candidates)
        if self.max_evaluate is not None and self.total_evaluated >= self.max_evaluate:
            state.set_convergence_status(True)

    def _check_and_append_candidate(self, candidate: CandidateBaseClass) -> None:
        """Check a candidate using the check callable, and then append it to
        the list of evaluated candidates.

        Parameters
        ----------
        candidate : CandidateBaseClass
            Candidate to check and append.
        """
        self.check_callback(candidate)
        self._add_time_stamp(candidate)
        self.evaluated_candidates.append(candidate)

    def _default_check_callback(self, _: CandidateBaseClass) -> None:
        """Default check callable: do nothing."""
        pass
        
    def _add_time_stamp(self, candidate):
        candidate.add_meta_information("time_stamp", time.time() - self.start_time)

    def __add__(self, other):
        return EvaluatorCollection(evaluators=[self, other])


class EvaluatorCollection(EvaluatorBaseClass):
    name = "EvaluatorCollection"

    def __init__(self, evaluators: list[EvaluatorBaseClass]) -> None:
        super().__init__()
        self.evaluators = evaluators

    def evaluate_candidate(self, candidate: Candidate) -> bool:
        self.apply_evaluators(candidate)

    def add_evaluator(self, evaluator: EvaluatorBaseClass) -> None:
        self.evaluators.append(evaluator)

    def list_evaluators(self) -> None:
        for i, evaluator in enumerate(self.evaluators):
            print("Evaluator {}: {} - {}".format(i, evaluator.name, evaluator))

    def apply_evaluators(self, candidate: Candidate) -> bool:
        for evaluator in self.evaluators:
            evaluator_state = evaluator(candidate)
            if not evaluator_state:
                return False
        return True

    def __add__(self, other: EvaluatorBaseClass): # noqa
        self.evaluators.append(other)
        return self
