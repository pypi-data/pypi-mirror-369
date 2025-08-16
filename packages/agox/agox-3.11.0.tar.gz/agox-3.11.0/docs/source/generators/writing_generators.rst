Writing generators
=====================

In order to implement a custom generator a few methods, as specified by the generator base-class, 
need to be written. The main one being the actual logic of the generator

.. literalinclude:: ../../../agox/generators/ABC_generator.py
    :lines: 49-54

This function is given three inputs

* A :code:`candidate` that serves as the object that the generator will alter according to its mechanism.
* A :code:`parents`-list which are the seed structures that generator can use, the :code:`candidate` is identical to the first parent. 
* The :code:`environment` which describes the system, e.g. stoichoimetry, cell and confinement cell. 

The generator should return a list, if the generation was succesful that list should 
contain the one or more candidate objects the generator produced. 

As the number of parents a generator requires is different, e.g. a :code:`RandomGenerator` uses zero parents whereas a 
:code:`RattleGenerator` uses one parent, each individual generator need to implement a function that 
returns the required number of parents: 

.. literalinclude:: ../../../agox/generators/ABC_generator.py
    :lines: 99-112

As an example we can look at the implementation of these functions in the :code:`RattleGenerator`: 

.. literalinclude:: ../../../agox/generators/rattle.py
    :lines: 14-38

Which just implements the logic of rattling, but also uses a number of methods and attributes
defined in the generator base-class:

* :code:`self.dimensionality`: An attribute describing whether the generator is producing three, two or one dimensional configurations. For two dimensions it is assume the generation will be done in the xy-plane and in one dimension on the x-axis.
* :code:`self.get_displacement_vector(radius)`: A function to produce a vector of length :code:`radius` obeying the dimensionality. 
* :code:`self.check_confinement(suggested_position).all()`: Returns :code:`True` if the :code:`suggested_position` is within the confinement cell, and :code:`False` otherwise. 
* :code:`self.check_new_position(..)`: Checks whether an atom placed at :code:`suggested_position` is within a range of valid bond lengths. 

Generally it is adviced that generators ensure that atoms are placed within the confinement box and with valid bond lengths, 
by using the last two of these methods. 

Because the :code:`RattleGenerator` only uses one seed/parent structure the other method is simply:

.. literalinclude:: ../../../agox/generators/rattle.py
    :lines: 54-55


