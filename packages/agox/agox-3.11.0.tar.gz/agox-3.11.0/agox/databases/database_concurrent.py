import os
from time import sleep

from agox.databases.database import Database
from agox.observer import Observer

from .database_utilities import *


class ConcurrentDatabase(Database):
    """
    A database that can be used to store information from multiple concurrent instances of AGOX.
    """

    init_statements = [
        """create table structures (
    id integer primary key autoincrement,
    ctime real,
    positions blob,
    energy real,
    type blob,
    cell blob,
    forces blob, 
    pbc blob,
    template_indices blob,
    iteration int,
    worker_number int
    )""",
        """CREATE TABLE text_key_values (
    key TEXT,
    value TEXT,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
        """CREATE TABLE float_key_values (
    key TEXT,
    value REAL,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
        """CREATE TABLE int_key_values (
    key TEXT,
    value INTEGER,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
        """CREATE TABLE boolean_key_values (
    key TEXT,
    value INTEGER,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
        """CREATE TABLE other_key_values (
    key TEXT,
    value BLOB,
    id INTEGER,
    FOREIGN KEY (id) REFERENCES systems(id))""",
    ]

    # Pack: Positions, energy, type, cell, forces, pbc, template_indices, iteration, worker_number
    # Unpack: ID, time, -//-
    pack_functions = [blob, nothing, blob, blob, blob, blob, blob, nothing, nothing]
    unpack_functions = [nothing, nothing, deblob, nothing, deblob, deblob, deblob, deblob, deblob, nothing, nothing]

    def __init__(
        self,
        worker_number=0,
        total_workers=1,
        sleep_timing=1,
        sync_frequency=50,
        sync_order=None,
        synchronous=True,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.storage_keys.append("worker_number")
        self.worker_number = worker_number
        self.total_workers = total_workers
        self.sync_frequency = sync_frequency
        self.synchronous = synchronous
        self.sleep_timing = sleep_timing

        self.filename_ready = self.filename[:-3] + "_WORKER{}_READY{}"
        self.filename_done = self.filename[:-3] + "_WORKER{}_DONE{}"

        if sync_order is None:
            self.sync_order = self.order[0] + 0.1
        else:
            self.sync_order = sync_order

        # self.add_observer_method(self.sync_database, gets={}, sets={}, order=self.sync_order)

        self._initialize()

    def _init_storage(self):
        super()._init_storage()

    def store_information(self, candidate):
        super().store_information(candidate=candidate)
        self.storage_dict["worker_number"].append(self.worker_number)

    def store_candidate(self, candidate, accepted=True, write=True):
        candidate.add_meta_information("worker_number", self.worker_number)
        candidate.add_meta_information("iteration", self.get_iteration_counter())
        super().store_candidate(candidate, accepted=accepted, write=write)

    def db_to_candidate(self, structure, meta_dict=None):
        candidate = super().db_to_candidate(structure, meta_dict=meta_dict)
        candidate.add_meta_information("worker_number", structure["worker_number"])
        candidate.add_meta_information("iteration", structure["iteration"])
        candidate.add_meta_information("id", structure["id"])

        return candidate

    @Observer.observer_method
    def store_in_database(self, state):
        evaluated_candidates = state.get_from_cache(self, self.get_key)
        anything_accepted = False
        for j, candidate in enumerate(evaluated_candidates):
            if candidate:
                self.writer(
                    "Energy {:06d}: {}".format(self.get_iteration_counter(), candidate.get_potential_energy()),
                )
                self.store_candidate(candidate, accepted=True, write=True)
                anything_accepted = True

            elif candidate is None:
                dummy_candidate = self.candidate_instanstiator(template=Atoms())
                dummy_candidate.set_calculator(SinglePointCalculator(dummy_candidate, energy=float("nan")))
                self.store_candidate(candidate, accepted=False, write=True)

        # This is the difference compared to the base-class method.
        self.sync_database()

        if anything_accepted:
            self.dispatch_to_observers(database=self, state=state)

    def sync_database(self):
        if self.decide_to_sync():
            if self.synchronous:
                self.synchronous_update()
            else:
                self.asynchronous_update()

    def synchronous_update(self):
        # write file
        iteration = self.get_iteration_counter()
        with open(self.filename_ready.format(self.worker_number, iteration), mode="w"):
            pass

        self.writer("Attempting to sync database")
        # Make sure the database contains all the expected information from all workers.
        state = self.check_status()
        print_string = ""
        while not state:
            sleep(self.sleep_timing)
            state = self.check_status()
            print_string += "."
        if len(print_string) > 0:
            self.writer(print_string)

        # Restore the database to memory.
        # This will change the order of candidates in the Database, so be careful if another module relies on that!
        self.restore_to_memory()
        self.writer("Succesfully synced database")

        # write success file
        with open(self.filename_done.format(self.worker_number, iteration), mode="w"):
            pass

        if self.worker_number == 0:  # i.e. i'm the master!
            state = self.cleanup()
            while not state:
                sleep(self.sleep_timing)
                state = self.cleanup()

        self.writer("Number of candidates synced from database {}".format(len(self)))

    def asynchronous_update(self):
        self.writer("Before asynchronous update: {}".format(len(self)))
        self.restore_to_memory()
        self.writer("After asynchronous update: {}".format(len(self)))

    def check_status(self):
        expected_iteration = self.get_iteration_counter()
        state = True
        for i in range(self.total_workers):
            if not os.path.exists(self.filename_ready.format(i, expected_iteration)):
                state = False

        return state

    def cleanup(self):
        expected_iteration = self.get_iteration_counter()
        state = True
        for i in range(self.total_workers):
            if not os.path.exists(self.filename_done.format(i, expected_iteration)):
                state = False
        if state:
            for i in range(self.total_workers):
                os.remove(self.filename_ready.format(i, expected_iteration))
                os.remove(self.filename_done.format(i, expected_iteration))
        return state

    def decide_to_sync(self):
        return self.get_iteration_counter() % self.sync_frequency == 0

    def get_all_candidates(self, respect_worker_number=False):
        if respect_worker_number:
            all_candidates = []
            for candidate in self.candidates:
                if candidate.get_meta_information("worker_number") == self.worker_number:
                    all_candidates.append(candidate)
            return all_candidates
        else:
            return super().get_all_candidates()
