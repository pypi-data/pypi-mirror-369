# Copyright 2021-2024, Mads-Peter V. Christiansen, Bjørk Hammer, Nikolaj Rønne.
# This file is part of AGOX.
# AGOX is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
# AGOX is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
# of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with AGOX. If not, see <https://www.gnu.org/licenses/>.

import atexit  # noqa
from datetime import datetime
from typing import Iterable

import numpy as np

from agox.candidates.standard import CandidateBaseClass, StandardCandidate
from agox.observer import FinalizationHandler, Observer, ObserverHandler
from agox.writer import Writer, get_icon, set_writer_verbosity
from agox.main.state import State


class AGOX(ObserverHandler, FinalizationHandler):
    """
    AGO-X
    Atomistic Global Optimization X
    """

    name = "AGOX"

    def __init__(
        self,
        *args,
        seed: int = None,
        candidate_instanstiator: CandidateBaseClass = None,
        attach: bool = True,
        report: bool = True,
        verbosity: int | None = None,
    ) -> None:
        """
        Parameters
        ----------
        *args : Observer
            Observer objects to attach to AGOX.
        seed : int, optional
            Seed for the random number generator.
        candidate_instanstiator : CandidateBaseClass, optional
            Candidate instanstiator to use, default is StandardCandidate.
        attach : bool, optional
            If True the observers are attached to AGOX.
        report : bool, optional
            If True a report is printed.
        """
        ObserverHandler.__init__(self, handler_identifier="AGOX", dispatch_method=self.run)
        FinalizationHandler.__init__(self)

        if verbosity is not None:
            set_writer_verbosity(verbosity)

        self._observers = list(args)
        self.candidate_instanstiator = candidate_instanstiator or StandardCandidate
        self.writer = Writer()

        if seed is not None:
            self.set_seed(seed)

        # This attaches all Observers
        if attach:
            self.update()

        if report:
            self.report()

    def report(self) -> None:
        icon = get_icon()
        print(icon)
        self.print_observers(hide_log=True)
        self.observer_reports(hide_log=True)

    def update(self) -> None:
        """
        Calls 'attach' on all Observer-objects in 'self.elements' and updates
        the candidate_instanstiator on all Observer-objects in 'self.elements'
        """
        for observer in self._observers:
            if hasattr(observer, "attach"):
                observer.attach(self)
            if hasattr(observer, "set_candidate_instanstiator"):
                observer.set_candidate_instanstiator(self.candidate_instanstiator)

    def set_seed(self, seed: int) -> None:
        if seed is not None:
            np.random.seed(seed)
            self.writer("Numpy random seed: {}".format(seed))

    def print_iteration_header(self, state: "State") -> None:
        print("\n")
        self.writer.write_header("Iteration: {}".format(state.get_iteration_counter()))
        dt = datetime.now()
        self.writer("Time: {}".format(dt.strftime("%H:%M:%S")))
        self.writer("Date: {}".format(dt.strftime("%d/%m/%Y")))

    def run(self, N_iterations: int, verbose=True, hide_log=True) -> None:  # noqa
        """
        Function called by runscripts that starts the actual optimization procedure.

        This function is controlled by modules attaching themselves as observers to this module.
        The order system ensures that modules with lower order are executed first, but no gurantee within each order,
        so if two modules attach themselves both with order 0 then their individual execution order is not guranteed.
        However, an observer with order 0 will always be executed before an observer with order 1.

        The default ordering system is:
        order = 0: Execution order

        All modules that intend to attach themselves as observers MUST take the order as an argument (with a default value(s)),
        so that if a different order is wanted that can be controlled from runscripts. Do NOT change order default values!
        """

        # Main-loop calling the relevant observers.
        state = State()

        # Force print if something crashes the run.
        atexit.register(self.on_failure)

        self.writer.write_header("AGOX run started")

        while state.get_iteration_counter() <= N_iterations and not state.get_convergence_status():
            self.print_iteration_header(state)
            self.dispatch_to_observers(state=state)
            self.print_timings(state)

            state.clear()
            state.advance_iteration_counter()
            self.writer.write_header("Iteration finished")

        # Some things may want to perform some operation only at the end of the run.
        for method in self.get_finalization_methods():
            method()

        # Remove the force print if everything went well.
        atexit.unregister(self.on_failure)

        self.writer.write_header("AGOX run finished")

    def add_observer(self, observer: Observer) -> None:
        """
        Add an observer to the AGOX object.

        Parameters
        ----------
        observer : Observer
            An observer to add to AGOX.
        """

        if not isinstance(observer, Observer):
            raise TypeError(f"Observer must be an instance of Observer: {observer.__name__}")

        self._observers.append(observer)

    def add_observers(self, *observers: Iterable[Observer], update: bool = True, report: bool = True) -> None:
        """
        Add a list of modules to the AGOX object.

        Parameters
        ----------
        modules : list
            A list of modules to be added to the AGOX object.
        """

        for observer in observers:
            self.add_observer(observer)

        if update:
            self.update()

        if report:
            self.report()

    def on_failure(self) -> None:
        """
        This method is called if the the main loop crashes.
        """
        print("RUN FAIL: AGOX run failed.")

    def print_timings(self, state: "State") -> None:
        from rich.table import Table
        from rich.tree import Tree

        self.writer.write_header("Timings")
        total_time = 0
        tree_list = []
        for name, time in state.execution_times.items():
            handler = name.split(".")[0]
            observer = ".".join(name.split(".")[1:2])
            method = ".".join(name.split(".")[2:])        
            tree_list.append([handler, observer, method, time])

            if handler == "AGOX":
                total_time += time

        row_table = Table.grid(expand=True)
        row_table.add_column()
        row_table.add_column(justify="right")
        row_table.add_row("Total time", f"{total_time:05.2f}s [   %  ]")
        tree = Tree(row_table, highlight=True)
        branches = {}
        for index in range(len(tree_list)):
            handler, observer, method, time = tree_list[index]
            percentage = time / total_time * 100
            text1 = f"{observer}.{method}"
            text2 = f"{time:05.2f}s [{percentage:05.2f}%]"

            row_table = Table.grid(expand=True)
            row_table.add_column()
            row_table.add_column(justify="right")
            row_table.add_row(text1, text2)

            if observer not in branches and handler not in branches:
                branches[observer] = tree.add(row_table)
            if handler in branches:
                branches[handler].add(row_table)

        self.writer(tree)






        
