from ase.calculators.emt import EMT
from ase.calculators.emt import parameters as emt_parameters

from agox.evaluators.local_optimization import LocalOptimizationEvaluator
from agox.evaluators.single_point import SinglePointEvaluator


def test_default_callback(environment_and_dataset):
    environment, dataset = environment_and_dataset

    evaluator = SinglePointEvaluator(EMT())
    for candidate in dataset:
        if any(symbol not in emt_parameters for symbol in candidate.symbols):
            continue

        assert evaluator.evaluate_candidate(candidate) is True


def test_reject_all(environment_and_dataset, capsys):
    environment, dataset = environment_and_dataset

    def reject_all(candidate):
        raise Exception('rejected')

    evaluator = SinglePointEvaluator(EMT(), check_callback=reject_all)
    for candidate in dataset:
        if any(symbol not in emt_parameters for symbol in candidate.symbols):
            continue

        assert evaluator.evaluate_candidate(candidate) is False

        captured = capsys.readouterr()
        assert captured.out == 'Energy calculation failed with exception: rejected\n'
        assert 'Exception: rejected' in captured.err

    assert len(evaluator.evaluated_candidates) == 0


def test_optimization(environment_and_dataset):
    environment, dataset = environment_and_dataset

    def reject_all(candidate):
        raise Exception('rejected')

    evaluator = LocalOptimizationEvaluator(EMT(), check_callback=reject_all)
    for candidate in dataset:
        if any(symbol not in emt_parameters for symbol in candidate.symbols):
            continue

        assert evaluator.evaluate_candidate(candidate) is False

    assert len(evaluator.evaluated_candidates) == 0
