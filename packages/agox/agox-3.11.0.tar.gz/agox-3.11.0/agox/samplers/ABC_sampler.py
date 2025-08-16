from abc import ABC, abstractmethod  # noqa: N999

import numpy as np

from agox.candidates.ABC_candidate import CandidateBaseClass
from agox.databases import Database
from agox.observer import Observer


class SamplerBaseClass(ABC, Observer):
    """
    Base class for samplers.

    Parameters
    ----------
    database : database object
        An instance of an AGOX database class which the sampler will attach to,
        and retrieve candidates from.
    filters : agox.utils.filters.FilterBaseClass
        Filter object that will be used to filter candidates from the database.
    sets : dict
        Dictionary with the sets that the sampler will observe.
    gets : dict
        Dictionary with the gets that the sampler will observe.
    order : int
        Order of the observer.
    """

    def __init__(
        self,
        database: Database | None = None,
        filters: list | None = None,
        sets: dict[str, str] | None = None,
        gets: dict[str, str] | None = None,
        order: int | float = 1,
        use_transfer_data: bool = True,
        surname: str | None = None,
        **kwargs,
    ):            
        Observer.__init__(self, sets=sets, gets=gets, order=order, surname=surname, **kwargs)
        self.sample = []
        self.use_transfer_data = use_transfer_data
        self.transfer_data = []
        self.filters = filters

        self.add_observer_method(
            self.setup_sampler, sets=self.sets[0], gets=self.gets[0], order=self.order[0], handler_identifier="database"
        )

        if database is not None:
            self.attach_to_database(database)

    ########################################################################################
    # Required properties
    ########################################################################################

    @property
    @abstractmethod
    def name(self):  # pragma: no cover
        return NotImplementedError

    @property
    def initialized(self):
        """
        Property that returns True if the sampler has been initialized, such
        that it is able to return a sample member.

        Can be overwritten if the sampler has a different way of checking if
        it is initialized.
        """
        return len(self) > 0

    ########################################################################################
    # Required methods
    ########################################################################################

    @abstractmethod
    def setup(self, all_candidates):  # pragma: no cover
        """

        Function that does the setup for the Sampler, e.g. filters candidates
        from the database or calculates probabilities.

        Must set self.sample.

        Parameters
        ----------
        all_candidates : list
            List of all candidates that will be considered by the sampler. If
            'setup_sampler' is not overwritten this will be all candidates
            currently in the database during in an AGOX run.
        """
        return None

    ########################################################################################
    # Default methods
    ########################################################################################

    @Observer.observer_method
    def setup_sampler(self, database, state):
        """
        Observer function that is attached to the database. The database passes
        itself and the state.

        The state is not passed to the 'self.setup' function that is called, so
        if any data on there is required it can be set as an attribute, e.g.
            self.something = state.get(...)
        or (probably preferably) the this function can be overwritten and more
        things can be parsed to sampler.setup().

        Parameters
        ----------
        database : database object.
            An instance of an AGOX database class.
        state : state object
            An instance of the AGOX State object.

        Returns
        -------
        state object
            The state object with any changes the sampler has made.
        """
        database_data = database.get_all_candidates()
        if self.filters is not None:
            database_data, indices = self.filters(database_data)

        all_candidates = database_data + self.transfer_data

        if self.do_check():
            self.setup(all_candidates)

    def get_parents(self, number_of_parents=1, replace=True):
        """
        Method that returns a list of parents for the generator.

        Parameters
        ----------
        number_of_parents : int
            Number of parents to return
        replace : bool
            If the parents should be sampled with replacement or not.

        Returns
        -------
        list
            List of parents.
        """
        if len(self.sample) == 0:
            return []
        elif len(self.sample) == number_of_parents:
            return self.get_all_members()

        indices = np.random.choice(len(self.sample), size=number_of_parents, replace=replace)
        parents = []
        for index in indices:
            member = self.sample[index].copy()
            self.sample[index].copy_calculator_to(member)
            parents.append(member)
        return parents

    def get_all_members(self):
        members = []
        for i, member in enumerate(self.sample):
            if member is not None:
                member = member.copy()
                self.sample[i].copy_calculator_to(member)
            members.append(member)
        return members

    def add_transfer_data(self, data):
        """
        Add structures to be considered by the Sampler, such that these structures
        are passed to 'self.setup' when it is called.

        The added structures need a few things:
        1. To be Candidate objects.
        2. To have a energies.

        Feature-update: Should check that the data matches a given environment.

        Parameters
        ----------
        data : list
            List of candidate or atoms objects to be considered by the sampler
        """
        correct_type = np.array([isinstance(dat, CandidateBaseClass) for dat in data]).all()
        if not correct_type:
            raise TypeError(
                """Only candidate objects can be specified as transfer data, you probably gave ASE Atoms objects."""
            )
        self.transfer_data = data

    def set_sample(self, data):
        """
        Sets the sample to the given list of candidates, can be used to
        initialize the sample to something specific - e.g. for basin-hopping
        with the MetropolisSampler.
        When using other samplers (such as KMeansSampler) these may be
        overwritten and not considered when making the next sample - if that is
        not the wanted behaviour then use 'add_transfer_data' instead/aswell.

        The added structures need a few things:
        1. To be Candidate objects.
        2. To have a energies.

        Parameters
        ----------
        data : list
            List of candidate objects.
        """
        correct_type = np.array([isinstance(dat, CandidateBaseClass) for dat in data]).all()
        if not correct_type:
            raise TypeError(
                """Only candidate objects can be specified as transfer data, you probably gave ASE Atoms objects."""
            )
        self.sample = data

    def __len__(self):
        return len(self.sample)

    def attach_to_database(self, database):
        from agox.databases.ABC_database import DatabaseBaseClass

        assert isinstance(database, DatabaseBaseClass)
        print(f"{self.name}: Attaching to database: {database}")
        self.attach(database)
