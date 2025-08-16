from typing import Callable
from uuid import uuid4


class FinalizationHandler:
    """
    Just stores information about functions to be called when finalizaing a run.
    """

    def __init__(self) -> None:
        self.finalization_methods = {}
        self.names = {}

    def attach_finalization(self, name: str, method: Callable) -> None:
        """
        Attaches finalization method.

        Parameters
        -----------
        name: str
            Human readable name of the attached method.
        method: method
            A method or function to attach.
        """
        key = uuid4()
        self.finalization_methods[key] = method
        self.names[key] = name

    def get_finalization_methods(self) -> list:
        """
        Returns
        --------
        List
            List of finalization methods.
        """
        return self.finalization_methods.values()

    def print_finalization(self, include_observer: bool = False, verbose: int = 0) -> None:
        """
        include_observer flag might be useful to debug if something is not working as expected.
        """

        names = [self.names[key] for key in self.finalization_methods.keys()]

        base_string = "{}: order = {} - name = {} - method - {}"
        if include_observer:
            base_string += " - method: {}"

        print("=" * 24 + " Finalization " + "=" * 24)
        for name in names:
            print("Name: {}".format(name))
        print("=" * len("=" * 25 + " Observers " + "=" * 25))
