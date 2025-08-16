GOFEE 
==============

The GOFEE algorithm is a Bayesian search algorithm first presented by Bisbo & Hammer

In GOFEE *N* candidates are generated each episode and are all locally optimzied 
in a Gaussian process regression (GPR) potential - or in fact in the so-called 
lower-confidence-bound expression given by

.. math::
    E(\mathbf{x}) = \hat{E}(\mathbf{x}) - \kappa \sigma(\mathbf{x})

Where :math:`\hat{E}` and :math:`\sigma` are the predicted energy and uncertainty of the 
GPR model for the structure represented by :math:`\mathbf{x}`. Following that the 
most promising candidate(s) are chosen for evaluation by an acquisitor, that also uses 
the LCB expression - such that those candidates that have low energy and high uncertainty 
are preferentially evaluated. 

Overall the algorithm has the following flow: 

1. Generate *N* candidates. 
2. Locally optimize those candidates in the LCB. 
3. Use the acquisitor to pick candidates for evaluation. 
4. Evaluate a small (usually just 1) number of candidates with only a few (usually 1) gradient-step in the target potential. 
5. Store in the evaluated candidate(s) in the database. 
6. Update the GPR model with the new data. 

Both step 1 and 2 happen in parallel using `Ray <https://www.ray.io/>`_.

.. tab-set:: 
    :class: sd-border-2 sd-pl-1 sd-rounded-2

    .. tab-item:: Cluster

        For a cluster we confine the search to happen in the smaller confinement 
        cell centered on the computational cell. This ensures that no atoms are 
        too close to the cell walls which can lead to issues with DFT codes. 

        .. script-tab-set:: 

            .. tab-item:: EMT

                |EMT|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_cluster_emt.py

            .. tab-item:: CHGNet

                |CHGNet|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_cluster_chgnet.py

            .. tab-item:: GPAW

                |GPAW|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_cluster_gpaw.py

            .. tab-item:: Orca

                |ORCA|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_cluster_orca.py

            .. tab-item:: VASP

                |VASP|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_cluster_vasp.py


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

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_surface_emt.py

            .. tab-item:: CHGNet

                |CHGNet|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_surface_chgnet.py

            .. tab-item:: GPAW

                |GPAW|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_surface_gpaw.py

            .. tab-item:: VASP

                |VASP|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_surface_vasp.py


    .. tab-item:: Bulk

        For a bulk system the confinement cell is chosen to match the computational
        cell specified by the, in this example empty, template. 

        Note that only the atomic positions are degrees of freedom, the lattice 
        is kept fixed and thus not part of the optimization.

        .. script-tab-set:: 

            .. tab-item:: EMT

                |EMT|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_bulk_emt.py

            .. tab-item:: CHGNet

                |CHGNet|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_bulk_chgnet.py

            .. tab-item:: GPAW

                |CHGNet|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_bulk_gpaw.py

            .. tab-item:: VASP

                |VASP|

                .. literalinclude:: ../../../agox/test/run_tests/tests_gofee/script_gofee_bulk_vasp.py
