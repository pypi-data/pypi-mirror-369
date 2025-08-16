import numpy as np
from agox.utils.ray_utils import RayPoolUser


class ParallelSum(RayPoolUser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def sum(self, X):
        # Make the jobs:
        N_jobs = X.shape[0]
        modules = [[]] * N_jobs
        args = [[x] for x in X]
        kwargs = [{} for _ in range(N_jobs)]

        # Run the jobs:
        results = self.pool_map(np.sum, modules, args, kwargs)

        return np.array(results)


X = np.random.rand(100, 100)

parallel_sum = ParallelSum(cpu_count=4)
results = parallel_sum.sum(X)

assert (results == np.sum(X, axis=1)).all()
