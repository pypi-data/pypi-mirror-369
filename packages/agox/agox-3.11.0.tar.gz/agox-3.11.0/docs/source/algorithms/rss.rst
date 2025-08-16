Random structure search 
=========================

The script below runs a 'random structure search' (RSS) type run, consisting of the 
following elemenets in each iteration. 

- Generate a random candidate. 
- Locally optimize that candidate. 
- Add the fully relaxed candidate to the database. 

Below several examples of running RSS for different systems and potentials 
are given. 

.. tab-set:: 
   :class: sd-border-2 sd-pl-1 sd-rounded-2 sd-outline-secondary

   .. tab-item:: Cluster

      For a cluster we confine the search to happen in the smaller confinement 
      cell centered on the computational cell. This ensures that no atoms are 
      too close to the cell walls which can lead to issues with DFT codes. 

      .. script-tab-set::

         .. tab-item:: EMT         

            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_cluster_emt.py

         .. tab-item:: CHGNet

            |CHGNet|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_cluster_chgnet.py

         .. tab-item:: GPAW

            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_cluster_gpaw.py

         .. tab-item:: ORCA
            
            |ORCA|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_cluster_orca.py

         .. tab-item:: VASP

            |VASP|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_cluster_vasp.py


   .. tab-item:: Surface

      For a surface a slab is commonly used as the template, the confinement cell is 
      sized and placed such that free atoms are only placed on one side. 
      Both the computational cell and the confinement cell are periodic in x and y 
      for appropriate description of interactions and for relaxations to be allowed 
      across periodic boundaries. 

      When searching for an overlayer it can be useful to set ``contiguous`` of the 
      ``RandomGenerator`` to ``False`` as that allows the overlayer atoms to nucleate/spawn/be placed at 
      several surfaces sites rather than requiring that they are placed contiguously.   

      If instead of an overlayer an adsorbed cluster is searched for the confinement 
      cell can be reduced. 

      The lattice is kept fixed, so cell parameters are not optimized. 

      .. script-tab-set:: 

         .. tab-item:: EMT
            
            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_surface_emt.py

         .. tab-item:: CHGNet
            
            |CHGNet|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_surface_chgnet.py

         .. tab-item:: GPAW
            
            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_surface_gpaw.py

         .. tab-item:: VASP

            |VASP|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_surface_vasp.py


   .. tab-item:: Bulk

      For a bulk system the confinement cell is chosen to match the computational
      cell specified by the, in this example empty, template. 

      Note that only the atomic positions are degrees of freedom, the lattice 
      is kept fixed and thus not part of the optimization.

      .. script-tab-set::

         .. tab-item:: EMT

            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_bulk_emt.py

         .. tab-item:: CHGNet
            
            |CHGNet|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_bulk_chgnet.py

         .. tab-item:: GPAW

            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_bulk_gpaw.py

         .. tab-item:: VASP

            |VASP|

            .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_cluster_vasp.py


   .. tab-item:: 2D

      AGOX can run searches in three, two and one dimensions. The following script 
      shows how to setup a 2D run, in this case for RSS but the changes apply to any 
      algorithm. 

      This involves: 

      1. Setting the third vector of the confinement cell to zero in all entries. 
      2. Adding an additional FixedPlane constraint. 

      .. literalinclude:: ../../../agox/test/run_tests/tests_rss/script_rss_2d.py


   