Parallelization
=======================

In AGOX two levels of parallization are supported: 

- The parallelization of the DFT calculator, e.g. GPAW, using MPI. This is all handled by the DFT calculator itself which needs to spawn an MPI-enabled subprocess. 
- Parallelization of parts of the algorithm itself, this is done through `Ray https://www.ray.io/`. 

This part of the documentation will focus on the latter.

Basics of Ray
--------------

Ray is a modern parallelization framework for Python, which is easier to use than e.g. mpi4py and is faster than the multiprocessing 
standard library. Note that this means that AGOX scripts do not need to be executed with `mpirun` or `mpiexec` but instead with `python`.

Ray works on so-called remote functions that return futures. Theses futures are handles to the actual result of the function call, 
which can be retrieved later. As an example 

.. literalinclude:: basic_ray_example.py
   :language: python
   :linenos:

In this example a remote function is defined and four calls to it are made in parallel. 
This does not execute the calculation but rather schedules it and returns a handle to the result.
The handles can be used to retrieve the actual result later, using `ray.get`.

The output of this script looks like this:

.. code-block:: console

    Time elapsed t1-t0:  0.006430827081203461
    Time elapsed t2-t1:  1.0111539606004953

Here we also see, what looks like the actual call to the function is almost instant and the 
execution of the script continues immmidiately. The execution of the script is not blocked by the
remote functions calls. It is only when we call `ray.get` that the script is blocked until the
result is available.

This way of using Ray requires very little additional code compared to the serial version. 
However, it has a downside: The remote functions are not *stateful*. This means that they cannot
remember anything, which is important e.g. for codes that jit compile functions.

Therefore we instead use Ray using 'actors'. Actors are objects that are created on a remote 
worker and remember their state. They can be used to store e.g. a compiled function.

Stateful workers
------------------

A simple example is shown below:

.. literalinclude:: actor_ray_example.py
   :language: python
   :linenos:

This adds some complexity, as we are now scheduling work between the actors manually. 
However, we gain the statefulness of the actors, which allows us to store compiled functions
or other data that is expensive to move, such as ML models.

The output of this script looks like this:

.. code-block:: console

    [0, 0, 0, 0]
    [1, 0, 0, 0]

AGOX implements a general-purpose Actor that can run any function of any AGOX module remotely, 
with scheduling handled automatically behind the scenes. 

Stateful workers in AGOX 
--------------------------  

We (mostly) dont want different results based on which Actor an AGOX function was 
executed on. Thus the AGOX implementation synchronizes relevant properties between 
remote workers and the main Python process. The stateful behaviour is the recommended 
use of Ray for both `Tensorflow https://docs.ray.io/en/releases-1.11.0/ray-core/using-ray-with-tensorflow.html` and `pytorch https://docs.ray.io/en/releases-1.11.0/ray-core/using-ray-with-pytorch.html`
and does in our experience also yield the best experience (and performance) when combined with Jax.

When using Ray AGOX automatically spawns a number of these general-purpose Actors 
that are all managed by a `Pool`-object. Therefore directly interacting with 
the actors is not necessary, but rather methods of the `Pool` are called. 

Currently there are three modules that implement the use of this `Pool`, namely
- Parallel relaxation in a model potential using `ParallelRelaxPostprocess`. 
- Paralell generation of candidates using `ParallelCollector`. 
- Parallel hyperparameter optimization for `GPR` and `SparseGPR`. 

Writing parallel modules in AGOX 
----------------------------------- 

The simplest example is when we don't actually need the stateful part, this could e.g 
be just adding numbers together like so 

.. literalinclude:: parallel_add.py
   :language: python
   :linenos:

Here we take a 2D array and sum over the columns in parallel. Each parallel 
job has a list of arguments, keyword arguments and modules - which are AGOX modules it 
might use, as well as the function it will execute `np.sum` in this case. 
The class has the `pool_map`-method through inheritance from `RayPoolUser`. 
This method returns the results in order, no thinking about `ray.get` required, 
that is handled behind the scenes. 

If we do need the stateful part, things are a little more complicated consider the 
following example

.. literalinclude:: parallel_network.py
   :language: python
   :linenos:

Here a PyTorch neural network is created, an AGOX module is given that network 
and uses it to make forward-passes in parallel. Note that it is very important 
that the net is added as a `dynamic_attribute` as it will otherwise not be 
properly synchronize. Note that in this example we can still use the `bias` attribute 
in the computation but as it is not added to the `dynamic_attributes`-list changing it 
will lead to a mismatch between parallel and serial execution.

In an AGOX run this synchronization will happen automatically at the end of each 
iteration, but modules can also choose to call the `pool_synchronize` themselves
if they need to synchronize at different times. 

