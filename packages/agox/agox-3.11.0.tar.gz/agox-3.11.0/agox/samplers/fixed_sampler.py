
import numpy as np

from agox.candidates.ABC_candidate import CandidateBaseClass
from agox.samplers.ABC_sampler import SamplerBaseClass


class FixedSampler(SamplerBaseClass):
    """
    Sampler that always returns the same sample.

    Parameters
    ----------
    sample : list
        List of candidates that will be returned by the sampler.
    p : list
        List of probabilities for each candidate in the sample.
        If None, all candidates have equal probability.
    """

    name = "FixedSampler"

    def __init__(self, sample, p=None):
        if isinstance(sample, CandidateBaseClass) or sample is None:
            self.sample = [sample]
        
        if isinstance(sample, list):
            for s in sample:
                assert isinstance(s, CandidateBaseClass), "Sample must be a list of Candidate objects"
            self.sample = sample

        if p is None:
            p = np.ones(len(self.sample)) / len(self.sample)
        else:
            assert len(p) == len(self.sample), "p must have the same length as sample"
            p = np.array(p)

    def setup(self, all_candidates):
        pass

    def has_none(self) -> bool:
        return None in self.sample
