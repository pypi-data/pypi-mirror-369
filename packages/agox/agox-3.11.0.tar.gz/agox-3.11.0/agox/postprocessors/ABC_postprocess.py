from abc import ABC, abstractmethod

from agox.observer import Observer
from agox.writer import Writer


class PostprocessBaseClass(ABC, Observer):
    """
    Base class for all postprocessors.

    Postprocessors are used to apply common postprocessing steps to all generated candidates.

    Parameters
    ----------
    gets : dict
        Dictionary of get keys, e.g. {'get_key':'candidates'}. Used to select
        from which entry in the agox.main.State cache the postprocessor should get candidates.
    sets : dict
        Dictionary of set keys, e.g. {'set_key':'candidates'}. Used to select
        in which entry in the agox.main.State cache the postprocessor should store the postprocessed candidates.
    """

    def __init__(
        self,
        gets: dict = None,
        sets: dict = None,
        order: int = 3,
        surname: str = None,
        **kwargs,
    ) -> None:
        if gets is None:
            gets = {"get_key": "candidates"}
        if sets is None:
            sets = {"set_key": "candidates"}        

        Observer.__init__(self, gets=gets, sets=sets, order=order, surname=surname, **kwargs)

        self.add_observer_method(
            self.postprocess_candidates,
            sets=self.sets[0],
            gets=self.gets[0],
            order=self.order[0],
            handler_identifier="AGOX",
        )

    def update(self):
        """
        Used if the postprocessor needs to continously update, e.g. the training of a surrogate potential.
        """
        pass

    @abstractmethod
    def postprocess(self, candidate):  # pragma: no cover
        """
        Method that actually do the post_processing
        """
        return postprocessed_candidate

    def process_list(self, list_of_candidates):
        """
        This allows all postproccesors to act on a list of candidates serially.
        This function can be overwritten by sub-class to implement parallelism.
        """
        processed_candidates = []
        for candidate in list_of_candidates:
            processed_candidate = self.postprocess(candidate)
            processed_candidates.append(processed_candidate)
        return processed_candidates

    def __add__(self, other):
        return SequencePostprocess(processes=[self, other], order=self.order)

    @Observer.observer_method
    def postprocess_candidates(self, state):
        candidates = state.get_from_cache(self, self.get_key)

        if self.do_check():
            candidates = self.process_list(candidates)
            candidates = list(filter(None, candidates))

        # Add data in write mode - so overwrites!
        state.add_to_cache(self, self.set_key, candidates, mode="w")


class SequencePostprocess(PostprocessBaseClass):
    name = "PostprocessSequence"

    def __init__(self, processes=[], order=None):
        self.processes = processes
        self.order = order

    def postprocess(self, candidate):
        for process in self.processes:
            candidate = process.postprocess(candidate)

        return candidate

    def process_list(self, list_of_candidates):
        for process in self.processes:
            list_of_candidates = process.process_list(list_of_candidates)
        return list_of_candidates

    def __add__(self, other):
        self.processes.append(other)
        return self

    def attach(self, main):
        for j, process in enumerate(self.processes):
            process.update_order(process.postprocess_candidates, order=self.order[0] + j * 0.1)
            process.attach(main)
