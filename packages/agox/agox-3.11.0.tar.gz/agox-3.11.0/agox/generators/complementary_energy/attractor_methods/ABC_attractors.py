from abc import ABC, abstractmethod

from agox.observer import Observer
from agox.writer import Writer


class AttractorMethodBaseClass(ABC, Observer):
    """
    Baseclass for attractors methods

    Parameters
    -----------
    order: int
        When to update the structures by checking the database
    """

    dynamic_attributes = ["structures"]

    def __init__(self, order=10):
        Observer.__init__(self, order=order)
        self.add_observer_method(self.update, order=self.order[0], sets={}, gets={})

        self.structures = []

    @Observer.observer_method
    def update(self, database, state):
        self.structures = database.get_all_candidates()

    @abstractmethod
    def get_attractors(self, structure):
        pass
