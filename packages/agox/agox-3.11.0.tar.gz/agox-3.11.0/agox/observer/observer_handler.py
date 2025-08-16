from collections import OrderedDict
from typing import Callable, Set, Tuple

import numpy as np

from agox.observer import ObserverMethod
from agox.writer import Writer


class ObserverHandler:
    """
    Base-class for classes that can have attached observers.
    """

    def __init__(self, handler_identifier: str, dispatch_method: Callable) -> None:
        """
        Parameters
        -----------
        handler_identifier: str
            Identifier for the handler.
        dispatch_method: Callable
            Method to dispatch to observers.
        """
        self.writer = Writer()
        self.observers = {}
        self.execution_sort_idx = []
        self.handler_identifier = handler_identifier
        self.set_dispatch_method(dispatch_method)

    ####################################################################################################################
    # General handling methods.
    ####################################################################################################################

    def attach_observer(self, observer_method: ObserverMethod) -> None:
        """
        Attaches an observer, saving it to the internal dict and re-evaluating
        the execution order.

        Parameters
        -----------
        observer_method: object
            An instance of the ObserverMethod class that will be attached.
        """
        self.observers[observer_method.key] = observer_method
        self.evaluate_execution_order()

    def delete_observer(self, observer_method: ObserverMethod) -> None:
        """
        Removes an observer, deleting it from the internal dict and re-evaluating
        the execution order.

        Parameters
        -----------
        observer_method: object
            An instance of the ObserverMethod class that will be attached.
        """
        del self.observers[observer_method.key]
        self.evaluate_execution_order()

    def evaluate_execution_order(self) -> None:
        """
        Evaluates the execution order by sorting the orders of stored
        observers.
        """
        keys = self.observers.keys()
        orders = [self.observers[key]["order"] for key in keys]
        self.execution_sort_idx = np.argsort(orders)

    def get_ordered_observers(self) -> OrderedDict:
        keys = [key for key in self.observers.keys()]
        observers = [self.observers[key] for key in keys]
        ordered_dict = OrderedDict()
        sort_idx = self.execution_sort_idx
        for index in sort_idx:
            ordered_dict[keys[index]] = observers[index]
        return ordered_dict

    def dispatch_to_observers(self, *args, **kwargs) -> None:
        """
        Dispatch to observers.

        Only rely on the order of execution if you have specified the 'order' argument for each observer.
        """
        observers = self.get_ordered_observers()
        for observer_method in observers.values():
            observer_method(*args, **kwargs)

    def set_dispatch_method(self, method: Callable) -> None:
        self.dispatch_method = self.name + "." + method.__name__

    ####################################################################################################################
    # Printing / Reporting
    ####################################################################################################################

    def print_observers(self, include_observer: bool = False, verbose: int = 0, hide_log: bool = True) -> None:
        """
        Parameters
        -----------
        include_observer: bool (default: False)
            Turns printing of observer name on. Might be useful to debug if
            something is not working as expected.
        verbose: int (default: 0)
            If verbose > 1 then more information is printed.
        hide_log: bool (default: True)
            If True then the LogEntry observers are not printed. Keeps the
            report more clean.
        """

        order_indexs = self.execution_sort_idx
        keys = [key for key in self.observers.keys()]
        names = [obs["name"] for obs in self.observers.values()]
        methods = [obs["method"] for obs in self.observers.values()]
        orders = [obs["order"] for obs in self.observers.values()]

        base_string = "{}: order = {} - name = {} - method - {}"
        if include_observer:
            base_string += " - method: {}"

        self.writer.write_header("Observers")
        for idx in order_indexs:
            self.writer("  Order {} - Name: {}".format(orders[idx], names[idx]))
            if verbose > 1:
                self.writer("  Key: {}".format(keys[idx]))
                self.writer("  Method: {}".format(methods[idx]))
                self.writer("_" * 50)

    def observer_reports(self, report_key: bool = False, hide_log: bool = True) -> None:
        """
        Generate observer report, which checks if the data flow is valid.

        Parameters
        -----------
        report_key: bool
            Whether or not to print the keys used to get or set from the cache.
        hide_log: bool
            Whether or not to print the LogEntry observers.
        """
        dicts_out_of_order = [value for value in self.observers.values()]

        self.writer.write_header("Observers set/get reports")

        base_offset = "  "
        extra_offset = base_offset + "    "
        for i in self.execution_sort_idx:
            observer_method = dicts_out_of_order[i]

            self.writer(base_offset + observer_method.name)
            report = observer_method.report(
                offset=extra_offset, report_key=report_key, print_report=False, return_report=True
            )
            for string in report:
                self.writer(string)

        get_set, set_set = self.get_set_match()
        self.writer(base_offset)
        self.writer(base_offset + "Overall:")
        self.writer(base_offset + f"Get keys: {get_set}")
        self.writer(base_offset + f"Set keys: {set_set}")
        self.writer(base_offset + f"Key match: {get_set==set_set}")
        if not get_set == set_set:
            self.writer(base_offset + "Sets do not match, this can be problematic!")
            if len(get_set) > len(set_set):
                self.writer(base_offset + "Automatic check shows observers will attempt to get un-set item!")
                self.writer(base_offset + "Program likely to crash!")
            if len(set_set) > len(get_set):
                self.writer(base_offset + "Automatic check shows observers set value that is unused!")
                self.writer(base_offset + "May cause unintended behaviour!")

            unmatched_keys = list(get_set.difference(set_set)) + list(set_set.difference(get_set))
            self.writer(base_offset + f"Umatched keys {unmatched_keys}")

    def get_set_match(self) -> Tuple[Set, Set]:
        """
        Check if gets and sets match.
        """
        dicts_out_of_order = [value for value in self.observers.values()]
        all_sets = []
        all_gets = []

        for observer_method in dicts_out_of_order:
            all_sets += observer_method.sets.values()
            all_gets += observer_method.gets.values()

        all_sets = set(all_sets)
        all_gets = set(all_gets)

        return all_gets, all_sets
