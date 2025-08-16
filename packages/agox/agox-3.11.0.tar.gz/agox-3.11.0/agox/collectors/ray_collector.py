import numpy as np
import ray

from agox.collectors.ABC_collector import CollectorBaseClass
from agox.utils.ray import RayPoolUser, Task


def remote_generate(generator, sampler, environment):
    return generator(sampler, environment)


class ParallelCollector(CollectorBaseClass, RayPoolUser):
    """
    This collector uses a pool of actors to generate candidates in parallel.

    Parameters
    ----------
    num_candidates : dict or list
        If dict, it must have the form {0: [], 500: []} where the keys are the iteration numbers
        and the values are the number of candidates to generate for that iteration.
        If a list it must provide the number of candidates for each generator used.
    """

    name = "PoolParallelCollector"

    def __init__(self, num_candidates=None, **kwargs):
        # Get the kwargs that are relevant for RayPoolUser
        RayPoolUser.__init__(self)
        # Give the rest to the CollectorBaseClass.
        CollectorBaseClass.__init__(self, **kwargs)
        self.num_candidates = num_candidates

        self.generator_keys = []
        for generator in self.generators:
            key = self.pool_add_module(generator)
            self.generator_keys.append(key)

    def make_candidates(self):
        # We need to build the args and kwargs sent to the actors.
        number_of_candidates = self.get_number_of_candidates()

        # We need to determine which generators to use, these are passed
        # as modules to the actors.
        # If sampler is empty and initialized, then use fallback generator
        if self.sampler is not None and len(self.sampler) == 0 and self.sampler.initialized:
            fallback_generator = self.get_fallback_generator()
            generator_id = self.pool_add_module(fallback_generator)
            modules = [[generator_id]] * np.sum(number_of_candidates)
        else:
            # This specifies which module each actor of the pool will use.
            modules = []
            for generator_key, number in zip(self.generator_keys, number_of_candidates):
                modules += [[generator_key]] * number

        sampler_id = ray.put(self.sampler)
        environment_id = ray.put(self.environment)

        tasks = []
        for i in range(np.sum(number_of_candidates)):
            task = Task(function=remote_generate, modules=modules[i], args=[sampler_id, environment_id], kwargs={})
            tasks.append(task)

        candidates = self.task_map(tasks)

        # Flatten the output which is a list of lists.
        flat_candidates = []
        for cand_list in candidates:
            for cand in cand_list:
                flat_candidates.append(cand.copy())
        return flat_candidates

    def get_number_of_candidates(self):
        if type(self.num_candidates) == list:
            return self.num_candidates
        elif type(self.num_candidates) == dict:
            return self.get_number_of_candidates_for_iteration()

    def get_number_of_candidates_for_iteration(self):
        # self.num_candidates must have this form: {0: [], 500: []}
        keys = list(self.num_candidates.keys())
        keys.sort()
        iteration = self.get_iteration_counter()
        if iteration is None:
            iteration = 0

        num_candidates = self.num_candidates[0]  # yes, it must contain 0
        # now step through the sorted list (as long as the iteration is past the key) and extract the num_candidates
        # the last one extracted will be the most recent num_candidates enforced and should apply to this iteration
        for k in keys:
            if iteration < k:
                break
            num_candidates = self.num_candidates[k]
        return num_candidates
