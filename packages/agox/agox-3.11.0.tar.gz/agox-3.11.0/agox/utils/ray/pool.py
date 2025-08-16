from dataclasses import dataclass
from timeit import default_timer as dt
from typing import Callable, Dict, List

import numpy as np

import ray
from agox.module import Module
from agox.observer import Observer
from agox.utils.ray.actor import Actor
from agox.writer import Writer
from ray.util.placement_group import (
    placement_group,
)
from ray.util.scheduling_strategies import PlacementGroupSchedulingStrategy


@dataclass
class Task:
    """
    Task dataclass.

    Parameters
    ----------
    fn: Callable
        Function to execute.
    modules: List
        List of keys to modules to pass to the function.
    args: List
        Arguments to pass to the function.
    kwargs: Dict
        Keyword arguments to pass to the function.
    """

    function: Callable
    modules: List
    args: List
    kwargs: Dict


class Pool(Observer, Module):
    """
    Pool class for managing a pool of actors.

    Pool of actors that can be used to execute functions in parallel.

    The pool is responsible for managing the actors and the modules that are
    attached to the actors. The pool is also responsible for updating the
    modules on the actors.

    Parameters
    ----------
    num_actors : int
        Number of actors in the pool. The number of actors should be equal to
        the number of CPU cores available.
    """

    name = "ParallelPool"

    def __init__(self, num_actors: int, verbose: bool = False):
        Observer.__init__(self)
        Module.__init__(self)

        # agox.modules.Module instances that are added to the pool are stored in a dict,
        # these will be available on the actors using the keys of the dict.
        self.verbose = verbose
        self.modules = {}

        # Start actors: Small wait time in between to avoid overloading the system.a
        self.idle_actors = []

        # Reserve a placement group for the actors.
        pg = self.reserve_placement_group(num_actors)
        self.idle_actors = []
        for actor_id in range(num_actors):
            actor = Actor.options(scheduling_strategy=PlacementGroupSchedulingStrategy(placement_group=pg)).remote(
                actor_id=actor_id
            )
            self.idle_actors.append(actor)

        self.number_of_actors = len(self.idle_actors)
        self.future_to_actor = {}
        self.pending_submits = []
        self.next_task_index = 0

        # Observer methods:
        self.add_observer_method(
            self.update_pool_actors,
            sets={},
            gets={},
            order=100,
            handler_identifier="AGOX",
        )

        self.attached_handlers = []

    ##########################################################################################################
    # Using the pool - mapping out jobs.
    ##########################################################################################################

    def task_map(self, tasks: List[Task]):
        """
        Execute a list of tasks in parallel over the pool of actors.

        Parameters
        ----------
        tasks : list of agox.utils.ray.pool.Task
            List of tasks to execute.
        """
        functions = [task.function for task in tasks]
        module_keys = [task.modules for task in tasks]
        args_fn = [task.args for task in tasks]
        kwargs_fn = [task.kwargs for task in tasks]
        return self.map(functions, module_keys, args_fn, kwargs_fn)

    def map(self, functions: List[Callable], module_keys: List, args_fn: List[List], kwargs_fn: List[Dict]):
        """

        Performs the given function 'fn' in parallel over the pool of actors.

        Parameters
        ----------
        fn : function
            Function to execute on the actors.
        module_keys : list
            Keys indicating which module on the actor is passed to the function.
        args_fn : list of lists.
            Positional arguments passed to 'fn'.
        kwargs_fn : list of dicts
            Keyword-arguments passed to 'fn'.

        Returns
        -------
        list
            List of outputs such that fn(module, args[0], kwargs[0]) is the first
            element of the list.
        """

        if not isinstance(functions, list):
            functions = [functions] * len(module_keys)

        for fn, args, kwargs, module_key in zip(functions, args_fn, kwargs_fn, module_keys):
            kwargs["pool_internal_seed"] = np.random.randint(0, 10e6, size=1)
            self.submit(fn, module_key, args, kwargs)

        # Futures:
        done = False
        all_results = [None for _ in range(len(args_fn))]

        while not done:
            # Use Ray wait to get a result.
            future_ready, _ = ray.wait(list(self.future_to_actor), num_returns=1)

            # Find the actor that was working on that future:
            index, actor = self.future_to_actor.pop(future_ready[0])

            # Return the actor to the idle pool:
            self.idle_actors.append(actor)

            # Now theres a free actor we re-submit:
            if len(self.pending_submits) > 0:
                fn, module_key, args, kwargs = self.pending_submits.pop(0)  # Pop 0 preserves the order.
                self.submit(fn, module_key, args, kwargs)

            # Because the result is ready this is 'instant' and the next job is
            # already queued.
            all_results[index] = ray.get(future_ready[0])

            if len(self.idle_actors) == self.number_of_actors:
                done = True

        # Reset the task index counter.
        self.next_task_index = 0

        return all_results

    def submit(self, fn, module_keys, args, kwargs):
        """
        Submit tasks to the worker-pool.

        Parameters
        ----------
        fn : function-handle
            Function to execute.
        module_keys : valid-key type (probably str is the best choice).
            Used to identify modules on the actor.
        args : list
            Arguments for fn
        kwargs : dict
            Key-word arguments for fn.
        """

        if len(self.idle_actors) > 0:  # Look to see if an idle actor exists.
            actor = self.idle_actors.pop()  # Take an idle actor
            future = actor.execute_function.remote(fn, module_keys, *args, **kwargs)  # Execute.
            future_key = tuple(future) if isinstance(future, list) else future  # Future as key
            self.future_to_actor[future_key] = (self.next_task_index, actor)  # Save
            self.next_task_index += 1  # Increment
        else:  # If no idle actors are available we save the job for later.
            # I am wondering if it would be helpful to put the args/kwargs now
            # Such that they are ready when an actor is available again.
            self.pending_submits.append((fn, module_keys, args, kwargs))

    def execute_on_actors(self, fn, module_key, args, kwargs):
        """
        Execute the function _once_ per actor with the same data.

        This could e.g. be used to set or get parameters.

        Parameters
        ----------
        fn : function
            Function to execute once pr. actor.
        module_key : list
            Modules to sue.
        args : list
            Arguments to pass to fn.
        kwargs : dict
            Key-word argument to pass to fn.

        Returns
        -------
        list
            The results of the evaluating the fn.
        """
        assert len(self.idle_actors) == self.number_of_actors
        futures = []
        for actor in self.idle_actors:
            futures += [actor.execute_function.remote(fn, module_key, *args, **kwargs)]
        return ray.get(futures)

    ##########################################################################################################
    # Managing the pool.
    ##########################################################################################################

    def get_key(self, module):
        """

        Parameters
        ----------
        module : agox.module.Module
            Module to get key for.

        Returns
        -------
        str
            The key of the module
        """
        assert isinstance(module, Module)
        return module.ray_key

    def add_module(self, module):
        """
        Parameters
        ----------
        module : AGOX module
            Module to add to the pool and its actors.

        Returns
        -------
        int
           The key that has been generateed for the module.
        """
        key = self.get_key(module)
        obj_ref = ray.put(module)
        assert len(self.idle_actors) == self.number_of_actors
        futures = [actor.add_module.remote(obj_ref, key) for actor in self.idle_actors]
        ray.get(futures)  # Block to make sure all the actors do this!
        self.modules[key] = module
        return key

    def remove_module(self, module):
        """
        Parameters
        ----------
        module : AGOX module
            Module to remove from the pool and its actors.

        """

        key = self.get_key(module)
        assert len(self.idle_actors) == self.number_of_actors
        futures = [actor.remove_module.remote(key) for actor in self.idle_actors]
        ray.get(futures)  # Block to make sure all the actors do this!
        del self.modules[key]

    @Observer.observer_method
    def update_pool_actors(self, state):
        """
        Responsible for
        1. Updating module attributes on the pool and actors.
        2. Interconnecting modules on the pool and its actors.

        The updating is handled by looking for which attributes of the supplied modules
        are marked as dynamic_attributes. E.g. for a generic AGOX Module:

            from agox.module import Module
            class GenericObserverClass(Module):

                dynamic_attributes = ['parameters']

                def __init__(self):
                    self.parameters = [1, 2, 3]
                    self.static_parameters = [2, 2, 2]

                def update_parameters(self):
                    self.parameters[0] += 1

        In this case only the 'parameters' attribute will be updated as 'static_parameters'
        are not referenced in dynamic_attributes.

        We want to internal modules on the Actors to link to each other if they use
        each other.

        If a module on the pool references another module on the pool, then they
        should also be connected on the Actors.

        Parameters
        ----------
        state : AGOX State object
            An instance of an AGOX State object.
        """
        self.update_modules()

    def monitoring(self, state):
        from ray.util.state import list_actors, summarize_objects

        if not self.include_dashboard:
            return

        context_info = ray.get_runtime_context()
        address = context_info.gcs_address
        tab = "    "
        self.writer("--- General Information ---")
        self.writer(tab + f"Address: {address}")

        self.writer("--- Actor information ---")
        actor_information = list_actors(address=address)
        total_actors = len(actor_information)
        living_actors = 0
        for actor in actor_information:
            if actor["state"] == "ALIVE":
                living_actors += 1
        self.writer(tab + f"Actors: {living_actors}/{total_actors}")

        object_information = summarize_objects(address=address).get("cluster", {})
        self.writer("--- Object information ---")
        for (
            key,
            val,
        ) in object_information.items():
            if key in ["total_objects", "total_size_mb"]:
                self.writer(tab + f"{key}: {val}")

    def update_modules(self):
        """
        Update dynamic attributes of modules on the actors.
        """
        tab = "   "
        update_count = 0
        module_count = 0
        update_time = 0
        for i, module in enumerate(self.modules.values()):
            if not module.self_synchronizing:
                t0 = dt()
                attribute_dict = self.synchronize_module(module, verbose=False)
                t1 = dt()

                update_count += len(attribute_dict)
                update_time += t1 - t0
                module_count += 1 * (len(attribute_dict) > 0)

                if self.verbose:
                    self.writer(tab + f"{i}: {module.name} -> {len(attribute_dict)} updates in {t1-t0:04.2f} s")
                    for j, attribute_name in enumerate(attribute_dict.keys()):
                        self.writer(2 * tab + f"{j}: {attribute_name}")
            else:
                if self.verbose:
                    self.writer(f"{module.name} handles its own synchronization")

        self.writer(f"Total updates: {update_count} in {update_time:04.2f} s for {module_count} modules")
        

    def update_module_interconnections(self):
        """
        Update module interconnections on actors.

        This is done like so for each module in self.modules:
        1. Find all dynamic submodules recursively.
        2. Update the connection on the Actor.
        """
        self.writer("Making module interconnections on actors")

        def interconnect_module(module, reference_module, setting_key):
            module.set_for_submodule(setting_key, reference_module)

        count = 0
        t0 = dt()
        tab = "   "

        # Iterate over all agox.module.Module instances in the pool.
        for module_key, module in self.modules.items():
            # Find submodules that have dynamic attributes.
            submodules = module.find_submodules(only_dynamic=True, top_level=True)
            for setting_key, submodule in submodules.items():
                sub_module_key = self.get_key(submodule)
                modules = [module_key, sub_module_key]
                args = [setting_key]
                self.execute_on_actors(interconnect_module, modules, args, {})

                # Interconnect the modules on the actors.
                self.writer(tab + f"{count}: Connected {module.name} with {submodule.name}")
                att_name = ".".join(setting_key)
                self.writer(2 * tab + f"  Attribute name: {att_name}")
                count += 1
        if count == 0:
            self.writer("No module interconnections found!")
        t1 = dt()
        self.writer(f"Interconnecting time: {t1-t0:04.2f}")

    def print_modules(self):
        tab = "   "
        self.writer("Modules in pool")
        for i, (key, module) in enumerate(self.modules.items()):
            num_dynamic = len(module.dynamic_attributes)
            report_str = tab + f"{i}: " + module.name + f" - Attrs. = {num_dynamic}"
            self.writer(report_str)

    def get_module_attributes(self, module, attributes):
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

        def get_attributes(module, attributes):
            return {attribute: module.__dict__.get(attribute, None) for attribute in attributes}

        return self.execute_on_actors(get_attributes, [self.get_key(module)], [attributes], {})

    def set_module_attributes(self, module, attributes, values):
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

        def set_attributes(module, attributes, values):
            for value, attribute in zip(values, attributes):
                module.__dict__[attribute] = value

        self.execute_on_actors(set_attributes, [self.get_key(module)], [attributes, values], {})

    def synchronize_module(self, module, attributes="all", writer=None, verbose=True):
        """
        Synchronizes a single module so that its dynamic attributes are the same
        on both the main process and the actors.

        If the module is not already on the actors it will be added and subsequent
        calls will synchronize.

        Parameters
        ----------
        module : AGOX module
            Module to synchronize.
        """
        if writer is None:
            writer = self.writer
        if not verbose:
            writer = lambda x: None

        key = self.get_key(module)
        if key in self.modules.keys():
            if attributes == "all":
                attribute_dict = module.get_dynamic_attributes()
            else:
                attribute_dict = {attribute: getattr(module, attribute) for attribute in attributes}
            writer(f"Updating attributes: {[key for key in attribute_dict.keys()]}")
            if len(attribute_dict) > 0:
                t0 = dt()
                self.set_module_attributes(module, attribute_dict.keys(), attribute_dict.values())
                t1 = dt()
                writer(f"Updated {len(attribute_dict)} attributes on Ray Actors in {t1-t0:04.2f} s.")
            return attribute_dict
        else:
            self.add_module(module)
            return {}

    def reset_pool(self):
        while len(self.modules) > 0:
            key = list(self.modules.keys())[0]
            self.remove_module(self.modules[key])

    @staticmethod
    def reserve_placement_group(n_actors, n_cpus=1):
        # Reserve a placement group for the actors.
        bundles = [{"CPU": n_cpus} for _ in range(n_actors)]

        # Create a placement group.
        pg = placement_group(bundles, strategy="PACK")
        ray.get(pg.ready())

        return pg
