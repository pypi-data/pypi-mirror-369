Potential / Calculator
=======================

The objective function for a global structure optimization is generally the 
potential energy given by some quantum mechanical description. In AGOX this 
is abstracted to a an ASE calculator. In the listed examples the potential 
is usually based on Effective Medium Theory, as implemented by the ``EMT`` ASE calculator. 
EMT is mostly not suitable for investigation of material properties, but may be 
useful to test the efficacy of a search algorithm.

Changing calculators
----------------------

Replacing the potential is easy, and just requires swapping to a different 
ASE Calculator, e.g in this part

.. code-block::

    ##############################################################################
    # Calculator
    ##############################################################################

    from ase.calculators.emt import EMT

    calc = EMT()

We can replace EMT with GPAW

.. code-block:: 

    ##############################################################################
    # Calculator
    ##############################################################################

    from agox.helpers import SubprocessGPAW

    kwargs = {
        "mode": {"name": "lcao"},
        "xc": "PBE",
        "txt": "dft.txt",
    }

    calc = SubprocessGPAW(**kwargs)

Calculator examples & details
-------------------------------

GPAW
^^^^^^

The GPAW calculator from the ``gpaw``-package expects the calling python script to 
be called with ``mpiexec`` in order to run in parallel using ``mpi4py``. As ``AGOX`` handles parallelization 
in a different way than ``mpi4py`` calling an agox script with ``mpiexec`` will result in errors. 
So in order to use GPAW in parallel the ``SubprocessGPAW``-calculator that is provided with AGOX should be used instead. 

.. code-block:: 

    from agox.helpers import SubprocessGPAW

    calc = SubprocessGPAW(mode={"name": "lcao"},
        xc="PBE",
        txt="dft.txt",
    )

.. warning:: 
    
    It is important that nothing is directly imported from ``gpaw`` as that will mess with parallelization options. 
    Therefore, all options to ``SubprocessGPAW`` must be specified using the text arguments rather 
    than object arguments.