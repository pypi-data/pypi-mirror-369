from timeit import default_timer as dt
from typing import Any, Callable, Dict, List, Optional, Union
from uuid import uuid4


class ObserverMethod:
    def __init__(
        self,
        class_name: str,
        method_name: str,
        method: Callable,
        gets: Dict,
        sets: Dict,
        order: Union[float, int],
        handler_identifier: str,
    ) -> None:
        """
        ObserverMethod class. Holds all information about the method that an
        observer class attaches to the observer-loop.

        Parameters
        ----------
        name: str
            Name of the class
        method_name: str
            Name of the method.
        method: method
            The method that is called by the observer-loop.
        sets: dict
            Dict containing the keys that the method will set in the cache.
        gets: dict
            Dict containing the keys that the method will get from the cache.
        order: float
            Execution order
        """
        self.class_name = class_name
        self.method_name = method_name
        self.method = method
        self.gets = gets
        self.sets = sets
        self.order = order

        self.name = self.class_name + "." + self.method_name
        self.class_reference = method.__self__
        self.key = uuid4()
        self.handler_identifier = handler_identifier
        self.handler_name = None

    def __getitem__(self, key: str) -> Union[str, Callable, Dict]:
        return self.__dict__[key]

    def __call__(self, *args, **kwargs) -> Any:
        state = kwargs.get("state")
        state.execution_times[self.get_name()] = -dt()
        result = self.method(*args, **kwargs)
        state.execution_times[self.get_name()] += dt()
        return result

    def get_name(self, handler_name: bool = True, class_name: bool = True, method_name: bool = True) -> str:
        name = ""
        if handler_name:
            name += self.handler_name + "."
        if class_name:
            name += self.class_name + "."
        if method_name:
            name += self.method_name
        return name

    def set_handler(self, handler_name: str) -> None:
        self.handler_name = handler_name

    def report(
        self,
        offset: Optional[str] = None,
        report_key: bool = False,
        return_report: bool = False,
        print_report: bool = True,
    ) -> Union[List[str], None]:
        """
        Generate report. Used by ObserverHandler.observer_reports

        Parameters
        ----------
        offset: str
        report_key: bool
            Print the key or not.
        return_report: bool
            Whether to return the report or not.
        print_report: bool
            Whether to print hte print or not.

        Returns
        -------
        List[str] or None:
            If report_key = True then it returns a string otherwise None is returned.
        """
        report = []
        if offset is None:
            offset = ""

        for key in self.gets.keys():
            value = self.gets[key]
            out = offset + f"Gets '{value}'"
            if report_key:
                out += f" using key attribute '{key}'"
            report.append(out)

        for key in self.sets.keys():
            value = self.sets[key]
            out = offset + f"Sets '{value}'"
            if report_key:
                out += f" using key attribute '{key}'"
            report.append(out)

        if len(self.gets) == 0 and len(self.sets) == 0:
            out = offset + "Doesnt set/get anything"
            report.append(out)

        if print_report:
            for string in report:
                print(string)
        if return_report:
            return report
