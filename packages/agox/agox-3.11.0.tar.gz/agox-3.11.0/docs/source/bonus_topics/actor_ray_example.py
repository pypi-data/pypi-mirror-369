import ray

ray.init(num_cpus=4)


@ray.remote
class Actor:
    def __init__(self):
        self.x = 0

    def inc(self):
        self.x += 1
        return self.x

    def get_value(self):
        return self.x


actors = [Actor.remote() for i in range(4)]

values = ray.get([actor.get_value.remote() for actor in actors])

print(values)

actors[0].inc.remote()

values = ray.get([actor.get_value.remote() for actor in actors])

print(values)
