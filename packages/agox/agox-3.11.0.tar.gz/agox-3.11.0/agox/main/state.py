# Copyright 2021-2024, Mads-Peter V. Christiansen, Bjørk Hammer, Nikolaj Rønne.
# This file is part of AGOX.
# AGOX is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# AGOX is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with AGOX. If not, see <https://www.gnu.org/licenses/>.

from collections import OrderedDict
from copy import deepcopy
from typing import Any, List, Literal

from agox.observer import Observer


class State:
    def __init__(self) -> None:
        """
        State object.

        Attributes
        ----------
        cache: dict
            Data communicated between modules is stored in the cache.
        iteration_counter: int
            Keeps track of the number of iterations.
        convergence: bool
            Convergence status, if True the iteration-loop is halted.
        """

        self.cache = {}
        self.execution_times = {}
        self.iteration_counter = 1
        self.converged = False

    def get_iteration_counter(self) -> int:
        """
        Returns
        -------
        int
            The current iteration number.
        """
        return self.iteration_counter

    def set_iteration_counter(self, count: int) -> None:
        """_summary_

        Parameters
        ----------
        count : int
            Iteration count
        """
        self.iteration_counter = count

    def advance_iteration_counter(self) -> None:
        """
        Adds one to the iteration counter.
        """
        self.iteration_counter += 1

    def get_from_cache(self, observer: Observer, key: str) -> List[Any]:
        """

        Gets from the cache with the given key. The observed is passed along
        aswell in order to ensure that the observer is allowed to get with
        that key.

        Parameters
        ----------
        observer : class object
            An AGOX Observer object, e.g. an instance of a Sampler.
        key : str
            The key with which to get something from the cache.

        Returns
        -------
        list
            List of things stored with the given key.
        """
        # Makes sure the module has said it wants to get with this key.
        assert key in observer.get_values
        return deepcopy(self.cache.get(key))

    def add_to_cache(self, observer: Observer, key: str, data: List[Any], mode: Literal["w", "a"]) -> None:
        """
        Add data to the cache.

        Parameters
        ----------
        observer : class object
            An AGOX Observer object, e.g. an instance of a Sampler.
        key : str
            The key with which to get something from the cache.
        data : list
            List of data to store in the cache.
        mode : str
            Determines the mode in which the data is added to the cache:
            w: Will overwrite existing data with the same key.
            a: Will append to existing data (if there is existing data).
        """
        assert type(data) is list
        # Makes sure the module has said it wants to get with this key.
        assert key in observer.set_values
        assert mode in ["w", "a"]

        if key in self.cache.keys() and mode != "w":
            self.cache[key] += data
        else:
            self.cache[key] = data

    def clear(self) -> None:
        """
        Clears the current cachce. Called at the end of each iteration.
        """
        self.cache = {}
        self.execution_times = OrderedDict()

    def get_convergence_status(self) -> bool:
        """
        Returns the convergence status.

        Returns
        -------
        bool
            If True convergence has been reached and the main iteration-loop
            will halt.
        """
        return self.converged

    def set_convergence_status(self, state: bool) -> None:
        """
        Set the convergence status.

        Parameters
        ----------
        state : bool
            If True convergence has been reached and the main iteration-loop
            will halt.
        """
        self.converged = state

    def set_execution_time(self, name: str, time: float) -> None:
        """
        Set the execution time of a module.

        Parameters
        ----------
        name : str
            The name of the module.
        time : float
            The execution time of the module.
        """
        self.execution_times[name] = time
