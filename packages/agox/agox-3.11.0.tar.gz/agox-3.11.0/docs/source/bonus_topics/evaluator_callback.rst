.. _EVAL_CALLBACK:

Evaluator Callback
====================

In the generic case this can be used to discard candidates *after* calculation depending 
on a callback function, e.g. if the SCF of a DFT calculation does not converge

.. code-block:: python 

    from ase.calculators.calculator import CalculationFailed

    def callback(candidate):
        if ...:  # property indicating the candidate did not converge
            raise CalculationFailed('candidate did not converge')

    evaluator = LocalOptimizationEvaluator(
        calc,
        check_callback=callback,
        ...
    )

VASP 
-----

As of Feb. 2025 the ASE VASP calculator does not raise an exception when VASP does 
not converge. This can lead to unphysical structures being added to the search database, 
which can have detrimental effects. 

To avoid this a callback can be created that throws an error when VASP does not converge

.. code-block:: python

    from ase.calculators.calculator import CalculationFailed
    from ase.calculators.vasp import Vasp

    def callback(candidate):
        if isinstance(candidate.calc, Vasp) and not candidate.calc.read_convergence():
            raise CalculationFailed('VASP: SCF not converged')

    evaluator = LocalOptimizationEvaluator(
    calc,
    check_callback=callback,
    ...
    )

Ensuring that candidates with unconverged energies are not added to the database. 


