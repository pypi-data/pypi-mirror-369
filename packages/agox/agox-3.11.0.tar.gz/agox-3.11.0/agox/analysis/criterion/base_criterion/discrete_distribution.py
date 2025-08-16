import warnings

import numpy as np
from scipy.stats import CensoredData, ecdf


class DiscreteDistribution:
    def __init__(self, times: np.ndarray, events: np.ndarray):
        self.succcesful = times[np.where(events == 1)]
        self.censored = times[np.where(events == 0)]

        self.rv = CensoredData(self.succcesful, right=self.censored)
        self.ecdf = ecdf(self.rv)

        self.times = times
        self.events = events

    def cdf(self) -> np.ndarray:
        cdf = self.ecdf.cdf.probabilities
        cdf = np.concatenate([[0], cdf])
        return cdf

    def quantiles(self) -> np.ndarray:
        quantiles = self.ecdf.cdf.quantiles
        quantiles = np.concatenate([[0], quantiles])
        return quantiles

    def lower(self, alpha: float = 0.95) -> np.ndarray:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            lower = self.ecdf.cdf.confidence_interval(alpha).low.probabilities

        lower = np.concatenate([[0], lower])
        return lower

    def upper(self, alpha: float = 0.95) -> np.ndarray:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            upper = self.ecdf.cdf.confidence_interval(alpha).high.probabilities
        upper = np.concatenate([[0], upper])
        return upper

    def pmf(self) -> np.ndarray:
        pmf = np.zeros_like(np.unique(self.times))

        for i, t in enumerate(np.unique(self.times)):
            pmf[i] = np.sum(self.events[self.times == t])

        pmf = pmf / len(self.events)

        return pmf
