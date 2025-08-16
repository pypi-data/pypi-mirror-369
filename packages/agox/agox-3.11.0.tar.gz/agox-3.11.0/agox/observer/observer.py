import functools
from copy import copy
from typing import Callable, Dict, List, Optional

from agox.candidates import StandardCandidate
from agox.module import Module
from agox.observer.observer_handler import ObserverHandler
from agox.observer.observer_method import ObserverMethod
from agox.writer import Writer


class Observer(Module):
    def __init__(
        self,
        gets: List[Dict] = None,
        sets: List[Dict] = None,
        order: List[int] = None,
        **kwargs,
    ) -> None:
        """
        Base-class for classes that act as observers.

        Parameters
        -----------
        gets: dict
        Dict where the keys will be set as the name of attributes with the
        value being the value of the attribute. Used to get something from the
        iteration_cache during a run.

        sets: dict
        Dict where the keys will be set as the name of attributes with the
        value being the value of the attribute. Used to set something from the
        iteration_cache during a run.

        order: int/float
        Specifies the (relative) order of when the observer will be executed,
        lower numbers are executed first.

        sur_name: str
            An additional name added to classes name, can be used to distinguish
            between instances of the same class.
        """
        Module.__init__(self, **kwargs)

        if gets is None:
            gets = dict()
        if isinstance(gets, dict):
            gets = [gets]

        if sets is None:
            sets = dict()
        if isinstance(sets, dict):
            sets = [sets]

        if order is None:
            order = [0]
        if isinstance(order, int) or isinstance(order, float):
            order = [order]

        combined = dict()
        for tuple_of_dicts in [gets, sets]:
            for dict_ in tuple_of_dicts:
                for key, item in dict_.items():
                    combined[key] = item
        for key, value in combined.items():
            if key not in self.__dict__.keys():
                self.__dict__[key] = value
            else:
                raise NameError("Key {} already exists in the class.".format(key))

        self.set_keys = sum([list(set_dict.keys()) for set_dict in sets], [])
        self.set_values = sum([list(set_dict.values()) for set_dict in sets], [])
        self.get_keys = sum([list(get_dict.keys()) for get_dict in gets], [])
        self.get_values = sum([list(get_dict.values()) for get_dict in gets], [])
        self.gets = gets
        self.sets = sets

        self.order = order

        self.observer_methods = {}
        self.observer_handler_identifiers = []

        self.iteration_counter = None
        self.candidate_instanstiator = StandardCandidate

    def add_observer_method(
        self, method: Callable, sets: Dict, gets: Dict, order: int, handler_identifier: str = "any"
    ) -> None:
        """
        Adds an observer method that will later be attached with 'self.attach'.

        Parameters
        -----------
        method: method
            The function/method that will be called by the observer-loop.
        sets: dict
            Dict containing the keys that the method will set in the cache.
        gets: dict
            Dict containing the keys that the method will get from the cache.
        """
        observer_method = ObserverMethod(self.__name__, method.__name__, method, gets, sets, order, handler_identifier)
        self.observer_methods[observer_method.key] = observer_method

    def remove_observer_method(self, observer_method: ObserverMethod) -> None:
        """
        Remove an observer_method from the internal dict of methods, if this is
        done before calling 'attach' it will not be added as an observer.

        Parameters
        -----------
        observer_method: object
            An instance of ObserverMethod.
        """
        key = observer_method.key
        if key in self.observer_methods.keys():
            del self.observer_methods[key]

    def update_order(self, observer_method: ObserverMethod, order: int) -> None:
        """
        Change the order of a method. Not really tested in practice.

        Parameters
        -----------
        observer_method: object
            An instance of ObserverMethod.

        order: float
            New order to set.
        """
        key = observer_method.key
        assert key in self.observer_methods.keys()
        self.observer_methods[key].order = order

    def attach(self, handler: ObserverHandler) -> None:
        """
        Attaches all ObserverMethod's as to observer-loop of the ObserverHandler
        object 'main'

        Parameters
        ----------
        handler: object
            An instance of an ObserverHandler.
        """
        for observer_method in self.observer_methods.values():
            if (
                observer_method.handler_identifier == "any"
                or observer_method.handler_identifier == handler.handler_identifier
            ):
                observer_method.set_handler(handler.name)
                handler.attach_observer(observer_method)
                self.observer_handler_identifiers.append(handler.handler_identifier)

    def reset_observer(self) -> None:
        """
        Reset the observer_methods dict, removing all observer methods.
        """
        self.observer_methods = {}

    ############################################################################
    # State
    ############################################################################

    def observer_method(func) -> Callable:  # noqa
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):  # noqa
            self.writer.write_header(self.name)
            state = kwargs.get("state")
            self.state_update(state)
            results = func(self, *args, **kwargs)
            return results

        return wrapper

    def state_update(self, state) -> None:  # noqa
        self.set_iteration_counter(state.get_iteration_counter())

    ############################################################################
    # Iteration counter methods:
    ############################################################################

    def get_iteration_counter(self) -> int:
        return self.iteration_counter

    def set_iteration_counter(self, iteration_count: int) -> None:
        self.iteration_counter = iteration_count

    def check_iteration_counter(self, count: int) -> bool:
        if self.iteration_counter is None:
            return True
        return self.iteration_counter >= count

    ############################################################################
    # Checker
    ############################################################################

    def do_check(self, **kwargs) -> bool:
        """
        Check if the method will run or just do nothing this iteration.

        Returns
        -------
        bool
            True if function will run, False otherwise.w
        """
        return True

    ############################################################################
    # Candidate instanstiator
    ############################################################################

    def set_candidate_instanstiator(self, candidate_instanstiator: StandardCandidate) -> None:
        self.candidate_instanstiator = copy(candidate_instanstiator)
