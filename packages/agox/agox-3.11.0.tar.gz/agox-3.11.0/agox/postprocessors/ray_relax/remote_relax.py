import traceback
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
from ase.calculators.singlepoint import SinglePointCalculator
from ase.optimize.optimize import Optimizer

from agox.candidates import Candidate
from agox.candidates.ABC_candidate import disable_cache
from agox.models import Model


@dataclass
class RelaxationResult:
    candidate: Candidate
    relaxation_steps: int
    max_force: float
    initial_energy: float
    final_energy: float
    converged: bool
    message: list[str] = field(default=None)
    trajectory: list[Candidate] = field(default=None)


def remote_relax(
    model: Model,
    candidate: Candidate,
    optimizer: Optimizer,
    optimizer_kwargs: dict,
    optimizer_run_kwargs: dict,
    message_function: Callable | None = None,
    trajectory: bool = False,
) -> RelaxationResult:
    """
    Relaxes a candidate using the given model and optimizer. Purpose of this function 
    is to be used as a remote function in Ray.

    Parameters
    ----------
    model : agox.models.ABC_model
        Model to use for relaxation.
    candidate : agox.candidates.ABC_candidate
        Candidate to relax.
    optimizer : ase.optimize.Optimizer
        Optimizer to use for relaxation.
    optimizer_kwargs : dict
        Keyword arguments to pass to the optimizer constructor.
    optimizer_run_kwargs : dict
        Keyword arguments to pass to the optimizer.run method.
    message_function : callable
        Function that creates a message that will be printed. The function
        must takes: candidate, optimizer, model as arguments and return a string or
        a list of strings.
    trajectory: bool
        Whether or not trajectories are returned by the remote relaxation function.    
    """
    # Setup the candidate
    _candidate = candidate.copy()
    _candidate.set_calculator(model)
    
    disable_cache(_candidate)

    # Setup the ASE optimizer
    optimizer = optimizer(_candidate, **optimizer_kwargs)

    if trajectory: # Add callback to store trajectory
        _trajectory = []

        def trajectory_callback(atoms: Candidate) -> None:
            traj_atoms = atoms.copy()
            traj_atoms.set_constraint([]) # Make sure to get rid of BoxConstraint.
            calculator = SinglePointCalculator(traj_atoms, **atoms.calc.results)
            traj_atoms.calc = calculator
            _trajectory.append(traj_atoms)

        optimizer.attach(trajectory_callback, interval=1, atoms=candidate)
    else:
        _trajectory = None

    # Run relaxation
    try:
        initial_energy = _candidate.get_potential_energy()
        optimizer.run(**optimizer_run_kwargs)
        n_steps = optimizer.get_number_of_steps()
        gradient = -1 * _candidate.get_forces().flatten()
        converged = optimizer.converged(gradient=gradient)
        final_energy = _candidate.get_potential_energy()
    except Exception as e:
        traceback.print_exc()
        n_steps = -1
        converged = False
        initial_energy = None
        final_energy = None

    _candidate.add_meta_information("relaxation_steps", n_steps)

    # Calculate max force
    forces = _candidate.get_forces()
    max_force = np.linalg.norm(forces, axis=-1).max()

    if message_function is not None: # Create message if message function is given
        message = message_function(_candidate, optimizer, model)
        if not isinstance(message, list):
            message = [message]
    else:
        message = None

    result = RelaxationResult(
        candidate=_candidate,
        relaxation_steps=n_steps,
        max_force=max_force,
        converged=converged,
        message=message,
        trajectory=_trajectory,
        initial_energy=initial_energy,
        final_energy=final_energy,
    )
    return result
