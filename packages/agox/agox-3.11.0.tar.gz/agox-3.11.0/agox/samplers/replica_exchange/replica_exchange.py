from typing import List, Literal, Optional

import numpy as np

from agox.candidates import Candidate
from agox.main.state import State
from agox.models import Model, ModelBaseClass
from agox.observer import Observer
from agox.samplers import SamplerBaseClass
from agox.samplers.replica_exchange import RateTracker, ReplicaExchangeSample


class ReplicaExchangeSampler(SamplerBaseClass):
    name = "RepliceExchangeSampler"

    """
    Replica exchange sampler.

    Parameters
    ----------
    sample_size : int
        Number of members in the sample.
    swap : str
        Method for swapping members. Options are 'up' or 'down'.
    temperatures: List[float]
        List of temperatures to use.
    t_max : float
        Maximum temperature.
    t_min : float
        Minimum temperature.
    swap_interval : int
        Number of iterations between swap attempts.
    swap: Literal["up", "down"]
        Method for swapping members. Options are 'up' or 'down'.
    always_accept : bool
        If True, always accept the new candidate.
    flush_prob : float
        Probability of flushing a member of the sample - to replace it by a new candidate.
        Happens after the model has been updated.
    gets : dict
        Dictionary with the key to get the candidates.
    sets : dict
        Dictionary with the key to set the candidates.
    """

    def __init__(
        self,
        model: Model = None,
        t_min: float = None,
        t_max: float = None,
        sample_size: int = 5,
        swap: Literal["up", "down"] = "up",
        temperatures: Optional[np.ndarray] = None,
        swap_interval: int = 10,
        always_accept: bool = False,
        flush_prob: float = 0.0,
        gets: dict = {"get_key": "candidates", "get_evaluated": "evaluated_candidates"},
        sets: dict = {"set_key": "candidates", "sample_key": "sample"},
        flush_minima: bool = False,
        force_criterion: float = 0.05,
        **kwargs,
    ) -> None:
        super().__init__(gets=gets, sets=sets, **kwargs)

        self._set_temperatures(t_min, t_max, sample_size, temperatures)
        self.sample_size = sample_size
        self.swap_interval = swap_interval
        self.always_accept = always_accept
        self.flush_prob = flush_prob
        self.flush_minima = flush_minima
        self.force_criterion = force_criterion

        self.sample = ReplicaExchangeSample(sample_size)
        self.tracker = RateTracker(sample_size)
        self.reset_observer()  # We remove observers added by the base-class.
        self._add_observers()

        if swap == "up":
            self.swap = self.swap_up
        elif swap == "down":
            self.swap = self.swap_down
        else:
            raise ValueError(f"Swap method '{swap}' not recognized. Use 'up' or 'down'.")

        if model is not None:
            self.attach_to_model(model)

    ############################################################################
    # Observer methods
    ############################################################################

    @Observer.observer_method
    def update_sampler_energies(self, model: Model, state: State) -> None:
        self.writer.debug(
            "Sampler Update", f"{'E0':^8s}", f"{'Edft':^8s}", f"{'Edft-E0':^8s}", f"{'E1':^8s}", f"{'E1-E0':^8s}"
        )

        evaluated_candidates = state.get_from_cache(self, self.get_evaluated)
        dft_uuids = {}
        for cand in evaluated_candidates:
            dft_uuids[cand.get_meta_information("uuid")] = [
                cand.get_meta_information("evaluator_energy"),
                cand.get_meta_information("evaluator_max_force"),
            ]

        iteration = self.get_iteration_counter()
        for i, sample_member in enumerate(self.sample):
            e_dft = np.nan
            if not sample_member.empty():
                uuid = sample_member.candidate.get_meta_information("uuid")
                if uuid in dft_uuids:
                    if iteration in dft_uuids[uuid][0]:
                        e_dft = dft_uuids[uuid][0][iteration]
                e_old = sample_member.get_energy()

                energy = model.predict_energy(sample_member.candidate)  # noqa: N806
                sample_member.energy = energy

            self.writer.debug(
                f"Sample {i} == {sample_member.candidate.get_meta_information('walker_index')}:",
                f"{e_old:8.3f}",
                f"{e_dft:8.3f}",
                f"{e_dft - e_old:8.3f}",
                f"{energy:8.3f}",
                f"{energy - e_old:8.3f}",
            )

        if self.flush_minima:
            for i in range(len(self.sample)):
                uuid = self.sample[i].candidate.get_meta_information("uuid")
                max_force = None
                if uuid in dft_uuids:
                    if iteration in dft_uuids[uuid][1]:
                        max_force = dft_uuids[uuid][1][iteration]
                print(max_force)
                if max_force is not None:
                    if max_force < self.force_criterion:
                        self.sample.update(i, None, np.inf)

        if self.flush_prob > 0.0:
            for i in range(len(self.sample)):
                if np.random.rand() < self.flush_prob:
                    self.sample.update(i, None, np.inf)

    @Observer.observer_method
    def setup_sampler(self, state: State) -> None:
        if self.do_check():
            evaluated_candidates = state.get_from_cache(self, self.get_key)
            evaluated_candidates = list(filter(None, evaluated_candidates))
            if len(evaluated_candidates) > 0:
                self.setup(evaluated_candidates)

        # Overwrite the candidates on the cache as the sampler may have updated meta information.
        state.add_to_cache(self, self.set_key, evaluated_candidates, mode="w")

        sample = [sample_member.candidate for sample_member in self.sample]
        state.add_to_cache(self, self.sample_key, sample, mode="w")

    ############################################################################
    # Setup methods
    ############################################################################

    def setup(self, evaluated_candidates: List[Candidate]) -> None:
        self.update_sample(evaluated_candidates)

        iteration = self.get_iteration_counter()
        if self.decide_to_swap(iteration):
            self.swap()

        if iteration % 1 == 0:
            self.report_statistics()

    def update_sample(self, evaluated_candidates: List[Candidate]) -> None:
        for candidate in evaluated_candidates:
            walker_index = candidate.get_meta_information("walker_index")
            accepted = False
            if self.sample[walker_index].empty():  # Happens either when flushed or when starting.
                accepted = True
            else:  # Regular Metropolis check when not empty.
                parent = self.sample[walker_index]
                temperature = self.temperatures[walker_index]
                accepted = self.metropolis_check(candidate, parent, temperature)

            if accepted:
                energy = candidate.get_potential_energy()
                self.sample.update(walker_index, candidate, energy)

            self.tracker.update_acceptance(walker_index, int(accepted))
            candidate.add_meta_information("accepted", accepted)

    def metropolis_check(self, candidate: Candidate, parent: Candidate, temperature: float) -> bool:
        if self.always_accept:
            return True
        E_candidate = candidate.get_potential_energy()  # noqa
        E_parent = parent.get_energy()  # noqa - Parent is a SampleMember

        if E_candidate < E_parent:
            accepted = True
            P = 1
        else:
            P = np.exp(-(E_candidate - E_parent) / temperature)  # noqa
            accepted = P > np.random.rand()

        return accepted

    ############################################################################
    # Swap methods
    ############################################################################

    def swap_check(self, i: int, j: int) -> bool:
        """
        Check if we should swap the i-th and j-th member of the sample.

        Parameters
        ----------
        i: int
            Index of the first member.
        j: int
            Index of the second member.

        Returns
        -------
        bool
            True if the swap is accepted, False otherwise.
        """
        E_i = self.sample[i].get_energy()  # noqa: N806
        E_j = self.sample[j].get_energy()  # noqa: N806
        beta_i = 1 / self.temperatures[i]
        beta_j = 1 / self.temperatures[j]

        P = np.min([1, np.exp((beta_i - beta_j) * (E_i - E_j))])  # noqa: N806

        return P > np.random.rand()

    def swap_up(self) -> None:
        self.writer("Swapping in 'up' mode")

        # Run over the sample starting from the bottom:
        for i in range(len(self.sample) - 1):
            j = i + 1
            swap_bool = self.swap_check(i, j)

            self.tracker.update_swap_up(i, int(swap_bool))
            self.tracker.update_swap_down(j, int(swap_bool))

            if swap_bool:
                self.sample.swap(i, j)

    def swap_down(self) -> None:
        self.writer("Swapping in 'down' mode")

        # Run over the sample starting from the highest temperature:
        for i in range(len(self.sample) - 1, 0, -1):
            j = i - 1
            swap_bool = self.swap_check(i, j)

            self.tracker.update_swap_up(j, int(swap_bool))
            self.tracker.update_swap_down(i, int(swap_bool))

            if swap_bool:
                self.sample.swap(i, j)

    def decide_to_swap(self, iteration_counter: int) -> bool:
        return iteration_counter % self.swap_interval == 0

    ############################################################################
    # Convenience methods
    ############################################################################

    def report_statistics(self) -> None:
        def float_format(value: float) -> str:
            return f"{value:.2f}"

        columns = ["Member", "Temperature", "Energy", "Accept", "Up", "Down"]
        rows = []
        energies = []
        acceptances = []
        for i in range(self.sample_size):
            swap_up = float_format(self.tracker.get_swap_up_rate(i))
            swap_down = float_format(self.tracker.get_swap_down_rate(i))
            a = self.tracker.get_acceptance_rate(i, start=-10)
            acceptance = float_format(a)
            e = self.sample[i].get_energy()
            energy = float_format(e)
            rows.append([str(i), float_format(self.temperatures[i]), energy, acceptance, swap_up, swap_down])
            acceptances.append(a or 0)
            energies.append(e or 0)

        self.writer.write_table(table_columns=columns, table_rows=rows, expand=True)
        self.writer.debug("Walker energies:   ", " ".join([f"{energy:8.3f}" for energy in energies]))
        self.writer.debug(
            "Walker strengths:  ", " ".join([f"{amplitude:8.3f}" for amplitude in self.tracker.rattle_amplitudes])
        )
        self.writer.debug("Walker acceptances:", " ".join([f"{acceptance:8.3f}" for acceptance in acceptances]))

    def get_walker(self, walker_index: int) -> Candidate:
        walker = self.sample[walker_index]
        if walker.empty():
            return None
        else:
            return walker.candidate.copy()

    def attach_to_model(self, model: Model) -> None:
        assert isinstance(model, ModelBaseClass)
        print(f"{self.name}: Attaching to model: {model}")
        self.attach(model)

    def _set_temperatures(self, t_min: float, t_max: float, sample_size: int, temperatures: np.ndarray) -> None:
        # Temperature logic:
        # Check that they are not all not none:
        if t_max is not None and t_min is not None and temperatures is not None:
            raise ValueError("Either t_max and t_min or temperatures must be provided, not both.")
        elif t_max is not None and t_min is not None:  # If both are provided, generate the temperatures.
            self.temperatures = np.geomspace(t_min, t_max, sample_size)
        elif temperatures is not None:
            if len(temperatures) != sample_size:
                raise ValueError(
                    f"Length of temperatures ({len(temperatures)}) does not match sample size ({sample_size})."
                )
            else:
                self.temperatures = temperatures
        else:
            raise ValueError("Either t_max and t_min or temperatures must be provided.")

    def _add_observers(self) -> None:
        self.add_observer_method(
            self.update_sampler_energies,
            gets=self.gets[0],
            sets=self.sets[0],
            order=self.order[0],
            handler_identifier="model",
        )

        self.add_observer_method(
            self.setup_sampler,
            gets=self.gets[0],
            sets=self.sets[0],
            order=self.order[0],
            handler_identifier="AGOX",
        )
