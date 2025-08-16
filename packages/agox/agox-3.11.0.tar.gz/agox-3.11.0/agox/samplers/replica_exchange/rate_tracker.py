from typing import Optional

import numpy as np


class RateTracker:
    def __init__(self, sample_size: int) -> None:
        self.sample_size = sample_size
        self.acceptance = {i: list() for i in range(sample_size)}
        self.swap_up = {i: list() for i in range(sample_size)}
        self.swap_down = {i: list() for i in range(sample_size)}
        self.rattle_amplitudes = [0] * sample_size

    def update_acceptance(self, sample_index: int, value: int) -> None:
        self.acceptance[sample_index].append(value)

    def update_swap_up(self, sample_index: int, value: int) -> None:
        if sample_index < self.sample_size - 1:
            self.swap_up[sample_index].append(value)

    def update_swap_down(self, sample_index: int, value: int) -> None:
        if sample_index < self.sample_size:
            self.swap_down[sample_index].append(value)

    def get_acceptance_rate(self, sample_index: int, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None) -> float:
        index_slice = slice(start, stop, step)
        return np.mean(self.acceptance[sample_index][index_slice])

    def get_swap_up_rate(self, sample_index: int, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None) -> float:
        index_slice = slice(start, stop, step)
        return np.mean(self.swap_up[sample_index][index_slice])

    def get_swap_down_rate(self, sample_index: int, start: Optional[int] = None, stop: Optional[int] = None, step: Optional[int] = None) -> float:
        index_slice = slice(start, stop, step)
        return np.mean(self.swap_down[sample_index][index_slice])

    def get_swap_up(self, sample_index: int) -> bool:
        if len(self.swap_up[sample_index]) == 0:
            return False
        return bool(self.swap_up[sample_index][-1])

    def get_swap_down(self, sample_index: int) -> bool:
        if len(self.swap_down[sample_index]) == 0:
            return False
        return bool(self.swap_down[sample_index][-1])

    def get_acceptance(self, sample_index: int) -> bool:
        if len(self.acceptance[sample_index]) == 0:
            return False
        return bool(self.acceptance[sample_index][-1])

