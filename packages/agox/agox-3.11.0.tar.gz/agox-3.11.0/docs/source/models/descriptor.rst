Descriptors
==================================

At the core of every machine learning potential is a description of
the atomic structure usable for ML regression methods.

In AGOX a descriptor object implements the necessary methods to
calculate feature-vectors based on ASE atoms objects or AGOX candidate
objects. Two distinct classes of descriptors are available: Global and
local. Global descriptors give a single feature-vector per structure
whereas local descriptors gives a feature-vector per atom in the
structure.

A descriptor object is instantiated from an AGOX environment defining
species together with other necessary information. Some descriptors
can be instantiated via class methods for easier use. 

Below is shown two ways of instantiating a global fingerprint
descriptor and two ways of instantiating the local SOAP descriptor.

.. literalinclude:: ../../../agox/test/model_tests/descriptors_api.py
