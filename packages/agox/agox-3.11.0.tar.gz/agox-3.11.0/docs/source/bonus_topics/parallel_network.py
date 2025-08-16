import numpy as np
from agox.utils.ray_utils import RayPoolUser
from agox.module import Module
import torch


def net_forward(parallel_class, x):
    return parallel_class.net(torch.tensor(x, dtype=torch.float64)).detach().numpy() + parallel_class.bias


class SimpleNet(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = torch.nn.Linear(100, 100, dtype=torch.float64)
        self.fc2 = torch.nn.Linear(100, 1, dtype=torch.float64)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.fc2(x)
        return x


class ParallelClass(RayPoolUser):
    dynamic_attributes = ["net"]

    def __init__(self, net, bias, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.net = net
        self.bias = bias

        self.ray_key = self.pool_add_module(self)

    def do_parallel(self, X):
        # Make the jobs:
        N_jobs = X.shape[0]
        modules = [[self.ray_key]] * N_jobs
        args = [[x] for x in X]
        kwargs = [{} for _ in range(N_jobs)]

        # Run the jobs:
        results = self.pool_map(net_forward, modules, args, kwargs)

        return np.array(results)

    def do_serial(self, X):
        return self.net(torch.tensor(X, dtype=torch.float64)).detach().numpy() + self.bias


# Make an instance of the class:
net = SimpleNet()
X = np.random.rand(10, 100)
parallel_class = ParallelClass(net, bias=1, cpu_count=4)

# Predictions:
results_parallel = parallel_class.do_parallel(X)
results_serial = parallel_class.do_serial(X)

# Compare to serial:
np.testing.assert_allclose(results_parallel, results_serial)  # Suceeds.

# Scramblee network:
net = SimpleNet()
parallel_class.net = net

# Synchronize:
parallel_class.pool_synchronize(writer=print)

# Predictions:
results_parallel = parallel_class.do_parallel(X)
results_serial = parallel_class.do_serial(X)

# Compare to serial:
np.testing.assert_allclose(results_parallel, results_serial)  # Succeeds

parallel_class.bias += 1

# Synchronize:
parallel_class.pool_synchronize(writer=print)

# Predictions:
results_parallel = parallel_class.do_parallel(X)
results_serial = parallel_class.do_serial(X)

# Compare to serial:
np.testing.assert_allclose(results_parallel, results_serial)  # Fails
