Gaussian Process Regression
==================================
A GPR model is a non-parametric regression model that is used to fit a
potential energy surface based on a atomistic structure descriptor.

To use a GPR model one has to define a descriptor and a kernel as
shown in the example below. On can choose to use the default
descriptor and kernel parameters or set them yourself.

Furthermore a prior function, which is a standard AGOX model can be
included as well as a filter, that reduces the number of structures
that the model is trained on. Filter can be added to include any
combination desired. Typically an EnergyFilter is sufficient.

Validation data can be added to the model, which is used to print
performance metrics after training. This can be a good idea to gauge
if your model is performing as desired.

The methods for predicting energies, forces and uncertainties are
given for reference. Note that a list of predictions is returned if a
list of Atoms- or Candidate objects are provided and else only the
prediction is returned.

Parallelization using Ray of hyperparameter optimization is performed
as default on all available cores, but can be controlled by additional
keywords. The `n_optimize` keyword defines how many optimization
trajectories should be performed per cpu core. 

.. literalinclude:: ../../../agox/test/model_tests/gpr_api.py

To see how models are loaded check out the Sparse GPR documentation.
		    
.. note::
   The GPR model implemented in AGOX can only be used with global
   features. If one wants to use local features for GAP-style models one
   should use the SparseGPR.




