import numpy as np


class ConstantPrior:
    def __init__(self, value=1):
        self.value = value

    def predict_energy(self, candidate):
        return self.value

    def predict_forcces(self, candidate):
        return np.zeros((len(candidate), 3))
