Basin hopping
==============

In basin hopping a sampler is used to keep track of a previously evaluated 
candidate which informs the generation of a new candidate. The algorithm 
involves the following steps in each iteration 

- Generate a candidate by rattling a previous candidate. 
- Locally optimize the generated candidate. 
- Check Metropolis criterion to determine if the new candidate is accepted as the starting point for generation. 
- Store the candidate in the database. 

Below scripts implementing basin-hopping in AGOX for several systems and calculators are 
presented.

.. tab-set::
   :class: sd-border-2 sd-pl-1 sd-rounded-2

   .. tab-item:: Cluster

      For a cluster we confine the search to happen in the smaller confinement 
      cell centered on the computational cell. This ensures that no atoms are 
      too close to the cell walls which can lead to issues with DFT codes. 

      .. script-tab-set:: 

         .. tab-item:: EMT

            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_cluster_emt.py

         .. tab-item:: CHGNet
            
            |CHGNet|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_cluster_chgnet.py

         .. tab-item:: GPAW

            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_cluster_gpaw.py

         .. tab-item:: ORCA

            |ORCA|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_cluster_orca.py

         .. tab-item:: VASP

            |VASP|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_cluster_vasp.py



   .. tab-item:: Surface

      For a surface a slab is commonly used as the template, the confinement cell is 
      sized and placed such that free atoms are only placed on one side. 
      Both the computational cell and the confinement cell are periodic in x and y 
      for appropriate description of interactions and for relaxations to be allowed 
      across periodic boundaries. 

      The lattice is kept fixed, so cell parameters are not optimized. 

      .. script-tab-set:: 

         .. tab-item:: EMT

            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_surface_emt.py

         .. tab-item:: CHGNet

            |CHGNET|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_surface_chgnet.py

         .. tab-item:: GPAW

            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_surface_gpaw.py

         .. tab-item:: VASP

            |VASP|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_surface_vasp.py


   .. tab-item:: Bulk

      For a bulk system the confinement cell is chosen to match the computational
      cell specified by the, in this example empty, template. 

      Note that only the atomic positions are degrees of freedom, the lattice 
      is kept fixed and thus not part of the optimization.

      .. script-tab-set:: 

         .. tab-item:: EMT

            |EMT|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_bulk_emt.py

         .. tab-item:: CHGNet

            |CHGNet|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_bulk_chgnet.py

         .. tab-item:: GPAW

            |GPAW|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_bulk_chgnet.py

         .. tab-item:: VASP

            |VASP|

            .. literalinclude:: ../../../agox/test/run_tests/tests_bh/script_bh_bulk_vasp.py
