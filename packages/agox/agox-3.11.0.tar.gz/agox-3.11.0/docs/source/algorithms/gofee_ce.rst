Complementary Energy
=============================

Example of using a more advanced generator in a GOFEE search. 

Here a `ComplementaryEnergy` generator, which defines a simple 
energy landscape based on local motiffs is used to generate high quality 
candidates. 

It offers a high degree of customization, with options for choosing: 

* The descriptor 
* The energy function
* How attractors are chosen 

.. literalinclude:: ../../../agox/test/run_tests/tests_ce/script_ce_gofee.py
    
If the customization options are not required a class-method is provided to 
create a default `ComplementaryEnergy` generator. 

.. literalinclude:: ../../../agox/test/run_tests/script_ce_default_gofee.py
    :lines: 92-94

.. warning::
   The script showcased here is intended to require little computational effort and therefore uses 
   use an Effective Medium Theory (EMT) potential, which is not suitable for 
   actual studies of materials properties. Please replace the `calculator` with 
   a more accurate potential before using the script for any serious calculations.
   See :ref:`MOD_ALGO` for additional details on how to make such changes.
