import traceback

import numpy as np
from ase.calculators.calculator import all_properties
from ase.calculators.singlepoint import SinglePointCalculator
from ase.constraints import FixAtoms
from ase.optimize import BFGS

from agox.candidates.ABC_candidate import disable_cache
from agox.postprocessors.ABC_postprocess import PostprocessBaseClass
from agox.utils.ray import RayPoolUser, Task


def relax(model, candidate, optimizer, optimizer_kwargs, optimizer_run_kwargs):
    candidate = candidate.copy()
    candidate.set_calculator(model)
    disable_cache(candidate)
    optimizer = optimizer(candidate, **optimizer_kwargs)
    try:
        optimizer.run(**optimizer_run_kwargs)
    except Exception as e:
        traceback.print_exc()
        print("Relaxation failed with exception: {}".format(e))
        candidate.add_meta_information("relaxation_steps", -1)
        return candidate
    candidate.add_meta_information("relaxation_steps", optimizer.get_number_of_steps())
    return candidate


class ParallelRelaxPostprocess(PostprocessBaseClass, RayPoolUser):
    """
    Relaxes candidates in parallel using Ray.

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

    name = "PoolRelaxer"

    def __init__(
        self,
        model=None,
        optimizer=None,
        optimizer_kwargs={"logfile": None},
        optimizer_run_kwargs={"fmax": 0.05, "steps": 200},
        constraints=None,
        start_relax=1,
        **kwargs,
    ):
        RayPoolUser.__init__(self)
        PostprocessBaseClass.__init__(self, **kwargs)

        self.optimizer = BFGS if optimizer is None else optimizer
        self.optimizer_kwargs = optimizer_kwargs
        self.optimizer_run_kwargs = optimizer_run_kwargs
        self.start_relax = start_relax
        self.model = model
        self.constraints = constraints if constraints is not None else []
        self.model_key = self.pool_add_module(model)

    def process_list(self, candidates):
        """
        Relaxes the given candidates in parallel using Ray.

        Parameters
        ----------
        list_of_candidates : listn
            List of AGOX candidates to relax.

        Returns
        -------
        list
            List of relaxed candidates.
        """

        if len(candidates) == 0:
            return candidates

        # Apply constraints.
        [self.apply_constraints(candidate) for candidate in candidates]

        # Make args, kwargs and modules lists:
        tasks = []
        for candidate in candidates:
            # Create task: function, modules, args, kwargs
            task = Task(
                function=relax,
                modules=[self.model_key],  # The model is stored on the actors, tell the task where to find it.
                args=[candidate, self.optimizer, self.optimizer_kwargs, self.optimizer_run_kwargs],
                kwargs={},
            )
            tasks.append(task)

        relaxed_candidates = self.task_map(tasks)

        # Remove constraints & move relaxed positions to input candidates:
        # This is due to immutability of the candidates coming from pool_map.
        [self.remove_constraints(candidate) for candidate in candidates]
        for cand, relax_cand in zip(candidates, relaxed_candidates):
            cand.set_positions(relax_cand.positions)
            results = {prop: val for prop, val in relax_cand.calc.results.items() if prop in all_properties}
            cand.calc = SinglePointCalculator(cand, **results)
            cand.meta_information.update(relax_cand.info)

        # Remove if relaxation failed:
        candidates = [
            cand
            for cand, rcand in zip(candidates, relaxed_candidates)
            if rcand.get_meta_information("relaxation_steps") > 0
        ]

        steps = np.array([candidate.get_meta_information("relaxation_steps") for candidate in relaxed_candidates])
        self.writer(f"{len(relaxed_candidates)} candidates relaxed.")
        self.writer("   Average number of steps: {:.1f}".format(steps.mean()))
        self.writer("   Std. number of steps: {:.1f}".format(steps.std()))

        max_forces = np.array([np.linalg.norm(candidate.get_forces(), axis=1).max(axis=0) for candidate in relaxed_candidates]).mean()
        self.writer(f"   Mean max force: {max_forces.mean():.3f}")
        self.writer(f"   Std. max force: {max_forces.std():.3f}")

        return candidates

    def postprocess(self, candidate):
        raise NotImplementedError('"postprocess"-method is not implemented, use postprocess_list.')

    def do_check(self, **kwargs):
        return self.check_iteration_counter(self.start_relax)

    ####################################################################################################################
    # Constraints
    ####################################################################################################################

    def apply_constraints(self, candidate):
        candidate.set_constraint(self.constraints)

    def remove_constraints(self, candidate):
        candidate.set_constraint([])
