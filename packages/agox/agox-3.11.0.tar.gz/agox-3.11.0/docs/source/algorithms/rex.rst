Replica Exchange
=================

In Replica exchange a population of walkers are maintained. Each walker explores 
the potential energy surface at a different temperature, with low temperature walkers 
preferentially exploring low energy regions and high temperature walkers being more 
willing to traverse high energy regions. 

The algorithm can be outlined as 

- Generate candidates by rattling each walkers current candidate.
- Locally optimize the generated candidates in a surrogate model.
- Check Metropolis criterion to determine if the new candidate is accepted to replace its parents.
- Check if candidates should be swapped between walkers. 
- Select structures for DFT, possibly no structures.
- Store the candidate in the database. 
- Update surrogate model if there are new structures with DFT energies.

Note that the algorithm uses a pretrained potential as the prior for the surrogate model, 
and it therefore does objective function (e.g. DFT) calculations only rarely - preferring 
to thoroughly explore the surrogate landscape between objective calculations.

The scripts below implement replica exchange searches

.. tabs:: 

    .. tab:: Quick script / EMT

        |EMT|

        .. literalinclude:: ../../../agox/test/run_tests/tests_rex/script_rex_emt.py

    .. tab:: Real script / DFT

        .. literalinclude:: ../../../agox/test/run_tests/tests_rex/script_rex_dft.py




