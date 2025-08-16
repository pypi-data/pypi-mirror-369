Grand Canonical Global Optimization
====================================

In the Grand Canonical Global Optimization algorithm, the objective function 
is not just the total energy but the Gibbs energy while allowing a variable 
number of atoms. 

The algorithm is a GOFEE-type search but now for optimizing the Gibbs energy 
and using a generator that can change the number of atoms.

The algorithm can be outlined as

- Generate candidates either randomly, by rattling or by adding/removing from a population/sample member.
- Relax the generated structures in a surrogate model. 
- Acquire a candidate to calculate with the QM-potential (e.g. DFT) using the lower-confidence bound. 
- Store acquired candidate in the database 
- Update the surrogate model.

The scripts in the dropdown below implement GCGO searches 

.. dropdown:: Search scripts
    :animate: fade-in-slide-down

    .. tab-set::

        .. tab-item:: Quick script / EMT

            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_gcgo/script_gcgo_emt.py

        .. tab-item:: Real script / DFT

            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_gcgo/script_gcgo_dft.py

Analyzing searches with GCGO requires the use of the :code:`ThermodynamicsData`-json file, as shown in the dropdown below.

.. dropdown:: CLI Analysis

    The `agox analysis` command-line interface can be given a path to a :code:`ThermodynamicsData`-json file to base the 
    the calculation of success curves and sorting of the shown structures to be based on the Gibbs energy. 

    .. code-block:: bash

        agox analysis path/to/directory path/to/different/directory -t /path/to/thermodata.json -dE 0.1

    Additionally, only the ``delta-total`` threshold criterion can be used for searches where the number of atoms may vary. 
    The line above will count configurations within 0.1 eV of the lowest energy as a a success.




