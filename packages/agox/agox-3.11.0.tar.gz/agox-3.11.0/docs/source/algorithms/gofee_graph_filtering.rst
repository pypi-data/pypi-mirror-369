Voroni Graph Filtering
=============================

Example of using graph-based filtering method to remove structures 
from the K-means sampler in a GOFEE search. 

The method uses a classifier to keep track of the evolution of the sample.
If structures with a graph descriptor `G` have been used too many times
to create new candidates, these structures are removed from the pool
of potential sample members.

Various hyperparameters can be varied to control the filtering process.

.. literalinclude:: ../../../agox/test/run_tests/tests_graph_filt/script_graph_filtering_gofee.py

.. warning::
   The script showcased here is intended to require little computational effort and therefore uses 
   use an Effective Medium Theory (EMT) potential, which is not suitable for 
   actual studies of materials properties. Please replace the `calculator` with 
   a more accurate potential before using the script for any serious calculations.
   See :ref:`MOD_ALGO` for additional details on how to make such changes.
