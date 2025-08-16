System definition
==================

Environment
-------------

The atomic system that optimized is defined by the following properties
- The atoms being moved around by the search.
- The cell and periodic boundary conditions.
- Any already placed and fixed atoms, such as a slab - a template.
- Which parts of the full cell the search is allowed to place atoms in - confinement.

In the examples these settings are commonly defined by the lines

.. code-block:: 

    template = Atoms("", cell=np.eye(3) * 12)
    confinement_cell = np.eye(3) * 6
    confinement_corner = np.array([3, 3, 3])
    environment = Environment(
        template=template,
        symbols="Au8Ni8",
        confinement_cell=confinement_cell,
        confinement_corner=confinement_corner,
    )

Going line by line this is telling AGOX that

- It is working with an empty template with a cubic cell with sides 12 Angstroms.
- The confinement cell is also but only with a side length of 6 Angstroms.
- The origin of the confinement cell is shifted by 3 Angstrom in every direction relative to the cell.
- All of this is collected into an ```Environment``` and it is additionally specified that the search is dealing with 8 gold and 8 nickel atoms.


Confinement
-------------

One of the most direct ways of limiting the search space is to sensibly choosing the 
confinement settings. In these examples an environment is created and a figure 
showing it is produced by calling ``environment.plot()``. These figures show 
the computational cell with black lines and the confinement cell with red lines.

Cluster
^^^^^^^^^

For a cluster a confinement cell is required to keep generators from placing atoms 
too close to computational cell boundaries. The 'correct' confinement size can be
difficult to guess, however execessively large confinement cells should be avoided 
as they allow unrealistic structures that may yet be local minima and excessively 
small confinement should likewise be avoided as that will make the search focus 
on compact clusters which may be unintendend.

The following code creates an environment with a 12x12x12 Å computational cell and a 
6x6x6 Å confinement cell

.. literalinclude:: ../../../agox/test/modifying_examples/confinement_examples.py
    :language: python
    :start-after: def cluster_confinement():
    :end-before: environment.plot('plots/cluster_confinement.png')
    :tab-width: 0
    :dedent: 4

And produces the following plot

.. figure:: ../../../agox/test/modifying_examples/plots/cluster_confinement.png

Surface films
^^^^^^^^^^^^^^

For surfaces the computational cell typically includes a vacuum region to reduce 
interactions through periodic boundary conditions. For systems where a 
thin film is expected to be the stable solution, it thus necessary to not let 
the search generate structures that span the entire vacuum region. 
Additionally, limiting the confinement region to a reasonable thickness greatly 
improves search performance, by avoiding the generation and evaluation of unrealistic 
configurations with e.g. 'arms' sticking out of the surface.

An example of an environment with such a confinement cell is created by the code below

.. literalinclude:: ../../../agox/test/modifying_examples/confinement_examples.py
    :language: python
    :start-after: def surface_film_confinement():
    :end-before: environment.plot('plots/surface_film_confinement.png')
    :tab-width: 0
    :dedent: 4

Which when plotted looks like so

.. figure:: ../../../agox/test/modifying_examples/plots/surface_film_confinement.png


Adsorped clusters
^^^^^^^^^^^^^^^^^^^

Similarly to the case of surface films, calculations with adsorped clusters also 
include a vacuum region to avoid interactions through periodic boundary conditions in 
the direction normal to the surface. 
However, unlike films adsorped clusters should not be allowed to interact through 
periodic conditions in the directions tangent to the surface either. A suitable 
confinement cell can thus be used to ensure this.

.. literalinclude:: ../../../agox/test/modifying_examples/confinement_examples.py
    :language: python
    :start-after: def surface_cluster_confinement():
    :end-before: environment.plot('plots/surface_cluster_confinement.png')
    :tab-width: 0
    :dedent: 4

And the plotting the resulting environment yields

.. figure:: ../../../agox/test/modifying_examples/plots/surface_cluster_confinement.png

Two-dimensional materials
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For completely two-dimensional (and equivalently one-dimensional) materials the 
confinement can be created to reflect that

.. literalinclude:: ../../../agox/test/modifying_examples/confinement_examples.py
    :language: python
    :start-after: two_d_environment():
    :end-before: environment.plot
    :tab-width: 0
    :dedent: 4
    :emphasize-lines: 7

Which when plotted gives

.. figure:: ../../../agox/test/modifying_examples/plots/two_d_environment.png

Note that in this case, to keep atoms from relaxing out of the plane an additional 
constraint must be specified 

.. code-block:: python

    fixed_plane = [FixedPlane(i, [0, 0, 1]) for i in environment.get_missing_indices()]
    constraints = environment.get_constraints() + fixed_plane

Which should be passed to relevant modules, such as relaxation or evaluation.

Constraints
-------------

Constraints are used for controlling how atoms are allowed to move during relaxations. 
The two most important constraints are 

- ``FixAtoms``: Fixes an atom to its given position, typically set on template atoms. 
- ``BoxConstraint``: Only allows an atom to move in such a way that it remains in the confinement cell.

Though other ``ASE`` constraints can be used as well. The figures produced `enviornment.plot()` 
indicate fixed atoms with a cross. 

Free top layer
^^^^^^^^^^^^^^^^^

Sometimes a surface reconstruction is so consequential that siginificant repositioning 
of the top (or more) layer of the clean surface also take place. The top layer 
could be placed by the search algorithm that would mean that they become degrees of freedom that 
the algorithm has to deal with - which will significantly increase the difficulty of the 
optimization prooblem. Instead, it can may be appropriate to let the surface layer 
relax in accordance to the overlayer created by the search algorithm. 

To do this this layer needs to be unfixed, as is done in the code below 

.. literalinclude:: ../../../agox/test/modifying_examples/confinement_examples.py
    :language: python
    :start-after: surface_toplayer_unconstrained()
    :end-before: environment.plot
    :tab-width: 0
    :dedent: 4
    :emphasize-lines: 21,29-30

Which when plotted gives, where the top layer is now unfixed as evidenced by the lack 
of crosses on those atoms.

.. figure:: ../../../agox/test/modifying_examples/plots/surface_toplayer_unc.png