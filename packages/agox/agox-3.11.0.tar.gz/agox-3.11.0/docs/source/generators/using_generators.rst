Using generators
=================

.. testcode::

    1 + 1
    print(2+2)

.. testoutput::
    
    4


Non-seeded generators
=======================

Generators can be used outside of an AGOX run to make configurations for arbitrary 
environments. The following script show this in the simplest case of using a 
:code:`RandomGenerator`

.. literalinclude:: ../../../agox/test/generator_tests/for_docs/nonseeded_script.py

This involves setting up an environment dictating which atoms the generator 
is to place and in which region of the supercell to place them. Because the 
:code:`RandomGenerator` doesn't need a seed structure we can pass :code:`None`
as the sampler. 

Generators return a list of candidate objects, so printing :code:`candidates` 
might produce something like: 

.. code-block::

    [StandardCandidate(symbols='Ni2Au2Ni2Au2NiAuNi2Au2NiAu', pbc=False, cell=[12.0, 12.0, 12.0])]

Seeded generators
===================

To use a seeded generator, that is a generator that requires one or more 
intitial configurations in order to generate a new candidate, a sampler 
needs to be defined and provided to the generator call. 

.. literalinclude:: ../../../agox/test/generator_tests/for_docs/seeded_script.py

Which again produces an output like: 

.. code-block::

    rattle_candidate = [StandardCandidate(symbols='NiAu2Ni2AuNi3AuNi2Au4', pbc=False, cell=[12.0, 12.0, 12.0])]


.. note:: 

    Generators are not gauranteed to be able to produce valid candidates, e.g. 
    if the confinement cell is small compared to the number of atoms to be placed 
    the generator may need several attempts before producing a valid candidate. 
    If a generator fails to produce a viable candidate it will return an empty 
    list. 
