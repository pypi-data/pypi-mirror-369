from functools import partial
from typing import List

import numpy as np

from agox.candidates import StandardCandidate
from agox.models.ABC_model import ModelBaseClass
from agox.samplers.ABC_sampler import SamplerBaseClass
from agox.utils.thermodynamics import ThermodynamicsData, gibbs_free_energy


class GibbsFreeEnergySampler(SamplerBaseClass):
    name = "GFESampler"

    def __init__(
        self,
        model: ModelBaseClass,
        thermo_data: ThermodynamicsData,
        sample_size: int = 20,
        gets: dict = {"get_key": "evaluated_candidates"},
        order: int = 6,
        **kwargs,
    ):
        super().__init__(gets=gets, order=order, **kwargs)
        self.sample_size = sample_size
        self.model = model
        self.gfe = partial(gibbs_free_energy, thermo_data=thermo_data)

    def get_random_member(self) -> StandardCandidate:
        idx = np.random.randint(0, len(self.sample))
        return self.sample[idx].copy()

    def setup(self, all_candidates: List[StandardCandidate]) -> None:
        idx = np.argsort([self.gfe(c, self.model.predict_energy(c)) for c in all_candidates])
        self.sample = [all_candidates[i] for i in idx][: min(self.sample_size, len(idx))]
