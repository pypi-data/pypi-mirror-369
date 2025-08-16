:code:`agox analysis`
===============

.. note:: 

   The most up to date help for :code:`agox analysis` is available through `agox analysis --help`.

The analysis tool can read outputs from searches and provide plots of some of the important statistics of a search. 
The tool requires one or more directories containing database files as arguments, e.g. 

.. code-block:: console

    agox analysis <DIRECTORIES>

Which will produce a figure with three subplots

- The best structures for each individual search database - can be cycled through using the arrow left and right arrow keys.
- The success curves for each directory as a function of time.
- The energy of found structures as a function of time.

The tool supports three distinct ways of measuring 'time'. 

- Indices: E.g. the number of calculations of the objective function (e.g. DFT). 
- Iterations: The number of search iterations. This is enabled with the :code:`-it` flag. 
- Time: The wall time. This is enabled with the :code:`-tt` flag and the unit can be set with :code:`-tu`. To convert to CPU time set the number of cores using the `-nc` option.

The criterion for success has several options

- :code:`--delta-total` or :code:`-dE`: The total energy span above the most stable structure to be considered a success.
- :code:`--delta-atom` or :code:`-de`: The energy pr. atom span above the most stable structure to be considered a succcess.
- :code:`--criterion` or :code:`-c`: The criterion to determine success either based on energy or based on the graph. Defaults to energy. To switch to graph use :code:`-c graph`.

For directories with many long searches loading and processing all the files can be somewhat slow, therefore the tool saves 
a condensed file containing only the necessary information the first time it is run. To reload and update this 
file use the :code:`-r` option.

