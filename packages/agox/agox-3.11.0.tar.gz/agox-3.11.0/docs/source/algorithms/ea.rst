Evolutionary algorithm
=======================

In an evolutionary algorithm a population is 'evolved' following a fitness 
criteria, this is kept track of in AGOX by a sampler. The algorithm is rather 
similar to a basin-hopping algorithm in terms of the overall elements, but some 
of the individual elements are slightly different. If the population has size *N*
the script below does the following: 

- Generate *N* candidates using the population. 
- Locally optimize the *N* candidates. 
- Store *N* candidates in the database. 
- Update the population. 

A key difference in the script below compared to basin-hopping script is that 
the sampler is not given as an argument to AGOX but rather attached to database. 

.. literalinclude:: ../../../agox/test/run_tests/tests_ea/script_ea.py
   
.. warning::
   The script showcased here is intended to require little computational effort and therefore uses 
   use an Effective Medium Theory (EMT) potential, which is not suitable for 
   actual studies of materials properties. Please replace the `calculator` with 
   a more accurate potential before using the script for any serious calculations.
   See :ref:`MOD_ALGO` for additional details on how to make such changes.
