from typing import Callable, List

import numpy as np
import ray


@ray.remote(
    num_cpus=1,
    runtime_env={
        "env_vars": {
            "OMP_NUM_THREADS": "1",
            "OPENBLAS_NUM_THREADS": "1",
            "MKL_NUM_THREADS": "1",
        }
    },
    max_restarts=5,
)
class Actor:
    """
    Basic Ray Actor used by AGOX.
    """

    def __init__(self, actor_id: int = 0):
        self.modules = {}
        self.id = actor_id

    def execute_function(self, fn: Callable, module_keys: List, *args, **kwargs):
        """
        Execute a function on the actor.

        Parameters:
        -----------
        fn: function
            Function to execute.
        module_keys: list
            List of keys to modules to pass to the function.
        args: list
            Arguments to pass to the function.
        kwargs: dict
            Keyword arguments to pass to the function.
        """
        kwargs = self.set_seed(**kwargs)
        return fn(*[self.modules[key] for key in module_keys], *args, **kwargs)

    def set_seed(self, **kwargs):
        """
        Set the seed for the actor.
        """
        seed = kwargs.pop("pool_internal_seed", None)
        if seed is not None:
            np.random.seed(seed)
        return kwargs

    def add_module(self, module, key):
        """
        Add a module to the actor.

        Parameters:
        -----------
        module: AGOX module
            The module to add to the actor.
        key: module.ray_key (uuid).
            The key that references the module on the actors.
        """
        self.modules[key] = module

    def remove_module(self, key):
        """
        Remove a module from the actor.
        """
        del self.modules[key]
