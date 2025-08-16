import numpy as np

from agox.acquisitors.ABC_acquisitor import AcquisitorBaseClass


class MetaInformationAcquisitor(AcquisitorBaseClass):
    name = "MetaInformationAcquisitor"

    def __init__(self, meta_key, mode="min", **kwargs):
        super().__init__(**kwargs)
        self.meta_key = meta_key
        self.mode = mode

        assert mode in ["max", "min"]  # Either maximize or minimize according to the meta key.

    def calculate_acquisition_function(self, candidates):
        sign = 1 if self.mode == "min" else -1
        fitness = np.zeros(len(candidates))

        for i, candidate in enumerate(candidates):
            fitness[i] = sign * candidate.get_meta_information(self.meta_key)

        return fitness
