from typing import List

from agox.observer import Observer
from agox.utils.ray.pool import Task
from agox.utils.ray.pool_startup import get_ray_pool


class RayPoolUser(Observer):
    """
    Mixin to handle the parallelization of AGOX modules using Ray.
    """

    def __init__(self):
        self.pool, ray_stats = get_ray_pool()
        self.cpu_count = ray_stats["CPU"]

    def pool_add_module(self, module, include_submodules=True):
        """
        Parameters
        ----------
        module : AGOX module
            The module being added to the pools modules.

        Returns
        -------
        int
            The key the pool uses for the module.
        """

        if include_submodules:
            submodules = module.find_submodules(only_dynamic=True)
            for submodule in submodules.values():
                self.pool_add_module(submodule)

        return self.pool.add_module(module)

    def pool_remove_module(self, module):
        """
        Parameters
        ----------
        module : AGOX module
            The module being added to the pools modules.
        """
        self.pool.remove_module(module)

    def pool_get_key(self, module):
        """_summary_

        Parameters
        ----------
        module : AGOX module.
            The module for which to retrieve the key.

        Returns
        -------
        int
            Key used for indexing to the module in the pool and on the actors.
        """
        return self.pool.get_key(module)

    def task_map(self, tasks: List[Task]):
        """
        Execute a list of tasks in parallel.

        Parameters
        ----------
        tasks : list of agox.utils.ray.pool.Task
            List of tasks to execute.
        """
        return self.pool.task_map(tasks)

    def pool_map(self, fn, modules, args, kwargs):
        """
        This is method that does the parallelization.

        Parameters
        ----------
        fn : function
            The function to execute in parallel.
        modules : list
            Keys for modules used by fn.
        args : list
            List of positional arguments for each call of the function.
        kwargs : list
            List of keyword arguments for the functions.

        The function 'fn' is executed once pr. set of modules, args and kwargs.
        So these lists must have the same length, and that length is equal to
        the number of parallel tasks - which does not need to equal the number
        of actors in the pool.

        As an example:

            def fn(calculator, atoms):
                atoms.set_calculator(calculator)
                return E = atoms.get_potential_energy()

            modules = [[model_key], [model_key]]
            args = [[atoms1], [atoms2]]
            kwargs = [{}, {}]

            E = pool_map(fn, modules, args, kwargs)

        Calculates the energy of two atoms objects in parallel with the calculator
        that is assumed to be a module on the Actors.

        The args and kwargs may also contain ObjectRefs obtained from ray.put.

        Returns
        -------
        list
            List of the output obtained by applying the function fn to each set
            of modules, args, kwargs.
        """
        return self.pool.map(fn, modules, args, kwargs)

    def pool_get_module_attributes(self, module, attributes):
        """

        Get one or more attributes of a module on the Actors of the pool.

        Parameters
        ----------
        module : AGOX module
            Module to get attributes from.
        attributes : list of str
            Names of the attributes to retrieve.

        Returns
        -------
        list of dicts
            A list containing the dicts that hold the requested attributes.
            The list has length equal to the number of actors and the dicts
            have length equal to the number of requested attributes.
        """
        return self.pool.get_module_attributes(module, attributes)

    def pool_set_module_attributes(self, module, attributes, values):
        """
        Set attributes of a module on the actors of the pool.

        Parameters
        ----------
        module : AGOX module
            Module to get attributes from.
        attributes : list of str
            Names of the attributes to set.
        values : list
            Values to set for each attribute.
        """
        self.pool.set_module_attributes(module, attributes, values)

    def attach(self, handler):
        """
        This method helps getting the pool attached to AGOX without needing
        to do so explicitly in a runscript.

        Parameters
        ----------
        handler : AGOX ObserverHandler instance
            The observer handler to attach to.
        """
        super().attach(handler)

        # Check if has pool:
        if not hasattr(self, "pool"):
            return

        if hash(handler) not in self.pool.attached_handlers:
            self.pool.attach(handler)
            self.pool.print_modules()
            self.pool.update_module_interconnections()
            self.pool.update_modules()
            self.pool.attached_handlers.append(hash(handler))

    def get_pool(self):
        return self.pool

    def pool_synchronize(self, attributes="all", writer=None):
        self.pool.synchronize_module(self, attributes=attributes, writer=writer)

    @classmethod
    def filter_kwargs(cls, kwargs):
        return {key: kwargs.pop(key) for key in cls.kwargs if key in kwargs}
