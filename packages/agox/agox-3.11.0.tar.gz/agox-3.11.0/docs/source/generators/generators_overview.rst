Overview of generators
========================

Generators are a key component of a optimization algorithm, as they are 
responsible for generating new candidate configurations and are present 
in all optimization algorithms. 

AGOX has a number of generators implemented currently: 

*  :code:`RandomGenerator`: Produces random structures, taking only bond lengths and the confinement cell into account. 

*  :code:`RattleGenerator`: Takes a previously found structure and displaces some of the atoms from their initial positions.

*  :code:`ReplaceGenerator`: Takes a previously found structure and moves them to new positions. 

*  :code:`PermutationGenerator`: Takes a previously found structure and swaps two atoms of different atomic type. 

*  :code:`ComplementaryEnergyGenerator`: Uses a complementary energy landscape to generate a structure based on a previous structure. 

*  :code:`CenterOfGeometryGenerator`: Moves atoms that are furthest from the center of geometry, can be useful to build clusters. 

*  :code:`ReuseGenerator`: Takes a previously generated, but not evaluated candidate. 

*  :code:`SamplingGenerator`: Takes members of the sample/population without any alterations. 

*  :code:`SteepestDescent`: Takes a structure that has had its true forces evaluated and takes a small step in that direction. 


Most of these generators depend on seed configuration and alter the coordinates, rather than directly placing atoms. 
How these seed candidates are selected are controlled by a :code:`Sampler` that typically selects a 
subset of the currently evaluated structures from the database in some fashion. 
