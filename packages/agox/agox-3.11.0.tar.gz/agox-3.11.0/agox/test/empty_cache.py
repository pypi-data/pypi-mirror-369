from agox.main import State


class FakeObserver:
    def __init__(self):
        self.set_values = ["candidates"]
        self.get_values = ["candidates"]


def test_empty_cache():
    state = State()

    # The state starts with an empty cache.
    assert state.cache == {}

    # The state can add to the cache.
    state.add_to_cache(FakeObserver(), "candidates", [], "w")

    # The state can get from the cache.
    assert state.get_from_cache(FakeObserver(), "candidates") == []
