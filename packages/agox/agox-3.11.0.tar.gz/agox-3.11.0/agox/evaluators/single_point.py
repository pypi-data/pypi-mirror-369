from agox.evaluators.local_optimization import LocalOptimizationEvaluator


class SinglePointEvaluator(LocalOptimizationEvaluator):
    """
    Does a single point calculation of a candidate.

    Bases on the LocalOptimizationEvaluator, but with steps=0.

    Parameters:
    -----------
    calculator: ASE calculator
        The calculator to use for the evaluation.
    """

    name = "SinglePointEvaluator"

    def __init__(self, calculator, **kwargs):
        super().__init__(calculator, optimizer_run_kwargs=dict(steps=0), **kwargs)
