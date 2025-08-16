import numpy as np
from ase.constraints import FixedLine, FixedPlane
from ase.md.langevin import Langevin
from ase.md.velocitydistribution import MaxwellBoltzmannDistribution, Stationary, ZeroRotation
from ase.units import fs

from agox.generators.ABC_generator import GeneratorBaseClass


class MDgenerator(GeneratorBaseClass):
    """
    Does a molecular dynamics simulation on the candidate structure to propose a new candidate.

    Parameters:
    -----------
    calculator : ASE calculator
        Calculator for the MD simulation.
    thermostat : ASE thermostat
        MD program used.
    thermostat_kwargs : dict
        Settings for MD program.
    start_settings : list
        List of start settings for the MD simulation.
    start_settings_kwargs : list
        List of dictionaries with settings for start settings.
    temperature_program : list
        List of tuples with temperature and steps for MD program if temperature is modifiable during simulation.
    set_start_settings : bool
        Whether to set start settings or not.
    constraints : list
        Constraints besides fixed template and 1D/2D constraints.
    check_template : bool
        Check if template atoms moved during MD simulation.
    """

    name = "MDgenerator"

    def __init__(
        self,
        calculator,
        thermostat=Langevin,
        thermostat_kwargs={"timestep": 1.0 * fs, "temperature_K": 10, "friction": 0.05},
        start_settings=[MaxwellBoltzmannDistribution, ZeroRotation, Stationary],
        start_settings_kwargs=[{"temperature_K": 100}, {}, {}],
        temperature_program=[(500, 10), (100, 10)],
        set_start_settings=False,
        constraints=[],
        check_template=False,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.calculator = calculator  # Calculator for MD simulation
        self.thermostat = thermostat  # MD program used
        self.thermostat_kwargs = thermostat_kwargs  # Settings for MD program
        self.set_start_settings = set_start_settings
        self.start_settings = start_settings
        self.start_settings_kwargs = start_settings_kwargs
        self.temperature_program = (
            temperature_program  # (temp in kelvin, steps) for MD program if temperature is modifiable during simulation
        )
        self.constraints = constraints  # Constraints besides fixed template and 1D/2D constraints

        self.check_template = check_template  # Check if template atoms moved during MD simulation

    def _get_candidates(self, candidate, parents, environment):
        candidate.set_calculator(self.calculator)

        self.remove_constraints(
            candidate
        )  # All constraints are removed from candidate before applying self.constraints to ensure only constraints set by user are present during MD simulation
        self.apply_constraints(candidate)
        self.molecular_dynamics(candidate)
        self.remove_constraints(
            candidate
        )  # All constraints are removed after MD simulation to not interfere with other AGOX modules

        candidate.add_meta_information("description", self.name)

        return [candidate]

    def molecular_dynamics(self, candidate):
        """Runs the molecular dynamics simulation and applies/removes constraints accordingly"""

        if self.set_start_settings:
            for setting, kwargs in zip(self.start_settings, self.start_settings_kwargs):
                setting(candidate, **kwargs)

        temperature_program = []
        for temp, steps in self.temperature_program:
            t = np.random.normal(temp, 0.1 * temp)
            temperature_program.append((t, steps))

        dyn = self.thermostat(candidate, **self.thermostat_kwargs)

        if self.check_template:
            positions_before = candidate.template.positions

        for temp, steps in temperature_program:
            dyn.set_temperature(temperature_K=temp)
            dyn.run(steps)

        if self.check_template:
            positions_after = candidate.template.positions

            if np.array_equal(positions_before, positions_after):
                self.writer("Template positions were not altered by MD simulation")
                # print('Template positions were not altered by MD simulation')
            else:
                self.writer("Template positions were altered by MD simulation")
                # print('Template positions were altered by MD simulation')

    def apply_constraints(self, candidate):
        """Applies constraints manually set and based on dimensionality of confinement cell"""

        constraints = self.constraints  # Add any passed constraints immediately
        dimensionality = self.get_dimensionality()
        if dimensionality == 1 or dimensionality == 2:  # Ensures movement within 1D or 2D confinement cell
            constraints.append(self.get_dimensionality_constraints(candidate))

        candidate.set_constraint(constraints)

    def get_dimensionality_constraints(self, candidate):
        """Depending on the dimensionality this either sets fixed line or fixed plane.
        Similar to how rattle needs dimensionality specified to match with confinement cell
        """

        template = candidate.get_template()
        n_template = len(template)
        n_total = len(candidate)
        dimensionality = self.get_dimensionality()
        if dimensionality == 1:
            return FixedLine(
                indices=np.arange(n_template, n_total), direction=[1, 0, 0]
            )  # Generator assumes 1D search happens in X direction
        if dimensionality == 2:
            return FixedPlane(
                indices=np.arange(n_template, n_total), direction=[0, 0, 1]
            )  # Generator assumes 2D search happens in XY-plane

    def remove_constraints(self, candidate):
        """Removes all constraints from candidate"""

        candidate.set_constraint([])

    def get_number_of_parents(self, sampler):
        return 1
