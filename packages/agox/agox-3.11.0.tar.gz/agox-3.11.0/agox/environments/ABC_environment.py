from abc import ABC, abstractmethod  # noqa: N999

from agox.utils.constraints import BoxConstraint, ConstraintManager
import numpy as np
from ase.constraints import FixAtoms

from agox.candidates import StandardCandidate
from agox.helpers.confinement import Confinement
from agox.module import Module
from agox.utils.constraints.box_constraint import BoxConstraint



class EnvironmentBaseClass(ABC, Module):
    """
    Base class for all environments.

    Environments are used to define the environment in which the candidates are
    generated. This includes confinement, constraints, and other settings.

    Parameters
    ----------
    confinement_cell : np.ndarray, optional
        The cell of the confinement, by default None.
    confinement_corner : np.ndarray, optional
        The corner of the confinement, by default None.
    constraints : list, optional
        List of constraints, by default [].
    use_box_constraint : bool, optional
        If True, a box constraint is used, by default True.
    box_constraint_pbc : list, optional
        List of booleans, by default [False]*3.
    fix_template : bool, optional
        If True, the template is fixed, by default True.
    """

    name = "Environment"

    def __init__(
        self,
        confinement_cell: np.ndarray = None,
        confinement_corner: np.ndarray =None,
        constraints: list | None = None,
        use_box_constraint: bool = True,
        box_constraint_pbc: list[bool, bool, bool] | None = None,
        fix_template: bool = True,
        surname: str | None = None,
        **kwargs,
    ) -> None:
        Module.__init__(self, surname=surname, **kwargs)

        self.confinement_cell = confinement_cell
        self.confinement_corner = confinement_corner
        self.constraints = constraints if constraints is not None else []
        self.use_box_constraint = use_box_constraint
        self.box_constraint_pbc = box_constraint_pbc if box_constraint_pbc is not None else [False] * 3
        self.fix_template = fix_template
        self.constraints = []

    @abstractmethod
    def get_template(self, **kwargs):  # pragma: no cover
        pass

    @abstractmethod
    def get_numbers(self, numbers, **kwargs):
        pass

    @abstractmethod
    def environment_report(self):
        pass

    def get_missing_indices(self):
        return np.arange(len(self._template), len(self._template) + len(self._numbers))

    def get_confinement_cell(self, distance_to_edge=3):
        if self.confinement_cell is not None:
            confinement_cell = self.confinement_cell
        elif self._template.pbc.all() is False:
            confinement_cell = self._template.get_cell().copy() - np.eye(3) * distance_to_edge * 2
        else:
            # Find the directions that are not periodic:
            confinement_cell = self._template.get_cell().copy() - np.eye(3) * distance_to_edge * 2
            directions = np.argwhere(self._template.pbc == True)
            for d in directions:
                confinement_cell[d, :] = self._template.get_cell()[d, :]

        return confinement_cell

    def get_confinement_corner(self, distance_to_edge=3):
        if self.confinement_cell is not None:
            confinement_corner = self.confinement_corner
        elif self._template.pbc.all() is False:
            confinement_corner = np.ones(3) * distance_to_edge
        else:
            # Find the directions that are not periodic:
            confinement_corner = np.ones(3) * distance_to_edge
            directions = np.argwhere(self._template.pbc == True)
            for d in directions:
                confinement_corner[d] = 0
        return confinement_corner

    def get_confinement(self, as_dict: bool = True):
        confinement = Confinement(self.confinement_cell, self.confinement_corner)
        if as_dict:
            return {'confinement': confinement}
        return confinement

    def get_box_constraint(self):
        confinement_cell = self.get_confinement_cell()
        confinement_corner = self.get_confinement_corner()
        return BoxConstraint(
            confinement_cell=confinement_cell,
            confinement_corner=confinement_corner,
            indices=self.get_missing_indices(),
            pbc=self.box_constraint_pbc,
        )

    def get_constraints(self):
        manager = ConstraintManager()
        if self.use_box_constraint:
            manager.add_constraint(self.get_box_constraint(), mode="optimize")
        if self.fix_template:
            manager.add_constraint(FixAtoms(indices=[]), mode="template")

        for constraint, mode in self.constraints:
            manager.add_constraint(constraint, mode=mode)
        return manager

    def add_constraint(self, constraint, mode=None):
        self.constraints.append((constraint, mode))

    def convert_to_candidate_object(self, template):
        template = StandardCandidate(
            template=template,
            positions=template.positions,
            numbers=template.numbers,
            cell=template.cell,
            info=template.info,
        )
        return template

    def plot(self, name="environment_plot.png"):
        import matplotlib.pyplot as plt

        from agox.utils.matplotlib_utils import use_agox_mpl_backend
        from agox.utils.plot import plot_atoms, plot_cell

        use_agox_mpl_backend()

        atoms = self.get_template()
        atoms.set_constraint(self.get_constraints())

        fig, axs = plt.subplots(1, 3, figsize=(15, 5))

        for ax, plane in zip(axs, ["xy", "xz", "yz"]):
            plot_atoms(ax, atoms, plane=plane, plot_constraint=True, repeat=True)
            plot_cell(ax, atoms.cell, plane=plane, collection_kwargs=dict(edgecolors="black", linestyles="dotted"))
            plot_cell(
                ax,
                self.confinement_cell,
                plane=plane,
                offset=self.confinement_corner,
                collection_kwargs=dict(edgecolors="red", linestyles="dashed"),
            )

            # Equal aspect ratio
            ax.set_aspect("equal", "box")

        fig.savefig(name, bbox_inches="tight")
        plt.close()
