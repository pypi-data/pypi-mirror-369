import traceback
from uuid import uuid4

import numpy as np
from ase.calculators.calculator import Calculator
from ase.calculators.singlepoint import SinglePointCalculator
from ase.constraints import FixAtoms
from ase.optimize.bfgs import BFGS
from ase.optimize.optimize import Optimizer

from agox.candidates import Candidate

from .ABC_evaluator import EvaluatorBaseClass


class LocalOptimizationEvaluator(EvaluatorBaseClass):

    name = "LocalOptimizationEvaluator"

    def __init__(
        self,
        calculator: Calculator,
        optimizer: Optimizer = BFGS,
        optimizer_run_kwargs: dict | None = None,
        optimizer_kwargs: dict | None = None,
        fix_template: bool = True,
        constraints: list | None = [],
        store_trajectory: bool = True,
        **kwargs,
    ) -> None:
        """
        Evaluator that performs a local optimization of a candidate using a ASE BFGS optimizer.

        Parameters
        -----------
        calculator: `ase.calculators.calculator.Calculator`
            The calculator to use for the evaluation.
        optimizer: `ase.optimize.optimize.Optimizer`, optional
            The optimizer to use for the local optimization. Default is BFGS.
        optimizer_run_kwargs: dict, optional
            The keyword arguments to pass to the optimizer.run() method. Defaults to 
            `{"fmax": 0.25, "steps": 200}`.
        optimizer_kwargs: dict, optional
            The keyword arguments to pass to the optimizer constructor.
            Defaults to `{"logfile": None}`.
        fix_template: bool, optional
            Whether to fix the template atoms during the optimization. Default is True.
        constraints: list, optional
            List of constraints to apply during the optimization.
        store_trajectory: bool, optional
            Whether to store the trajectory of the optimization. Default is True.
            If False only the last step is stored.
        """
        super().__init__(**kwargs)
        self.calculator = calculator
        self.store_trajectory = store_trajectory

        # Optimizer stuff:
        self.optimizer = optimizer
        self.optimizer_kwargs = optimizer_kwargs if optimizer_kwargs is not None else {"logfile": None}
        self.optimizer_run_kwargs = optimizer_run_kwargs if optimizer_run_kwargs is not None else {"fmax": 0.25, "steps": 200}

        # Constraints:
        self.constraints = constraints

        if self.name == "LocalOptimizationEvaluator":
            if self.optimizer_run_kwargs["steps"] == 0:
                print(
                    f"{self.name}: Running with steps = 0 is equivalent to SinglePointEvaluator, consider using that instead to simplify your runscript."
                )
                self.store_trajectory = False

    def evaluate_candidate(self, candidate: Candidate) -> bool:
        candidate.calc = self.calculator
        try:
            if self.optimizer_run_kwargs["steps"] > 0:
                self.apply_constraints(candidate)
                optimizer = self.optimizer(candidate, **self.optimizer_kwargs)

                # The observer here stores all the steps if 'store_trajectory' is True.
                optimizer.attach(self._observer, interval=1, candidate=candidate, steps=optimizer.get_number_of_steps)

                optimizer.run(**self.optimizer_run_kwargs)
                candidate.add_meta_information("relax_index", optimizer.get_number_of_steps())

                steps = optimizer.get_number_of_steps()
                max_steps = self.optimizer_run_kwargs["steps"]
                E = candidate.get_potential_energy(apply_constraint=False) # noqa: N806
                self.writer(f"Optimization: {self.E_initial:5.3f} ---> {E:5.3f} ({steps}/{max_steps} steps)")

                # If 'store_trajectory' is False we manually store the last step.
                if not self.store_trajectory:
                    self._check_and_append_candidate(candidate)
            else:
                F = candidate.get_forces(apply_constraint=False) # noqa: N806
                E = candidate.get_potential_energy(apply_constraint=False) # noqa: N806
                self._check_and_append_candidate(candidate)

        except Exception as e:
            self.writer("Energy calculation failed with exception: {}".format(e))
            traceback.print_exc()
            return False

        E = candidate.get_potential_energy(apply_constraint=False) # noqa: N806
        F = candidate.get_forces(apply_constraint=False) # noqa: N806
        calc = SinglePointCalculator(candidate, energy=E, forces=F)
        candidate.calc = calc

        return True

    def _observer(self, candidate: Candidate, steps: int) -> None:
        self.check_callback(candidate)  # check before candidate gets copied and assigned a SinglePointCalculator

        E = candidate.get_potential_energy(apply_constraint=False) # noqa: N806
        if steps() == 0:
            self.E_initial = E
        F = candidate.get_forces(apply_constraint=False) # noqa: N806

        traj_candidate = candidate.copy()
        calc = SinglePointCalculator(traj_candidate, energy=E, forces=F)
        traj_candidate.set_calculator(calc)
        traj_candidate.add_meta_information("relax_index", steps())
        traj_candidate.add_meta_information("final", False)
        self._add_time_stamp(traj_candidate)

        if steps() > 0:
            traj_candidate.add_meta_information("uuid", str(uuid4()))

        if self.store_trajectory:
            self.evaluated_candidates.append(traj_candidate)

    def apply_constraints(self, candidate: Candidate) -> None:
        constraints = self.constraints
        candidate.set_constraint(constraints)    

        for constraint in candidate.constraints:
            if hasattr(constraint, 'reset'):
                constraint.reset() 

    def get_template_constraint(self, candidate: Candidate) -> FixAtoms:
        return FixAtoms(indices=np.arange(len(candidate.template)))
