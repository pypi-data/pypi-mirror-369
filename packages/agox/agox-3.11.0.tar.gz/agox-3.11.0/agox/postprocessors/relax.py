import numpy as np
from ase.calculators.calculator import all_properties
from ase.calculators.singlepoint import SinglePointCalculator
from ase.constraints import FixAtoms
from ase.optimize import BFGS

from agox.postprocessors.ABC_postprocess import PostprocessBaseClass


class RelaxPostprocess(PostprocessBaseClass):
    """
    Relaxes candidates using a local optimization algorithm.

    Parameters
    ----------
    model : agox.models.ABC_model
        Model to use for relaxation.
    optimizer : ase.optimize.Optimizer
        Optimizer to use for relaxation.
    optimizer_run_kwargs : dict
        Keyword arguments to pass to the optimizer.run method.
    optimizer_kwargs : dict
        Keyword arguments to pass to the optimizer constructor.
    fix_template : bool
        If True, the template atoms are fixed during relaxation.
    constraints : list
        List of constraints to apply during relaxation.
    start_relax : int
        The iteration to start relaxing candidates.
    """

    name = "PostprocessRelax"

    def __init__(
        self,
        model=None,
        optimizer=None,
        optimizer_kwargs={"logfile": None},
        optimizer_run_kwargs={"fmax": 0.05, "steps": 200},
        constraints=[],
        start_relax=1,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.optimizer = BFGS if optimizer is None else optimizer
        self.optimizer_kwargs = optimizer_kwargs
        self.optimizer_run_kwargs = optimizer_run_kwargs
        self.start_relax = start_relax
        self.model = model

        # Constraints:
        self.constraints = constraints
    
    def postprocess(self, candidate):
        initial_candidate = candidate.copy()
        candidate.set_calculator(self.model)
        self.apply_constraints(candidate)
        optimizer = self.optimizer(candidate, **self.optimizer_kwargs)

        try:
            optimizer.run(**self.optimizer_run_kwargs)
        except Exception as e:
            print("Relaxation failed with exception: {}".format(e))
            return initial_candidate

        candidate.add_meta_information("relaxation_steps", optimizer.get_number_of_steps())

        results = {prop: val for prop, val in candidate.calc.results.items() if prop in all_properties}
        candidate.calc = SinglePointCalculator(candidate, **results)

        print(f"Relaxed for {optimizer.get_number_of_steps()} steps")

        self.remove_constraints(candidate)
        return candidate

    def do_check(self, **kwargs):
        return self.check_iteration_counter(self.start_relax) * self.model.ready_state

    ####################################################################################################################
    # Constraints
    ####################################################################################################################

    def apply_constraints(self, candidate):
        candidate.set_constraint(self.constraints)

    def remove_constraints(self, candidate):
        candidate.set_constraint([])