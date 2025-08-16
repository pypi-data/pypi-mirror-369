from typing import Callable

import numpy as np
import pytest
from ase import Atoms
from ase.calculators.emt import EMT

from agox.candidates import Candidate
from agox.environments import Environment
from agox.generators import RandomGenerator
from agox.models import CalculatorModel
from agox.postprocessors import ParallelRelaxPostprocess


@pytest.fixture
def model() -> CalculatorModel:
    return CalculatorModel(calculator=EMT())

@pytest.fixture
def relax_postprocess(model: CalculatorModel) -> ParallelRelaxPostprocess:
    relaxer = ParallelRelaxPostprocess(model=model, 
                                       optimizer_run_kwargs={'steps': 5})
    return relaxer

@pytest.fixture
def candidate_factory() -> Callable:

    template = Atoms(cell=np.eye(3)*8)

    environment = Environment(symbols='Cu8', 
                              template=template,
                              confinement_cell=np.eye(3)*10, 
                              confinement_corner=np.ones(3))    
    generator = RandomGenerator(**environment.get_confinement())

    def factory(n=1) -> list[Candidate]:
        return [generator(sampler=None, environment=environment)[0] for _ in range(n)]
    return factory

def test_message_function(capsys, candidate_factory: Callable, relax_postprocess: ParallelRelaxPostprocess) -> None:
    candidates = candidate_factory(n=2)

    def message_function(*args, **kwargs):
        return "Test message"
    
    relax_postprocess.set_actor_message_function(message_function)
    relax_postprocess.process_list(candidates)

    output = capsys.readouterr().out
    assert "Test message" in output

def test_return_trajectory(capsys, candidate_factory: Callable, relax_postprocess: ParallelRelaxPostprocess) -> None:
    candidates = candidate_factory(n=2)
    relax_postprocess.trajectory = True
    relax_postprocess.set_trajectory_function(lambda *args, **kwargs: print("Trajectory function called"))
    relax_postprocess.process_list(candidates)

    output = capsys.readouterr().out
    assert "Trajectory function called" in output

def test_return_trajectory_type(capsys, candidate_factory: Callable, relax_postprocess: ParallelRelaxPostprocess) -> None:
    candidates = candidate_factory(n=2)
    relax_postprocess.trajectory = True

    def trajectory_function(trajectories, iteration):
        assert isinstance(trajectories, list)
        assert isinstance(trajectories[0], list)
        assert isinstance(trajectories[0][0], Atoms)

    relax_postprocess.set_trajectory_function(trajectory_function)
    relax_postprocess.process_list(candidates)

