import ray
import time
from timeit import default_timer as timer

ray.init(num_cpus=4)


@ray.remote
def f(x):
    time.sleep(1)
    return x * x


t0 = timer()
futures = [f.remote(i) for i in range(4)]
t1 = timer()
results = ray.get(futures)
t2 = timer()
print("Time elapsed t1-t0: ", t1 - t0)
print("Time elapsed t2-t1: ", t2 - t1)
