Sparse Gaussian Process Regression
==================================
A sparse GPR is a more time efficient GPR model, that uses a number of
inducing points in feature space to both training and inference time. 

The sparse GPR model API inherits from the  GPR model with
additional functionality related to the sparsification of the
model. Hereby all features available on the GPR model are also
available for the sparse GPR model.

The sparsification is performed by a sparsifier object given to the
model. The main difference between a sparsifier and a filter is on
what types of data the data-reduction is performed. Filters select
atoms-type data, whereas sparsifiers select vector type data.

The sparse GPR can be used with both local and global features, where
the first case will result in a GAP-style model.

Beware that the amount of noise is per feature center i.e. per structure
for a global feature and per atom for a local feature.

An example of training the sparse GPR with a local descriptor and CUR
sparsification is given below.

Hyperparameter optimization is not turned on by default, but can be
done by setting `n_optimize=1` or higher for a better hyperparameter search. 

.. literalinclude:: ../../../agox/test/model_tests/sgpr_api.py

.. note::
   As default sparse GPR models only train on energies. Training on
   energies and forces is possible by including a filter, that selects
   force-data. If one wants to train with all available forces use:
   `force_data_filter="all"`. Noise levels is recommended to be set
   individually for energies and forces using `noise_E` and `noise_F`
   keywords. 
		    
As an example, training on forces can be done like so: 

.. literalinclude:: ../../../agox/test/model_tests/sgpr_api_forces.py

To load a model from disk one has to initialize the model object and
load the parameters.

.. literalinclude:: ../../../agox/test/model_tests/load_api.py

.. note::
   If a model should be actively trained during an AGOX run, then the
   model needs to be attached to a database. 

.. note:: 
   If you don't need parallelism for e.g. model hyperparameter optimization, 
   then you can set `use_ray=False` in the model constructor. This will
   disable the Ray parallelization.