from typing import Callable

import numpy as np
from ase.calculators.calculator import all_properties
from ase.calculators.singlepoint import SinglePointCalculator
from ase.constraints import FixAtoms
from ase.optimize import BFGS
from ase.optimize.optimize import Optimizer

from agox.candidates import Candidate
from agox.models import Model
from agox.postprocessors.ABC_postprocess import PostprocessBaseClass
from agox.postprocessors.ray_relax.remote_relax import RelaxationResult, remote_relax
from agox.utils.ray import RayPoolUser, Task


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
    actor_message_function : callable
        Function that creates a message that will be printed. The function
        must takes: candidate, optimizer, model as arguments and return a string or
        a list of strings.
    trajectory: bool
        Whether or not trajectories are returned by the remote relaxation function.
    """

    name = "PoolRelaxer"

    def __init__(
        self,
        model: Model = None,
        optimizer: Optimizer | None = None,
        optimizer_kwargs: dict | None = None,
        optimizer_run_kwargs: dict | None = None,
        fix_template: bool = True,
        constraints: list | None = None,
        start_relax: int = 1,
        actor_message_function: Callable | None = None,
        trajectory: bool = False,
        trajectory_function: Callable | None = None,
        **kwargs,
    ) -> None:
        RayPoolUser.__init__(self)
        PostprocessBaseClass.__init__(self, **kwargs)

        # Optimizer settings:
        self.optimizer = BFGS if optimizer is None else optimizer
        self.optimizer_kwargs = optimizer_kwargs if optimizer_kwargs is not None else {"logfile": None}
        self.optimizer_run_kwargs = (
            optimizer_run_kwargs if optimizer_run_kwargs is not None else {"fmax": 0.05, "steps": 200}
        )
        self.start_relax = start_relax

        # Model
        self.model = model
        self.model_key = self.pool_add_module(model)

        # Constraints:
        self.constraints = constraints if constraints is not None else []
        self.fix_template = fix_template
        self.actor_message_function = actor_message_function

        # Dealing with trajectories.
        self.trajectory = trajectory
        self.set_trajectory_function(trajectory_function)

    def process_list(self, candidates: list[Candidate]) -> list[Candidate]:
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
                function=remote_relax,
                modules=[self.model_key],  # The model is stored on the actors, tell the task where to find it.
                args=[candidate, self.optimizer, self.optimizer_kwargs, self.optimizer_run_kwargs],
                kwargs={"message_function": self.actor_message_function, "trajectory": self.trajectory},
            )
            tasks.append(task)

        relaxed_results = self.task_map(tasks)
        candidates = self._set_results(candidates, relaxed_results)
        self.report_basic_information(relaxed_results)
        self.report_messages(relaxed_results)

        if self.trajectory:
            self.apply_trajectory_function(relaxed_results)

        return candidates

    def postprocess(self, candidate: Candidate) -> Candidate:
        raise NotImplementedError('"postprocess"-method is not implemented, use postprocess_list.')

    def do_check(self, **kwargs) -> bool:
        return self.check_iteration_counter(self.start_relax)

    def _set_results(self, candidates: list[Candidate], results: list[RelaxationResult]) -> None:
        _candidates = []
        for candidate, result in zip(candidates, results):
            if result.relaxation_steps > 0:
                self.remove_constraints(candidate)
                self._set_result_to_candidate(candidate, result)
                _candidates.append(candidate)
        return _candidates

    def _set_result_to_candidate(self, candidate: Candidate, result: RelaxationResult) -> None:
        candidate.set_positions(result.candidate.positions)
        results = {prop: val for prop, val in result.candidate.calc.results.items() if prop in all_properties}
        candidate.calc = SinglePointCalculator(candidate, **results)
        candidate.meta_information.update(result.candidate.meta_information)

    def report_basic_information(self, results: list[RelaxationResult]) -> None:
        steps = np.array([result.relaxation_steps for result in results])
        convergence = np.array([result.converged for result in results])
        max_forces = np.array([result.max_force for result in results])
        improvement = np.array([result.final_energy - result.initial_energy for result in results])


        self.writer(f"{len(results)} candidates relaxed.")
        self.writer("Mean number of steps: {:.1f}".format(steps.mean()))
        self.writer("Std. number of steps: {:.1f}".format(steps.std()))
        self.writer("Mean \N{Greek Capital Letter Delta}E: {:.3f} eV".format(improvement.mean()))
        for idx, delta in enumerate(improvement):
            self.writer.debug(f"Relaxation {idx}: \N{Greek Capital Letter Delta}E = {delta}")
        self.writer(f"Mean max force: {max_forces.mean():.3f}")
        self.writer(f"Std. max force: {max_forces.std():.3f}")
        self.writer(f"Convergence: {convergence.sum()} / {len(convergence)}")

    def report_messages(self, results: list[RelaxationResult]) -> None:
        """
        Print messages from the relaxation results.

        Parameters
        ----------
        results : list
            List of relaxation results.
        """
        for idx, result in enumerate(results):
            if result.message is not None:
                message = "\n".join(result.message)
                self.writer(message)

    def apply_trajectory_function(self, results: list[RelaxationResult]) -> None:
        """
        Apply the trajectory function to the relaxation results. This method 
        calls the trajectory function with the trajectories and the iteration
        counter. May be used to e.g. save the trajectories to disk or print 
        some information about the trajectories.

        Parameters
        ----------
        results : list
            List of relaxation results.

        Returns
        -------
            None
        """
        trajectories = [result.trajectory for result in results]
        iteration = self.get_iteration_counter()
        self._trajectory_function(trajectories, iteration)

    @staticmethod
    def _default_trajectory_function(trajectories: list[list[Candidate]], iteration: int) -> None:
        """
        Default trajectory function that does nothing.
        """
        return None

    def set_trajectory_function(self, function: Callable) -> None:
        """
        Set the function that processes the relaxation trajectories. The function must take
        two arguments: trajectories, iteration. The function should not return anything.
        This will not be called unless `trajectory = True` in the constructor of this 
        class.
        
        Example: That stores the trajectories to disk.

        ```python
        def trajectory_function(trajectories: list[list[Candidate]], iteration: int):
            from ase.io import write
            for index, traj in enumerate(trajectories):
                if traj is not None:
                    write(f"trajectory_iter{iteration}_{index}.traj", traj)
        ```

        Parameters
        ----------
        function : callable
            Function that processes the relaxation trajectories.
        """
        self._trajectory_function = function if function is not None else self._default_trajectory_function


    def set_actor_message_function(self, actor_message_function: Callable) -> None:
        """
        Set the actor message function.

        Example:

        ```python
        def message_function(candidate, optimizer, model) -> str:
            import ray
            message = []
            message.append(f"{ray.get_runtime_context().get_actor_id()}")
            message.append(f"Max force: {candidate.get_forces().max()}")
            return message
        ```

        Parameters
        ----------
        actor_message_function : callable
            Function that creates a message that will be printed. The function
            must takes: candidate, optimizer, model as arguments and return a string or
            a list of strings.
        """
        self.actor_message_function = actor_message_function

    ####################################################################################################################
    # Constraints
    ####################################################################################################################

    def apply_constraints(self, candidate: Candidate) -> None:
        constraints = self.constraints + []
        if self.fix_template:
            constraints.append(self.get_template_constraint(candidate))

        for constraint in constraints:
            if hasattr(constraint, "reset"):
                constraint.reset()

        candidate.set_constraint(constraints)

    def remove_constraints(self, candidate: Candidate) -> None:
        candidate.set_constraint([])

    def get_template_constraint(self, candidate: Candidate) -> FixAtoms:
        return FixAtoms(indices=np.arange(len(candidate.template)))
