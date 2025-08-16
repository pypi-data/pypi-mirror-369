import numpy as np
from scipy.optimize import minimize

from agox.generators.ABC_generator import GeneratorBaseClass


class ComplementaryEnergyGenerator(GeneratorBaseClass):
    """
    Use complementary energy landscape to generate new candidates.

    Parameters
    ------------
    calc: CE calculator
        Used to evaluate the CE energy and forces
    descriptor: Local descriptor
        Used to calculate local descriptor for atoms in structures
    attractor_method: Method for picking attractors
        Used to construct attractors in CE expression
    move_all: Bool
        Whether to move all non-template atoms or not. If "mover_indices"
        is not None, the atoms with the corresponding indices will be free
        to move, thereby ignoring the "move_all" argument.
    mover_indices: List of integers
        Only atoms with the corresponding indices can move during
        candidate generation.
    """

    name = "ComplementaryEnergyGenerator"

    def __init__(
        self, calculator, descriptor, attractor_method, move_all=True, mover_indices=None, replace=True, **kwargs
    ):
        super().__init__(replace=replace, **kwargs)
        self.calc = calculator
        self.descriptor = descriptor
        self.attractor_method = attractor_method
        self.move_all = move_all
        self.mover_indices = mover_indices

    def _get_candidates(self, candidate, parents, environment):
        template = candidate.get_template()
        n_template = len(template)

        # Set attractors
        attractors = self.attractor_method.get_attractors(candidate)
        self.calc.attractors = attractors

        # Determine which atoms to move if no indices has been supplied
        # Picks those with highest local complementary energy
        if self.mover_indices is None:
            if self.move_all:
                mover_indices = range(n_template, len(candidate))
            else:
                n_movers = np.random.randint(1, len(candidate) - n_template)
                mover_indices = np.array(range(n_template, len(candidate)))
                self.calc.mover_indices = mover_indices
                local_ce = self.calc.get_local_ce_energy(candidate)
                largest_local_ce_indices = np.argsort(local_ce)[::-1]
                mover_indices = mover_indices[largest_local_ce_indices][:n_movers]

            self.mover_indices = mover_indices

        # Set mover indices and attractors for calculator
        self.calc.mover_indices = self.mover_indices

        # Set calculator
        candidate.calc = self.calc

        def objective_func(pos):
            candidate.positions[self.mover_indices] = np.reshape(pos, [len(self.mover_indices), 3])
            ce = candidate.get_potential_energy(apply_constraint=0)
            grad = -candidate.get_forces(apply_constraint=0)[self.mover_indices]
            return ce, grad.flatten()

        pos = candidate.positions[self.mover_indices].flatten()
        pos = minimize(objective_func, pos, method="BFGS", jac=True, options={"maxiter": 75, "disp": False}).x
        suggested_positions = np.reshape(pos, [len(self.mover_indices), 3])

        for index in range(len(self.mover_indices)):
            i = self.mover_indices[index]
            for _ in range(100):
                if _ == 0:
                    radius = 0
                else:
                    radius = 0.5 * np.random.rand() ** (1 / self.get_dimensionality())
                displacement = self.get_displacement_vector(radius)
                suggested_position = suggested_positions[index] + displacement

                # Check confinement limits:
                if not self.check_confinement(suggested_position):
                    continue

                # Check that suggested_position is not too close/far to/from other atoms
                # Skips the atom it self.
                if self.check_new_position(candidate, suggested_position, candidate[i].number, skipped_indices=[i]):
                    candidate[i].position = suggested_position
                    break

        return [candidate]

    @classmethod
    def default(
        cls,
        environment,
        database,
        move_all=True,
        mover_indices=None,
        attractors_from_template=False,
        predefined_attractors=None,
        **kwargs,
    ):
        from agox.generators.complementary_energy.attractor_methods.ce_attractors_current_structure import (
            AttractorCurrentStructure,
        )
        from agox.generators.complementary_energy.ce_calculators import ComplementaryEnergyDistanceCalculator
        from agox.models.descriptors.exponential_density import ExponentialDensity

        lambs = [0.5, 1, 1.5]
        rc = 10.0
        descriptor = ExponentialDensity(environment=environment, lambs=lambs, rc=rc)
        ce_calc = ComplementaryEnergyDistanceCalculator(descriptor=descriptor)
        ce_attractors = AttractorCurrentStructure(
            descriptor=descriptor,
            attractors_from_template=attractors_from_template,
            predefined_attractors=predefined_attractors,
        )
        ce_attractors.attach(database)

        return cls(
            calculator=ce_calc,
            descriptor=descriptor,
            attractor_method=ce_attractors,
            move_all=move_all,
            **environment.get_confinement(),
        )

    def get_number_of_parents(self, sampler):
        return 1
