import os
from abc import ABC, abstractmethod
from typing import Any, Callable, Optional

import numpy as np
from ase import Atoms
from ase.calculators.calculator import Calculator, all_changes

from agox.candidates.ABC_candidate import CandidateBaseClass
from agox.databases import Database
from agox.main import State
from agox.observer import Observer, ObserverHandler
from agox.utils.filters import FilterBaseClass


class ModelBaseClass(Calculator, ObserverHandler, Observer, ABC):
    """Model Base Class implementation

    Parameters
    ----------
    database : AGOX Database obj
        If used for on-the-fly training on a database, this should be set
    iteration_start_training : int
        When model is attached as observer it starts training after this number of
        iterations.
    update_period : int
        When model is attached as observer it updates every update_period
        iterations.
    record : set
        Training record.

    """

    def __init__(
        self,
        database: Optional[Database] = None,
        filter: FilterBaseClass = None, # noqa
        order: float = 0,
        iteration_start_training: int = 0,
        update_period: int = 1,
        surname: str = "",
        gets: dict[str, str] | None = None,
        sets: dict[str, str] | None = None,
        **kwargs,
    ) -> None:
        """
        Parameters
        ----------
        database : AGOX Database obj
            If used for on-the-fly training on a database, this should be set
        filter : FilterBaseClass
            Filter object to use for filtering data
        order : float
            Order of observer
        iteration_start_training : int
            When model is attached as observer it starts training after this number of
            iterations.
        update_period : int
            When model is attached as observer it updates every update_period
            iterations.
        surname : str
            Surname of observer
        gets : dict
            Gets dictionary
        sets : dict
            Sets dictionary    
        """
        Observer.__init__(self, order=order, surname=surname, gets=gets, sets=sets, **kwargs)
        ObserverHandler.__init__(self, handler_identifier="model", dispatch_method=self.training_observer)
        Calculator.__init__(self)

        self.filter = filter
        self._save_attributes = ["_ready_state"]
        self.iteration_start_training = iteration_start_training
        self.update_period = update_period

        self.validation_data = []
        self._ready_state = False
        self._record = set()
        self.update = False

        self.add_observer_method(
            self.training_observer,
            gets=self.gets[0],
            sets=self.sets[0],
            order=self.order[0],
            handler_identifier="database",
        )

        if database is not None:
            self.attach_to_database(database)

    @property
    @abstractmethod
    def name(self) -> None:  # pragma: no cover
        """str: Name of model. Must be implemented in child class."""
        ...

    @property
    @abstractmethod
    def implemented_properties(self) -> None:  # pragma: no cover
        """:obj: `list` of :obj: `str`: Implemented properties.
        Available properties are: 'energy', 'forces', 'uncertainty'

        Must be implemented in child class.
        """
        ...

    @abstractmethod
    def predict_energy(self, atoms: Atoms, **kwargs) -> None:  # pragma: no cover
        """Method for energy prediction.

        Note
        ----------
        Always include **kwargs when implementing this function.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        float
            The energy prediction

        Must be implemented in child class.
        """
        pass

    @abstractmethod
    def train(self, training_data: list[Atoms], **kwargs) -> None:  # pragma: no cover
        """Method for model training.

        Note
        ----------
        Always include **kwargs when implementing this function.
        If your model is not trainable just write a method that does nothing

        Parameters
        ----------
        atoms : :obj: `list` of :obj: `ASE Atoms`
            List of ASE atoms objects or AGOX candidate objects to use as training data.
            All atoms must have a calculator with energy and other nesseary properties set, such that
            it can be accessed by .get_* methods on the atoms.


        Must be implemented in child class.

        """
        pass

    @property
    def ready_state(self) -> None:
        """bool: True if model has been trained otherwise False."""
        return self._ready_state

    @ready_state.setter
    def ready_state(self, state: bool) -> None:
        self._ready_state = bool(state)

    def add_save_attributes(self, attribute: str | list[str]) -> None:
        """Add attribute to save list.

        Parameters
        ----------
        attribute : str or list of str
            Name of attribute to add to save list.

        """
        if isinstance(attribute, str):
            self._save_attributes.append(attribute)
        else:
            self._save_attributes += attribute

    def remove_save_attributes(self, attribute: str | list[str]) -> None:
        """Remove attribute from save list.

        Parameters
        ----------
        attribute : str or list of str
            Name of attribute to remove from save list.

        """
        if isinstance(attribute, str):
            self._save_attributes.remove(attribute)
        else:
            for a in attribute:
                self._save_attributes.remove(a)

    def reset_save_attributes(self) -> None:
        """Reset save list."""
        self._save_attributes = []

    @Observer.observer_method
    def training_observer(self, database: Database, state: State) -> None:
        """Observer method for use with on-the-fly training based data in an AGOX database.

        Note
        ----------
        This implementation simply calls the train_model method with all data in the database

        Parameters
        ----------
        atoms : AGOX Database object
            The database to keep the model trained against

        Returns
        ----------
        None

        """
        iteration = self.get_iteration_counter()

        if iteration < self.iteration_start_training:
            return
        if iteration % self.update_period != 0 and iteration != self.iteration_start_training:
            return

        data = database.get_all_candidates()
        self.train(data)
        self.dispatch_to_observers(model=self, state=state)

    def add_validation_data(self, data: list[Atoms]) -> None:
        """Add validation data to model.

        Parameters
        ----------
        data : :obj: `list` of :obj: `ASE Atoms`
            List of ASE atoms objects or AGOX candidate objects to use as validation data.
            All atoms must have a calculator with energy and other nesseary properties set, such that
            it can be accessed by .get_* methods on the atoms.

        """
        if isinstance(data, list):
            self.validation_data += data
        else:
            self.validation_data.append(data)

    def predict_forces(self, atoms: Atoms, **kwargs) -> np.ndarray:
        """Method for forces prediction.

        The default numerical central difference force calculation method is used, but
        this can be overwritten with an analytical calculation of the force.

        Note
        ----------
        Always include **kwargs when implementing this function.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        np.array
            The force prediction with shape (N,3), where N is len(atoms)

        """
        return self.predict_forces_central(atoms, **kwargs)

    def predict_forces_central(self, atoms: Atoms, acquisition_function: Optional[Callable] = None, d: float=0.001, **kwargs) -> np.ndarray:
        """Numerical cenral difference forces prediction.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.
        acquisition_function : Acquisition function or None
            Function that takes evaluate acquisition function based on
            energy and uncertainty prediction. Used for relaxation in acquisition
            funtion if force uncertainties are not available.

        Returns
        ----------
        np.array
            The force prediction with shape (N,3), where N is len(atoms)

        """
        if acquisition_function is None:
            energy = lambda a: self.predict_energy(a) # noqa
        else:
            energy = lambda a: acquisition_function(*self.predict_energy_and_uncertainty(a)) # noqa

        e0 = energy(atoms)  # self.predict_energy(atoms)
        energies = []

        for a in range(len(atoms)):
            for i in range(3):
                new_pos = atoms.get_positions()  # Try forward energy
                new_pos[a, i] += d
                atoms.set_positions(new_pos)
                if atoms.positions[a, i] != new_pos[a, i]:  # Check for constraints
                    energies.append(e0)
                else:
                    energies.append(energy(atoms))
                    atoms.positions[a, i] -= d

                new_pos = atoms.get_positions()  # Try backwards energy
                new_pos[a, i] -= d
                atoms.set_positions(new_pos)
                if atoms.positions[a, i] != new_pos[a, i]:
                    energies.append(e0)
                else:
                    energies.append(energy(atoms))
                    atoms.positions[a, i] += d

        penergies = np.array(energies[0::2])  # forward energies
        menergies = np.array(energies[1::2])  # backward energies

        forces = ((menergies - penergies) / (2 * d)).reshape(len(atoms), 3)
        return forces

    def predict_uncertainty(self, atoms: Atoms, **kwargs) -> float:
        """Method for energy uncertainty prediction.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        float
            The energy uncertainty prediction

        """
        return 0

    def predict_uncertainty_forces(self, atoms: Atoms, **kwargs) -> np.ndarray:
        """Method for energy uncertainty prediction.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        np.array
            The force uncertainty prediction with shape (N,3) with N=len(atoms)

        """
        return np.zeros((len(atoms), 3))

    def predict_energy_and_uncertainty(self, atoms: Atoms, **kwargs) -> tuple[float, float]:
        """Method for energy and energy uncertainty prediction.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        float, float
            The energy and energy uncertainty prediction

        """
        return self.predict_energy(atoms, **kwargs), self.predict_uncertainty(atoms, **kwargs)

    def predict_forces_and_uncertainty(self, atoms: Atoms, **kwargs) -> tuple[np.ndarray, np.ndarray]:
        """Method for energy and energy uncertainty prediction.

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        np.array, np.array
            Forces and forces uncertainty. Both with shape (N, 3) with N=len(atoms).

        """
        return self.predict_forces(atoms, **kwargs), self.predict_forces_uncertainty(atoms, **kwargs)

    def converter(self, atoms: Atoms, **kwargs) -> dict:
        """Converts an ASE atoms object to a format that can be used by the model

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for which to predict the energy.

        Returns
        ----------
        object
            The converted object

        """
        return {}

    def calculate(self, atoms: Atoms = None, properties: list[str]=["energy"], system_changes: list[str] = all_changes) -> None:
        """ASE Calculator calculate method

        Parameters
        ----------
        atoms : ASE Atoms obj or AGOX Candidate object
            The atoms object for to predict properties of.
        properties : :obj: `list` of :obj: `str`
            List of properties to calculate for the atoms
        system_changes : ASE system_changes
            Which ASE system_changes to check for before calculation

        Returns
        ----------
        None
        """
        Calculator.calculate(self, atoms, properties, system_changes)

        energy = self.predict_energy(self.atoms)
        self.results["energy"] = energy

        if "forces" in properties:
            forces = self.predict_forces(self.atoms)
            self.results["forces"] = forces

    def validate(self, **kwargs) -> dict:
        """Method for validating the model.

        Parameters
        ----------
        kwargs : dict
            Keyword arguments to pass to the validation method.

        Returns
        ----------
        dict
            Dictionary with validation results

        """
        if len(self.validation_data) == 0:
            return None

        e_true = []
        e_pred = []
        for d in self.validation_data:
            e_true.append(d.get_potential_energy())
            e_pred.append(self.predict_energy(d))

        e_true = np.array(e_true)
        e_pred = np.array(e_pred)

        return {
            "Energy MAE [eV]": np.mean(np.abs(e_true - e_pred)),
            "Energy RMSE [eV]": np.sqrt(np.mean((e_true - e_pred) ** 2)),
            "Max absolute energy error [eV]": np.max(np.abs(e_true - e_pred)),
            "Max relative energy error [%]": np.max((e_true - e_pred) / e_true) * 100,
            "Min relative energy error [%]": np.min((e_true - e_pred) / e_true) * 100,
        }

    def _training_record(self, data: list[Atoms]) -> None:
        """
        Record the training data.

        Parameters
        ----------
        data : list
            List of Atoms objects.

        """
        if not all([isinstance(d, CandidateBaseClass) for d in data]):
            return

        for d in data:
            self._record.add(d.cache_key)

        self.update = True

    def _get_new_data(self, data: list[Atoms]) -> tuple[list, list]:
        """
        Get the new data.

        Parameters
        ----------
        data : list
            List of Atoms objects.

        Returns
        -------
        list
            List of new Atoms objects.

        list
            List of old Atoms objects.

        """
        if not all([isinstance(d, CandidateBaseClass) for d in data]):
            return data, []

        new_data = []
        old_data = []
        for d in data:
            if d.cache_key in self._record:
                old_data.append(d)
            else:
                new_data.append(d)
        return new_data, old_data

    def print_model_info(self, validation: dict[str, Any] = None, **kwargs) -> None:
        """Prints model information

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments to pass to the model

        Returns
        ----------
        None
        """
        model_info = self.model_info(**kwargs)
        if validation is not None:
            model_info.append("------ Validation Info ------")
            model_info.append("Validation data size: {}".format(len(self.validation_data)))
            for key, val in validation.items():
                model_info.append("{}: {:.3}".format(key, val))

        for s in model_info:
            self.writer(s)

    def model_info(self, **kwargs) -> list[str]:
        """Returns model information

        Parameters
        ----------
        **kwargs : dict
            Keyword arguments to pass to the model

        Returns
        ----------
        list of str
            The model information
        """
        return ["No model information available."]

    def save(self, path: str = "model.h5") -> None:
        """
        Save the model as a pickled object.

        Parameters
        ----------
        path : str, optional
            Path to save the model to. The default is 'model.h5'.
        """
        import h5py

        with h5py.File(path, "w") as f:
            for key in self._save_attributes:
                obj = self
                for k in key.split("."):
                    data = getattr(obj, k)
                    obj = data
                if data is not None:
                    f.create_dataset(key, data=data)

        self.writer("Saving model to {}".format(path))

    def load(self, path: str) -> None:
        """
        Load a pickle

        Parameters
        ----------
        path : str
            Path to a saved model.

        Returns
        -------
        model-object
            The loaded model object.
        """
        assert os.path.exists(path), "Path does not exist"
        import h5py

        self.writer("Loading model from {}".format(path))
        with h5py.File(path, "r") as f:
            for key in self._save_attributes:
                obj = self
                for k in key.split(".")[:-1]:
                    obj = getattr(obj, k)

                k = key.split(".")[-1]

                if key in f:
                    value = f[key][()]
                    setattr(obj, k, value)

        self.writer("Model loaded")

    def attach_to_database(self, database: Database) -> None:
        from agox.databases.ABC_database import DatabaseBaseClass

        assert isinstance(database, DatabaseBaseClass)
        print(f"{self.name}: Attaching to database: {database}")
        self.attach(database)
