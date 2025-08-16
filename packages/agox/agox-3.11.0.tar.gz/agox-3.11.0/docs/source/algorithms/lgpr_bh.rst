Local GPR Basin Hopping
=========================

The following script shows how to run a Basin-Hopping search with a local 
GPR model that is trained on the fly and replaces some of the ab-initio calculations. 

.. literalinclude:: ../../../agox/test/run_tests/tests_lgpr_bh/script_lgpr_bh.py

.. warning::
   The script showcased here is intended to require little computational effort and therefore uses 
   use an Effective Medium Theory (EMT) potential, which is not suitable for 
   actual studies of materials properties. Please replace the `calculator` with 
   a more accurate potential before using the script for any serious calculations.
   See :ref:`MOD_ALGO` for additional details on how to make such changes.
