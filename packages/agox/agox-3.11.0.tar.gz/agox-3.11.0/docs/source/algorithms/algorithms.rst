.. _Search algorithms:

Search algorithms
================================

Examples of scripts for different algorithms, choices of parameters are 
reasonable but not guaranteed to be optimal for the particular test system 
or any other system. 

All the scripts take an input argument that will be used 
as the database index, as for the Slurm example in the getting started section. 

.. toctree::
   :maxdepth: 1

   rss
   bh
   gofee
   rex
   gcgo
   ea
   gofee_ce
   gofee_graph_filtering
   lgpr_bh

Indepedent searches, seeds and reproducibility.
------------------------------------------------

It is often a good practice to run several independent searches, with different random seeds. To 
facilitate this we suggest settings the seed and database name based on an input argument, e.g. 
from SLURM this can be achieved by replacing the lines

.. code-block:: python

   # Manually set seed and database-index
   seed = 42
   database_index = 0

Where the seed and database index are set manually for reproducibility, with the following lines

.. code-block:: python

   # Using argparse if e.g. using array-jobs on Slurm to do several independent searches.
   from argparse import ArgumentParser
   parser = ArgumentParser()
   parser.add_argument('-i', '--run_idx', type=int, default=0)
   args = parser.parse_args()

   seed = args.run_idx
   database_index = args.run_idx


.. warning::
   The scripts showcased here are intended to require little computational effort and therefore some
   use an Effective Medium Theory (EMT) potential, which is not suitable for 
   actual studies of materials properties. Some examples use various DFT potentials, but the settings may not be suitable for 
   all systems. Please ensure the settings are appropriate for your system or replace the `calculator` with  a more accurate potential before using the scripts for any serious calculations.
   See :ref:`MOD_ALGO` for additional details on how to make such changes.