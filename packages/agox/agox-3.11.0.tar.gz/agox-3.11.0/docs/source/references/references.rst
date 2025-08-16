Citation
===========

If you have used AGOX for a publication please cite

.. tabs::

    .. tab:: Text
        
        Mads-Peter V. Christiansen, Nikolaj Rønne, Bjørk Hammer, 
        `Atomistic Global Optimization X: A Python package for optimization 
        of atomistic structures <https://arxiv.org/abs/2204.01451>`_, J. Chem. Phys. 157, 054701 (2022)

    .. tab:: Bibtex

        .. code-block:: none

	   @article{christiansen2022,
	   author = {Christiansen, Mads-Peter V. and Rønne, Nikolaj and Hammer, Bjørk},
	   title = "{Atomistic global optimization X: A Python package for optimization of atomistic structures}",
	   journal = {The Journal of Chemical Physics},
	   volume = {157},
	   number = {5},
	   pages = {054701},
	   year = {2022},
	   month = {08},
	   issn = {0021-9606},
	   doi = {10.1063/5.0094165},
	   url = {https://doi.org/10.1063/5.0094165},
	   eprint = {https://pubs.aip.org/aip/jcp/article-pdf/doi/10.1063/5.0094165/16548931/054701\_1\_online.pdf},
       }


			
If using the GOFEE algorithm please also cite

.. tabs::

    .. tab:: Text
        
        Malthe K. Bisbo, Bjørk Hammer, `Efficient global structure optimization 
        with a machine-learned surrogate model <https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.124.086102>`_, Phys. Rev. Lett., 124, 086102, (2020)

    .. tab:: Bibtex

        .. code-block:: none

            @article{bisbo2020,
            author = {Bisbo, Malthe K. and Hammer, Bjørk},
            journal = {Phys. Rev. Lett.},
            title = {Efficient global structure optimization 
                with a machine-learned surrogate model},
            volume = {124},
            year = {2020},
            pages = {086102}
            }


If using the local Gaussian regression model, please also cite

.. tabs::

    .. tab:: Text
        
        Nikolaj Rønne, Mads-Peter V. Christiansen, Andreas Møller Slavensky, Zeyuan Tang, Florian Brix, Mikkel Elkjær Pedersen, Malthe Kjær Bisbo, and Bjørk Hammer, 
        `Atomistic structure search using local surrogate model <https://doi.org/10.1063/5.0121748>`_, J. Chem. Phys. 157, 174115 (2022)

    .. tab:: Bibtex
	     
        .. code-block:: none

	     @article{ronne2022,
	     author = {Rønne, Nikolaj and Christiansen, Mads-Peter V. and Slavensky, Andreas Møller and Tang, Zeyuan and Brix, Florian and Pedersen, Mikkel Elkjær and Bisbo, Malthe Kjær and Hammer, Bjørk},
	     title = "{Atomistic structure search using local surrogate model}",
	     journal = {The Journal of Chemical Physics},
	     volume = {157},
	     number = {17},
	     pages = {174115},
	     year = {2022},
	     month = {11},
	     issn = {0021-9606},
	     doi = {10.1063/5.0121748},
	     url = {https://doi.org/10.1063/5.0121748},
	     eprint = {https://pubs.aip.org/aip/jcp/article-pdf/doi/10.1063/5.0121748/16553993/174115\_1\_online.pdf},
	 }

If using the Complementary Energy generation method, please also cite

.. tabs:: 

	.. tab:: Text
		Andreas Møller Slavensky, Mads-Peter V Christiansen, Bjørk Hammer, 
		`Generating candidates in global optimization algorithms using complementary energy landscapes <https://doi.org/10.1063/5.0156218>`_, J. Chem. Phys. 159, 024123 (2023)

	.. tab:: Bibtex

		.. code-block:: none

		@article{slavensky2023,
		author = {Slavensky, Andreas Møller and Christiansen, Mads-Peter V. and Hammer, Bjørk},
		title = "{Generating candidates in global optimization algorithms using complementary energy landscapes}",
		journal = {The Journal of Chemical Physics},
		volume = {159},
		number = {2},
		pages = {024123},
		year = {2023},
		month = {07},
		abstract = "{Global optimization of atomistic structure relies on the generation of new candidate structures in order to drive the exploration of the potential energy surface (PES) in search of the global minimum energy structure. In this work, we discuss a type of structure generation, which locally optimizes structures in complementary energy (CE) landscapes. These landscapes are formulated temporarily during the searches as machine learned potentials (MLPs) using local atomistic environments sampled from collected data. The CE landscapes are deliberately incomplete MLPs that rather than mimicking every aspect of the true PES are sought to become much smoother, having only a few local minima. This means that local optimization in the CE landscapes may facilitate the identification of new funnels in the true PES. We discuss how to construct the CE landscapes and we test their influence on the global optimization of a reduced rutile SnO2(110)-(4  × 1) surface and an olivine (Mg2SiO4)4 cluster for which we report a new global minimum energy structure.}",
		issn = {0021-9606},
		doi = {10.1063/5.0156218},
		url = {https://doi.org/10.1063/5.0156218},
		eprint = {https://pubs.aip.org/aip/jcp/article-pdf/doi/10.1063/5.0156218/18037556/024123\_1\_5.0156218.pdf},
	}